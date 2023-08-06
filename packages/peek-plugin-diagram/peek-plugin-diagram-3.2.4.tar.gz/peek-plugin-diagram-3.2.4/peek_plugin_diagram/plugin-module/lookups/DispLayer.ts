import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private";

@addTupleType
export class DispLayer extends Tuple {
    public static readonly tupleName = diagramTuplePrefix + "DispLayer";

    id: number;
    name: string;
    order: number;
    selectable: boolean;
    visible: boolean;
    modelSetId: number;

    constructor() {
        super(DispLayer.tupleName);
    }
}
