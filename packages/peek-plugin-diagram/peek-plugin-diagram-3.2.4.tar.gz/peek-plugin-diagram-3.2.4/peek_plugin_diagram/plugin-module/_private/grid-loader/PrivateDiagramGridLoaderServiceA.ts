import { GridTuple } from "./GridTuple";
import { Observable } from "rxjs";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { PrivateDiagramGridLoaderStatusTuple } from "./PrivateDiagramGridLoaderStatusTuple";

export abstract class PrivateDiagramGridLoaderServiceA extends NgLifeCycleEvents {
    abstract observable: Observable<GridTuple[]>;

    protected constructor() {
        super();
    }

    abstract isReady(): Promise<boolean>;

    abstract isReadyObservable(): Observable<boolean>;

    abstract statusObservable(): Observable<PrivateDiagramGridLoaderStatusTuple>;

    abstract status(): PrivateDiagramGridLoaderStatusTuple;

    abstract watchGrids(gridKeys: string[]): void;

    abstract loadGrids(
        currentGridUpdateTimes: { [gridKey: string]: string },
        gridKeys: string[]
    ): void;
}
