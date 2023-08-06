import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private";

@addTupleType
export class DispColor extends Tuple {
    public static readonly tupleName = diagramTuplePrefix + "DispColor";

    id: number;
    name: string;
    color: string;
    altColor: string;
    swapPeriod: number;
    modelSetId: number;

    constructor() {
        super(DispColor.tupleName);
    }
}
