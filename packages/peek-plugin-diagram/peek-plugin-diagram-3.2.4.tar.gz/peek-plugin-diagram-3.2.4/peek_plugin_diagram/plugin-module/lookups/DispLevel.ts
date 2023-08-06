import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private";

@addTupleType
export class DispLevel extends Tuple {
    public static readonly tupleName = diagramTuplePrefix + "DispLevel";

    id: number;
    name: string;
    order: number;
    minZoom: number;
    maxZoom: number;
    coordSetId: number;

    constructor() {
        super(DispLevel.tupleName);
    }

    isVisibleAtZoom(zoom: number): boolean {
        return this.minZoom <= zoom && zoom < this.maxZoom;
    }
}
