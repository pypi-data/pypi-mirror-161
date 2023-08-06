import { Injectable } from "@angular/core";
import {
    DiagramPositionService,
    DispKeyLocation,
    OptionalPositionArgsI,
    PositionUpdatedI,
} from "../../DiagramPositionService";
import { Observable, Subject } from "rxjs";

import { DispKeyLocationTuple } from "../location-loader/DispKeyLocationTuple";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { PrivateDiagramLocationLoaderService } from "../location-loader";
import { PrivateDiagramCoordSetService } from "./PrivateDiagramCoordSetService";

export interface DiagramPositionI {
    coordSetKey: string;
    x: number;
    y: number;
    zoom: number;
    opts: OptionalPositionArgsI;
}

export interface DiagramPositionByKeyI {
    modelSetKey: string;
    coordSetKey: string | null;
    opts: OptionalPositionArgsI;
    dispKeyIndexes: DispKeyLocationTuple[] | null;
}

export interface DiagramPositionByCoordSetI {
    modelSetKey: string | null;
    coordSetKey: string | null;
}

@Injectable()
export class PrivateDiagramPositionService extends DiagramPositionService {
    // This observable is for when the canvas updates the title
    private titleUpdatedSubject: Subject<string> = new Subject<string>();
    private positionByCoordSetSubject =
        new Subject<DiagramPositionByCoordSetI>();
    private positionSubject = new Subject<DiagramPositionI>();
    private positionByKeySubject = new Subject<DiagramPositionByKeyI>();
    private isReadySubject = new Subject<boolean>();
    private positionUpdatedSubject = new Subject<PositionUpdatedI>();
    private selectKeysSubject = new Subject<string[]>();

    constructor(
        private coordSetService: PrivateDiagramCoordSetService,
        private locationIndexService: PrivateDiagramLocationLoaderService,
        private balloonMsg: BalloonMsgService
    ) {
        super();
    }

    positionByCoordSet(modelSetKey: string, coordSetKey: string): void {
        this.positionByCoordSetSubject.next({ modelSetKey, coordSetKey });
    }

    position(
        coordSetKey: string,
        x: number,
        y: number,
        zoom: number,
        opts: OptionalPositionArgsI = {}
    ): void {
        this.positionSubject.next({
            coordSetKey: coordSetKey,
            x: x,
            y: y,
            zoom: zoom,
            opts,
        });
    }

    async positionByKeys(
        keys: string[],
        modelSetKey: string,
        coordSetKey: string
    ): Promise<void> {
        const locations: any[] = [];

        for (const key of keys) {
            const keyLocations = await this.locationsForKey(modelSetKey, key);

            if (keyLocations?.length === 0) {
                continue;
            }

            const keyLocation = keyLocations[0].positions;

            locations.push(...keyLocation);
        }

        let x = 0;
        let y = 0;

        for (const location of locations) {
            x += location.x;
            y += location.y;
        }

        x /= locations.length;
        y /= locations.length;

        this.position(
            coordSetKey,
            parseFloat(x.toString()),
            parseFloat(y.toString()),
            parseFloat("0.85"),
            {}
        );

        this.selectKeysSubject.next(keys);
    }

    async positionByKey(
        modelSetKey: string,
        coordSetKey: string | null,
        opts: OptionalPositionArgsI = {}
    ): Promise<void> {
        if (!this.coordSetService.isReady()) {
            throw new Error(
                "positionByKey called before coordSetService is ready"
            );
        }

        if (opts.highlightKey == null || opts.highlightKey.length == 0)
            throw new Error("positionByKey must be passed opts.highlightKey");

        let dispKeyIndexes: DispKeyLocationTuple[] =
            await this.locationIndexService.getLocations(
                modelSetKey,
                opts.highlightKey
            );

        if (dispKeyIndexes.length == 0) {
            this.balloonMsg.showError(
                `Can not locate display item ${opts.highlightKey}` +
                    ` in model set ${modelSetKey}`
            );
        }

        if (coordSetKey != null) {
            dispKeyIndexes = dispKeyIndexes //
                .filter((d) => d.coordSetKey === coordSetKey);

            if (!dispKeyIndexes.length) {
                this.balloonMsg.showError(
                    `Can not locate display item ${opts.highlightKey}` +
                        ` in model set ${modelSetKey}, in coord set ${coordSetKey}`
                );
            }
        }

        if (dispKeyIndexes.length === 1) {
            const dispKeyIndex = dispKeyIndexes[0];

            const coordSet = this.coordSetService.coordSetForKey(
                modelSetKey,
                dispKeyIndex.coordSetKey
            );

            if (coordSet == null) {
                throw new Error(
                    "Could not find coordSet for key=" +
                        dispKeyIndex.coordSetKey
                );
            }

            this.positionSubject.next({
                coordSetKey: dispKeyIndex.coordSetKey,
                x: dispKeyIndex.x,
                y: dispKeyIndex.y,
                zoom: coordSet.positionOnZoom,
                opts,
            });

            return;
        }

        // Emitting this will cause the diagram to ask the user what to do.
        this.positionByKeySubject.next({
            modelSetKey: modelSetKey,
            coordSetKey: coordSetKey,
            opts: opts,
            dispKeyIndexes: dispKeyIndexes,
        });
    }

    async canPositionByKey(
        modelSetKey: string,
        dispKey: string
    ): Promise<boolean> {
        const val: DispKeyLocationTuple[] =
            await this.locationIndexService.getLocations(modelSetKey, dispKey);
        return val.length != 0;
    }

    async locationsForKey(
        modelSetKey: string,
        dispKey: string
    ): Promise<DispKeyLocation[]> {
        const tuples: DispKeyLocationTuple[] =
            await this.locationIndexService.getLocations(modelSetKey, dispKey);

        const locations = [];
        const locationByCoordSet = {};
        for (const tuple of tuples) {
            let location = locationByCoordSet[tuple.coordSetKey];
            if (location == null) {
                location = {
                    modelSetKey: modelSetKey,
                    coordSetKey: tuple.coordSetKey,
                    dispKey: dispKey,
                    positions: [],
                    zoom: 2.0,
                };
                locationByCoordSet[tuple.coordSetKey] = location;
                locations.push(location);
            }

            location.positions.push({ x: tuple.x, y: tuple.y });
        }
        return locations;
    }

    setReady(value: boolean) {
        this.isReadySubject.next(true);
    }

    setTitle(value: string) {
        this.titleUpdatedSubject.next(value);
    }

    positionUpdated(pos: PositionUpdatedI): void {
        this.positionUpdatedSubject.next(pos);
    }

    isReadyObservable(): Observable<boolean> {
        return this.isReadySubject;
    }

    positionUpdatedObservable(): Observable<PositionUpdatedI> {
        return this.positionUpdatedSubject;
    }

    titleUpdatedObservable(): Observable<string> {
        return this.titleUpdatedSubject;
    }

    positionObservable(): Observable<DiagramPositionI> {
        return this.positionSubject;
    }

    positionByKeyObservable(): Observable<DiagramPositionByKeyI> {
        return this.positionByKeySubject;
    }

    positionByCoordSetObservable(): Observable<DiagramPositionByCoordSetI> {
        return this.positionByCoordSetSubject;
    }

    selectKeysObservable(): Observable<string[]> {
        return this.selectKeysSubject;
    }
}
