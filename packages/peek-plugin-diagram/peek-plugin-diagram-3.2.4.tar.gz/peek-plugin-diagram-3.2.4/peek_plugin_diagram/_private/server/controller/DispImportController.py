import logging
from typing import List

from sqlalchemy.exc import SQLAlchemyError
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.defer import inlineCallbacks

from peek_plugin_base.storage.DbConnection import DbSessionCreator
from peek_plugin_diagram._private.storage.Display import DispBase
from peek_plugin_diagram._private.worker.tasks.ImportDispTask import (
    importDispsTask,
)
from peek_plugin_livedb.server.LiveDBWriteApiABC import LiveDBWriteApiABC

logger = logging.getLogger(__name__)


class DispImportController:
    def __init__(
        self,
        dbSessionCreator: DbSessionCreator,
        liveDbWriteApi: LiveDBWriteApiABC,
    ):
        self._dbSessionCreator = dbSessionCreator
        self._liveDbWriteApi = liveDbWriteApi

    def shutdown(self):
        self._liveDbWriteApi = None

    @inlineCallbacks
    def importDisps(
        self,
        modelSetKey: str,
        coordSetKey: str,
        importGroupHash: str,
        dispsEncodedPayload: bytes,
    ):
        liveDbItemsToImport = yield importDispsTask.delay(
            modelSetKey, coordSetKey, importGroupHash, dispsEncodedPayload
        )

        if liveDbItemsToImport:
            yield self._liveDbWriteApi.importLiveDbItems(
                modelSetKey, liveDbItemsToImport
            )

            # Give and connector plugins time to load the new items
            yield self._sleep(2.0)

            yield self._liveDbWriteApi.pollLiveDbValueAcquisition(
                modelSetKey, [i.key for i in liveDbItemsToImport]
            )

    def _sleep(self, seconds):
        d = Deferred()
        reactor.callLater(seconds, d.callback, True)
        return d

    def getImportGroupHashes(self, prefix: str) -> List[DispBase]:
        ormSession = self._dbSessionCreator()
        query = ormSession.query(DispBase.importGroupHash).distinct(
            DispBase.importGroupHash
        )
        if prefix:
            query = query.filter(DispBase.importGroupHash.like(f"{prefix}%"))

        ret = []

        try:
            for row in query.all():
                ret.append(row.importGroupHash)
            return ret
        finally:
            ormSession.close()

    def removeDispsByImportGroupHash(self, importGroupHash):
        dispTable = DispBase.__table__
        ormSession = self._dbSessionCreator()
        engine = ormSession.get_bind()
        conn = engine.connect()
        transaction = conn.begin()

        try:
            engine.execute(
                dispTable.delete().where(
                    dispTable.c.importGroupHash == importGroupHash
                )
            )
            transaction.commit()
        except SQLAlchemyError:
            transaction.rollback()
            raise
        finally:
            conn.close()
