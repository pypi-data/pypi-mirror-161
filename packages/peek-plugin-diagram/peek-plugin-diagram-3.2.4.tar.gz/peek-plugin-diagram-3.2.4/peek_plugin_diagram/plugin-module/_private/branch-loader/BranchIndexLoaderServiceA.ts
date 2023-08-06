import { Observable } from "rxjs";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { BranchIndexLoaderStatusTuple } from "./BranchIndexLoaderStatusTuple";
import { BranchIndexResultI } from "./BranchIndexLoaderService";

export abstract class BranchIndexLoaderServiceA extends NgLifeCycleEvents {
    constructor() {
        super();
    }

    abstract isReady(): boolean;

    abstract isReadyObservable(): Observable<boolean>;

    abstract statusObservable(): Observable<BranchIndexLoaderStatusTuple>;

    abstract status(): BranchIndexLoaderStatusTuple;

    abstract getBranches(
        modelSetKey: string,
        coordSetId: number | null,
        keys: string[]
    ): Promise<BranchIndexResultI>;
}
