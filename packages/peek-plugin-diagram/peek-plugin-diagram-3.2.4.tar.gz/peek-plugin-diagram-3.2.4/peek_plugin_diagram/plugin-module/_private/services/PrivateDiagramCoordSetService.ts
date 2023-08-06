import { Observable, Subject } from "rxjs";
import { takeUntil } from "rxjs/operators";
import { Injectable } from "@angular/core";
import { NgLifeCycleEvents, TupleSelector } from "@synerty/vortexjs";
import { ModelCoordSet } from "../tuples/ModelCoordSet";
import { PrivateDiagramTupleService } from "./PrivateDiagramTupleService";
import { DiagramCoordSetService } from "../../DiagramCoordSetService";
import { DiagramCoordSetTuple } from "../../tuples/DiagramCoordSetTuple";

/** CoordSetCache
 *
 * This class is responsible for buffering the coord sets in memory.
 *
 * Typically there will be less than 20 of these.
 *
 */
@Injectable()
export class PrivateDiagramCoordSetService
    extends NgLifeCycleEvents
    implements DiagramCoordSetService
{
    private _coordSetByKeyByModelSetKey: {
        [modekSetKey: string]: { [coordSetKey: string]: ModelCoordSet };
    } = {};
    private _coordSetsByModelSetKey: {
        [modekSetKey: string]: ModelCoordSet[];
    } = {};
    private _coordSetById: { [id: number]: ModelCoordSet } = {};
    private _isReady: boolean = false;
    private _coordSetSubjectByModelSetKey: {
        [key: string]: Subject<DiagramCoordSetTuple[]>;
    } = {};
    private _lastDiagramCoordSetTuplesByModelSetKey: {
        [key: string]: DiagramCoordSetTuple[];
    } = {};

    constructor(private tupleService: PrivateDiagramTupleService) {
        super();

        this.initialLoad();
    }

    shutdown(): void {}

    isReady(): boolean {
        return this._isReady;
    }

    /** Coord Sets
     *
     * Return the coord sets that belong to the modelSetKey
     *
     * @param modelSetKey
     */
    diagramCoordSetTuples(
        modelSetKey: string
    ): Observable<DiagramCoordSetTuple[]> {
        // Create the subject if we need to
        if (this._coordSetSubjectByModelSetKey[modelSetKey] == null) {
            this._coordSetSubjectByModelSetKey[modelSetKey] = new Subject<
                DiagramCoordSetTuple[]
            >();
        }
        let subject = this._coordSetSubjectByModelSetKey[modelSetKey];

        // Notify the observer once they have registered if we already have data
        let lastData =
            this._lastDiagramCoordSetTuplesByModelSetKey[modelSetKey];
        if (lastData != null) setTimeout(() => subject.next(lastData), 10);

        // return the subject.
        return subject;
    }

    coordSetForKey(
        modelSetKey: string,
        coordSetKey: string
    ): ModelCoordSet | null {
        let coordSetsByCoordSetKey =
            this._coordSetByKeyByModelSetKey[modelSetKey];
        if (coordSetsByCoordSetKey == null) return null;

        return coordSetsByCoordSetKey[coordSetKey];
    }

    coordSets(modelSetKey: string): ModelCoordSet[] {
        let coordSets = this._coordSetsByModelSetKey[modelSetKey];
        return coordSets == null ? [] : coordSets;
    }

    coordSetForId(id: number): ModelCoordSet {
        return this._coordSetById[id];
    }

    modelSetKeys(): string[] {
        return Object.keys(this._coordSetsByModelSetKey);
    }

    private initialLoad(): void {
        let ts = new TupleSelector(ModelCoordSet.tupleName, {});

        this.tupleService.offlineObserver
            .subscribeToTupleSelector(ts)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: ModelCoordSet[]) => {
                this._coordSetByKeyByModelSetKey = {};
                this._coordSetsByModelSetKey = {};
                this._coordSetById = {};

                for (let item of tuples) {
                    this._coordSetById[item.id] = item;

                    // Coord Set by Coord Set Key, by Model Set Key
                    let coordSetByCoordSetKey =
                        this._coordSetByKeyByModelSetKey[
                            item.data.modelSetKey
                        ] == null
                            ? (this._coordSetByKeyByModelSetKey[
                                  item.data.modelSetKey
                              ] = {})
                            : this._coordSetByKeyByModelSetKey[
                                  item.data.modelSetKey
                              ];

                    coordSetByCoordSetKey[item.key] = item;

                    // Coord Set array by Model Set Key
                    let coordSets =
                        this._coordSetsByModelSetKey[item.data.modelSetKey] ==
                        null
                            ? (this._coordSetsByModelSetKey[
                                  item.data.modelSetKey
                              ] = [])
                            : this._coordSetsByModelSetKey[
                                  item.data.modelSetKey
                              ];

                    coordSets.push(item);
                }

                this._isReady = tuples.length != 0;
                this.notifyForDiagramCoordSetTuples(tuples);
            });
    }

    private notifyForDiagramCoordSetTuples(tuples: ModelCoordSet[]): void {
        let coordSetsByModelSetKey = {};
        for (let tuple of tuples) {
            if (coordSetsByModelSetKey[tuple.data.modelSetKey] == null)
                coordSetsByModelSetKey[tuple.data.modelSetKey] = [];

            let item = new DiagramCoordSetTuple();
            item.name = tuple.name;
            item.key = tuple.key;
            item.enabled = tuple.enabled;
            item.isLanding = tuple.isLanding;
            coordSetsByModelSetKey[tuple.data.modelSetKey].push(item);
        }

        this._lastDiagramCoordSetTuplesByModelSetKey = coordSetsByModelSetKey;

        for (let key of Object.keys(coordSetsByModelSetKey)) {
            if (this._coordSetSubjectByModelSetKey[key] != null)
                this._coordSetSubjectByModelSetKey[key].next(
                    coordSetsByModelSetKey[key]
                );
        }
    }
}
