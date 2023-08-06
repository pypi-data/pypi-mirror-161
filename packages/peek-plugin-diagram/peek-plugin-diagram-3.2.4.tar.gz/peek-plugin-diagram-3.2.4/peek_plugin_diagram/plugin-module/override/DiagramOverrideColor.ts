import {
    DiagramOverrideBase,
    DiagramOverrideTypeE,
} from "./DiagramOverrideBase";
import { addTupleType } from "@synerty/vortexjs";
import { DispColor } from "../lookups";
import { diagramTuplePrefix } from "../_private/PluginNames";

/** Diagram Delta Color Override Tuple
 *
 * This delta applies an override colour to a set of display keys
 *
 */
@addTupleType
export class DiagramOverrideColor extends DiagramOverrideBase {
    public static readonly tupleName =
        diagramTuplePrefix + "DiagramOverrideColor";

    private dispKeys_ = [];
    private lineColor_: DispColor | null = null;
    private fillColor_: DispColor | null = null;
    private color_: DispColor | null = null;

    constructor(modelSetKey: string, coordSetKey: string) {
        super(
            modelSetKey,
            coordSetKey,
            DiagramOverrideTypeE.Color,
            DiagramOverrideColor.tupleName
        );
    }

    get dispKeys(): string[] {
        return this.dispKeys_;
    }

    get lineColor(): DispColor {
        return this.lineColor_;
    }

    get fillColor(): DispColor {
        return this.fillColor_;
    }

    get color(): DispColor {
        return this.color_;
    }

    addDispKeys(dispKeys: string[]): void {
        this.dispKeys_.add(dispKeys);
    }

    // Line Color
    setLineColor(value: DispColor | null): void {
        this.lineColor_ = value;
    }

    // Fill Color
    setFillColor(value: DispColor | null): void {
        this.fillColor_ = value;
    }

    // Color
    setColor(value: DispColor | null): void {
        this.color_ = value;
    }
}
