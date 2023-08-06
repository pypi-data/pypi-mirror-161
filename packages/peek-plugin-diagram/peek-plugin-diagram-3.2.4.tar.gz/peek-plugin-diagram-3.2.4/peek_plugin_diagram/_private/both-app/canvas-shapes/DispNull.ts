import { DispBase, DispBaseT, PointI, PointsT } from "./DispBase";
import { PeekCanvasShapePropsContext } from "../canvas/PeekCanvasShapePropsContext";
import { ModelCoordSet } from "@peek/peek_plugin_diagram/_private/tuples";
import { PeekCanvasBounds } from "../canvas/PeekCanvasBounds";

export interface DispNullT extends DispBaseT {}

export class DispNull extends DispBase {
    static geom(disp): PointsT {
        return disp.g;
    }

    static centerPointX(disp: DispNullT): number {
        return disp.g[0];
    }

    static centerPointY(disp: DispNullT): number {
        return disp.g[1];
    }

    static center(disp: DispNullT): PointI {
        return { x: disp.g[0], y: disp.g[1] };
    }

    static setGeomFromBounds(disp: DispNullT, bounds: PeekCanvasBounds): void {
        disp.g = [
            bounds.x,
            bounds.y, // Bottom Left
            bounds.x + bounds.w,
            bounds.y, // Bottom Right
            bounds.x + bounds.w,
            bounds.y + bounds.h, // Top Right
            bounds.x,
            bounds.y + bounds.h, // Top Left
        ];
    }

    static create(coordSet: ModelCoordSet): DispNullT {
        return <DispNullT>DispBase.create(coordSet, DispBase.TYPE_DN);
    }

    static makeShapeContext(context: PeekCanvasShapePropsContext): void {
        DispBase.makeShapeContext(context);
    }

    // ---------------
    // Represent the disp as a user friendly string

    static makeShapeStr(disp: DispNullT): string {
        let center = DispNull.center(disp);
        return (
            DispBase.makeShapeStr(disp) +
            `\nAt : ${parseInt(<any>center.x)}x${parseInt(<any>center.y)}`
        );
    }
}
