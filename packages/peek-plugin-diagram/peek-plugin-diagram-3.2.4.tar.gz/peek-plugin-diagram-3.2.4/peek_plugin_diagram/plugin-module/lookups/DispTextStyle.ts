import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private";

@addTupleType
export class DispTextStyle extends Tuple {
    public static readonly tupleName = diagramTuplePrefix + "DispTextStyle";

    id: number;
    name: string;
    fontName: string;
    fontSize: number;
    fontStyle: string | null;
    scalable: boolean;
    scaleFactor: number;
    modelSetId: number;
    spacingBetweenTexts: number;

    constructor() {
        super(DispTextStyle.tupleName);
    }
}
