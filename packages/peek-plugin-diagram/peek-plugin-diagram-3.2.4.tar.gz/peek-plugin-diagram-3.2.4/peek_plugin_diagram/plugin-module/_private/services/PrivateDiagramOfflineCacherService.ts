import { filter, first, takeUntil } from "rxjs/operators";
import { Injectable } from "@angular/core";
import {
    NgLifeCycleEvents,
    TupleSelector,
    VortexStatusService,
} from "@synerty/vortexjs";
import { PrivateDiagramTupleService } from "./PrivateDiagramTupleService";
import { GroupDispsTuple, ModelCoordSet, ModelSet } from "../tuples";
import {
    DispColor,
    DispLayer,
    DispLevel,
    DispLineStyle,
    DispTextStyle,
} from "../../lookups";
import { BranchKeyToIdMapTuple } from "../branch/BranchKeyToIdMapTuple";
import { BranchService } from "@peek/peek_plugin_branch";

/** Diagram Lookups offline cacher
 *
 * This Service is never unloaded, it makes sure that the lookups that the diagram
 * needs are always stored in the local DB.
 *
 * For NS, This is where the embedded web version reads it from.
 *
 */
@Injectable()
export class PrivateDiagramOfflineCacherService extends NgLifeCycleEvents {
    private static readonly LookupTuples = [
        DispLevel,
        DispLayer,
        DispColor,
        DispTextStyle,
        DispLineStyle,
    ];

    private lookupSubs = [];
    private dispGroupSubs = [];

    constructor(
        private tupleService: PrivateDiagramTupleService,
        vortexStatusService: VortexStatusService,
        private globalBranchService: BranchService
    ) {
        super();

        // Delete data older than 7 days
        let date7DaysAgo = new Date(Date.now() - 7 * 24 * 3600 * 1000);

        let promise = null;
        if (vortexStatusService.snapshot.isOnline) {
            promise = this.tupleService.offlineStorage
                .deleteOldTuples(date7DaysAgo)
                .catch((err) =>
                    console.log(`ERROR: Failed to delete old tuples`)
                );
        } else {
            vortexStatusService.isOnline
                .pipe(takeUntil(this.onDestroyEvent))
                .pipe(filter((val) => val === true))
                .pipe(first())
                .subscribe(() => {
                    this.tupleService.offlineStorage
                        .deleteOldTuples(date7DaysAgo)
                        .catch((err) =>
                            console.log(`ERROR: Failed to delete old tuples`)
                        );
                });
            promise = Promise.resolve();
        }

        promise.then(() => {
            this.loadModelSet();
            this.loadModelCoordSet();
            this.loadBranchToIdMap();
        });
    }

    /**
     * Cache Model Set
     *
     * This method caches the model set list for offline use.
     *
     */
    private loadModelSet() {
        let tupleSelector = new TupleSelector(ModelSet.tupleName, {});

        this.tupleService.offlineObserver
            .subscribeToTupleSelector(tupleSelector)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((modelSets: ModelSet[]) => {
                this.tupleService.offlineObserver.flushCache(tupleSelector);
                this.loadLookups(modelSets);

                for (let modelSet of modelSets) {
                    // HACK!!!
                    // force the global branch service to cache it's stuff
                    this.globalBranchService.branches(modelSet.key);
                }
            });
    }

    /**
     * Cache Model Set
     *
     * This method caches the coord sets
     *
     */
    private loadModelCoordSet() {
        let tupleSelector = new TupleSelector(ModelCoordSet.tupleName, {});

        this.tupleService.offlineObserver
            .subscribeToTupleSelector(tupleSelector)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: ModelCoordSet[]) => {
                this.tupleService.offlineObserver.flushCache(tupleSelector);
                this.loadDispGroups(tuples);
            });
    }

    /**
     * Cache Branch KeyToIdMap Tuple
     *
     * This method caches the coord sets
     *
     */
    private loadBranchToIdMap() {
        let tupleSelector = new TupleSelector(
            BranchKeyToIdMapTuple.tupleName,
            {}
        );

        this.tupleService.offlineObserver
            .subscribeToTupleSelector(tupleSelector)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: BranchKeyToIdMapTuple[]) => {
                this.tupleService.offlineObserver.flushCache(tupleSelector);
            });
    }

    /**
     * Cache Lookups
     *
     * This method caches the lookups for a model set
     *
     */
    private loadLookups(modelSets: ModelSet[]) {
        while (this.lookupSubs.length) this.lookupSubs.pop().unsubscribe();

        for (let modelSet of modelSets) {
            for (let LookupTuple of PrivateDiagramOfflineCacherService.LookupTuples) {
                let tupleSelector = new TupleSelector(LookupTuple.tupleName, {
                    modelSetKey: modelSet.key,
                });

                let sub = this.tupleService.offlineObserver
                    .subscribeToTupleSelector(tupleSelector)
                    .pipe(takeUntil(this.onDestroyEvent))
                    .subscribe((tuples: any[]) => {
                        this.tupleService.offlineObserver.flushCache(
                            tupleSelector
                        );
                    });

                this.lookupSubs.push(sub);
            }
        }
    }

    /**
     * Load Disp Groups
     *
     * This method caches the DispGroups for coord sets.
     *
     */
    private loadDispGroups(coordSets: ModelCoordSet[]) {
        let subs = this.dispGroupSubs;

        while (subs.length) subs.pop().unsubscribe();

        for (let coordSet of coordSets) {
            if (coordSet.dispGroupTemplatesEnabled !== true) continue;

            let tupleSelector = new TupleSelector(GroupDispsTuple.tupleName, {
                coordSetId: coordSet.id,
            });

            let sub = this.tupleService.offlineObserver
                .subscribeToTupleSelector(tupleSelector)
                .pipe(takeUntil(this.onDestroyEvent))
                .subscribe((tuples: any[]) => {
                    this.tupleService.offlineObserver.flushCache(tupleSelector);
                });

            subs.push(sub);
        }
    }
}
