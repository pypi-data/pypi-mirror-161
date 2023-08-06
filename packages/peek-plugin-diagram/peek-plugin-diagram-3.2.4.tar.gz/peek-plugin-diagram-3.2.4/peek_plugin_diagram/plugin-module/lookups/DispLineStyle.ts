import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private";

@addTupleType
export class DispLineStyle extends Tuple {
    public static readonly tupleName = diagramTuplePrefix + "DispLineStyle";

    id: number;
    name: string;
    backgroundFillDashSpace: string;

    readonly CAP_BUTT = "butt";
    readonly CAP_ROUND = "round";
    readonly CAP_SQUARE = "square";
    capStyle: string;

    readonly JOIN_BEVEL = "bevel";
    readonly JOIN_ROUND = "round";
    readonly JOIN_MITER = "miter";
    joinStyle: string;

    dashPattern: null | string; // Stored in the DB as a string
    dashPatternParsed: null | number[]; // Parsed when the tuples are loaded

    startArrowSize: number;
    endArrowSize: number;

    // winStyle: number;

    modelSetId: number;

    scalable: boolean;

    constructor() {
        super(DispLineStyle.tupleName);
    }
}
