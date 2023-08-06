import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "../PluginNames";

@addTupleType
export class BranchIndexLoaderStatusTuple extends Tuple {
    public static readonly tupleName =
        diagramTuplePrefix + "BranchIndexLoaderStatusTuple";

    cacheForOfflineEnabled: boolean = false;
    initialLoadComplete: boolean = false;
    loadProgress: number = 0;
    loadTotal: number = 0;
    lastCheck: Date;

    constructor() {
        super(BranchIndexLoaderStatusTuple.tupleName);
    }
}
