import { takeUntil } from "rxjs/operators";
import { Component } from "@angular/core";
import {
    NgLifeCycleEvents,
    TupleDataObserverService,
    TupleSelector,
} from "@synerty/vortexjs";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { DiagramImporterStatusTuple } from "../tuples/DiagramImporterStatusTuple";

@Component({
    selector: "pl-diagram-status",
    templateUrl: "./status.component.html",
})
export class StatusComponent extends NgLifeCycleEvents {
    item: DiagramImporterStatusTuple = new DiagramImporterStatusTuple();

    constructor(
        private balloonMsg: BalloonMsgService,
        private tupleObserver: TupleDataObserverService
    ) {
        super();

        let ts = new TupleSelector(DiagramImporterStatusTuple.tupleName, {});
        this.tupleObserver
            .subscribeToTupleSelector(ts)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe(
                (tuples: DiagramImporterStatusTuple[]) =>
                    (this.item = tuples[0])
            );
    }
}
