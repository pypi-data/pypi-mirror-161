import { DispPoly, DispPolyT } from "./DispPoly";
import {
    DispBase,
    DispHandleI,
    DispHandleTypeE,
    DispType,
    PointI,
} from "./DispBase";
import {
    PeekCanvasShapePropsContext,
    ShapeProp,
    ShapePropType,
} from "../canvas/PeekCanvasShapePropsContext";
import { ModelCoordSet } from "@peek/peek_plugin_diagram/_private/tuples/ModelCoordSet";
import { DispColor } from "@peek/peek_plugin_diagram/lookups";
import { PeekCanvasBounds } from "../canvas/PeekCanvasBounds";
import { BranchTuple } from "@peek/peek_plugin_diagram/_private/branch/BranchTuple";
import { PrivateDiagramLookupService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramLookupService";
import { DispEdgeTemplate, DispEdgeTemplateT } from "./DispEdgeTemplate";

export interface DispPolylineT extends DispPolyT {
    // Edge Color
    ec: number;
    ecl: DispColor;

    // Start Key
    sk: string;

    // End Key
    ek: string;

    // Start end type, is this an arrow, etc?
    st: number | null;

    // End End Type
    et: number | null;

    // Target Template Line ID
    ti: number;

    // Target Template Line Name
    tn: string;
}

export enum DispPolylineEndTypeE {
    None = 0,
    Arrow = 1,
    Dot = 2,
}

export class DispPolyline extends DispPoly {
    static targetGroupId(disp: DispPolylineT): number {
        return disp.ti;
    }

    static setTargetEdgeTemplateId(disp: DispPolylineT, val: number): void {
        disp.ti = val;
    }

    static setTargetEdgeTemplateName(
        disp: DispPolylineT,
        coordSetId: number,
        name: string
    ): void {
        disp.tn = `${coordSetId}|${name}`;
    }

    static targetEdgeTemplateCoordSetId(disp: DispPolylineT): number | null {
        if (disp.tn == null || disp.tn.indexOf("|") === -1) return null;
        return parseInt(disp.tn.split("|")[0]);
    }

    static targetEdgeTemplateName(disp: DispPolylineT): string | null {
        if (disp.tn == null || disp.tn.indexOf("|") === -1) return null;
        return disp.tn.split("|")[1];
    }

    /** Edge Color
     *
     * And alternate color of this polyline, used to color it if it's representing an
     * edge of a GraphDB.
     */
    static edgeColor(disp: DispPolylineT): DispColor {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        return disp.ecl;
    }

    /** Set Edge Color
     *
     */
    static setEdgeColor(disp: DispPolylineT, val: DispColor): void {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        disp.ecl = val;
        disp.ec = val == null ? null : val.id;
    }

    /** Start Key
     *
     * The key of another disp object if the start of this polyline is related to it
     */
    static startKey(disp: DispPolylineT): string | null {
        return disp.sk;
    }

    /** End Key
     *
     * The key of another disp object if the end of this polyline is related to it
     */
    static endKey(disp: DispPolylineT): string | null {
        return disp.ek;
    }

    /** Start Key
     *
     * The key of another disp object if the start of this polyline is related to it
     */
    static startEndType(disp: DispPolylineT): DispPolylineEndTypeE {
        return disp.st || 0;
    }

    static setStartEndType(disp: DispPolylineT, val: number | null): void {
        disp.st = val == 0 ? null : val;
    }

    /** End Key
     *
     * The key of another disp object if the end of this polyline is related to it
     */
    static endEndType(disp: DispPolylineT): DispPolylineEndTypeE {
        return disp.et || 0;
    }

    static setEndEndType(disp: DispPolylineT, val: number | null): void {
        disp.et = val == 0 ? null : val;
    }

    /** Start End Keys
     *
     * This method returns a unique list af the start and end keys of the selected
     * polylines.
     *
     * Non-polylines are ignored.
     *
     * @param disps: A list of shapes
     * @return: A list of start and end keys
     */
    static startEndKeys(disps: any[]): string[] {
        let keysDict = {};
        for (let disp of disps) {
            if (DispBase.typeOf(disp) != DispType.polyline) continue;

            let startKey = DispPolyline.startKey(disp);
            let endKey = DispPolyline.endKey(disp);

            if (startKey != null) keysDict[startKey] = true;
            else if (endKey != null) keysDict[endKey] = true;
        }
        return Object.keys(keysDict);
    }

    static deltaMoveStart(disp: any, dx: number, dy: number) {
        disp.g[0] += dx;
        disp.g[1] += dy;
        DispBase.setBoundsNull(disp);
    }

    static deltaMoveEnd(disp: any, dx: number, dy: number) {
        let len = disp.g.length;
        disp.g[len - 2] += dx;
        disp.g[len - 1] += dy;
        DispBase.setBoundsNull(disp);
    }

    static center(disp): PointI {
        return PeekCanvasBounds.fromGeom(disp.g).center();
    }

    static firstPoint(disp): PointI {
        return { x: disp.g[0], y: disp.g[1] };
    }

    static lastPoint(disp): PointI {
        let l = disp.g.length;
        return { x: disp.g[l - 2], y: disp.g[l - 1] };
    }

    static create(coordSet: ModelCoordSet): DispPolylineT {
        return <DispPolylineT>DispPoly.create(coordSet, DispBase.TYPE_DPL);
    }

    static contains(
        dispPoly: DispPolylineT,
        point: PointI,
        margin: number
    ): boolean {
        const x = point.x;
        const y = point.y;

        const points = DispPolyline.geom(dispPoly);
        let x1 = points[0];
        let y1 = points[1];
        for (let i = 2; i < points.length; i += 2) {
            let x2 = points[i];
            let y2 = points[i + 1];

            let dx = x2 - x1;
            let dy = y2 - y1;

            // For Bounding Box
            let left = (x1 < x2 ? x1 : x2) - margin;
            let right = (x1 < x2 ? x2 : x1) + margin;
            let top = (y1 < y2 ? y1 : y2) - margin;
            let bottom = (y1 < y2 ? y2 : y1) + margin;

            // Special condition for vertical lines
            if (dx == 0) {
                if (left <= x && x <= right && top <= y && y <= bottom) {
                    return true;
                }
            }

            let slope = dy / dx;
            // y = mx + c
            // intercept c = y - mx
            let intercept = y1 - slope * x1; // which is same as y2 - slope * x2

            let yVal = slope * x + intercept;
            let xVal = (y - intercept) / slope;

            if (
                ((y - margin < yVal && yVal < y + margin) ||
                    (x - margin < xVal && xVal < x + margin)) &&
                left <= x &&
                x <= right &&
                top <= y &&
                y <= bottom
            )
                return true;

            x1 = x2;
            y1 = y2;
        }

        return false;
    }

    // ---------------
    // Support shape editing
    static makeShapeContext(context: PeekCanvasShapePropsContext): void {
        DispPoly.makeShapeContext(context);

        let lineEndOptions = [
            {
                name: "None",
                object: { id: DispPolylineEndTypeE.None },
                value: DispPolylineEndTypeE.None,
            },
            {
                name: "Arrow",
                object: { id: DispPolylineEndTypeE.Arrow },
                value: DispPolylineEndTypeE.Arrow,
            },
            {
                name: "Dot",
                object: { id: DispPolylineEndTypeE.Dot },
                value: DispPolylineEndTypeE.Dot,
            },
        ];

        context.addProp(
            new ShapeProp(
                ShapePropType.Option,
                (disp) => {
                    // The UI expects an object with an ID
                    return { id: DispPolyline.startEndType(disp) };
                },
                (disp, valObj) => DispPolyline.setStartEndType(disp, valObj.id),
                "Line Start Style",
                { options: lineEndOptions }
            )
        );

        context.addProp(
            new ShapeProp(
                ShapePropType.Option,
                (disp) => {
                    // The UI expects an object with an ID
                    return { id: DispPolyline.endEndType(disp) };
                },
                (disp, valObj) => DispPolyline.setEndEndType(disp, valObj.id),
                "Line End Style",
                { options: lineEndOptions }
            )
        );
    }

    /** Set Target Line
     *
     * Change the template that this polyline immitates
     *
     *
     * @param polyline
     * @param edgeTemplate
     * @param edgeTemplateCoordSetId
     * @param lookupService
     * @param branchTuple
     */
    static setEdgeTemplate(
        polyline: DispPolylineT,
        edgeTemplate: DispEdgeTemplateT,
        edgeTemplateCoordSetId: number,
        lookupService: PrivateDiagramLookupService,
        branchTuple: BranchTuple
    ): void {
        DispPolyline.setTargetEdgeTemplateName(
            polyline,
            edgeTemplateCoordSetId,
            DispEdgeTemplate.templateName(edgeTemplate)
        );

        DispPolyline.setLayer(polyline, DispEdgeTemplate.layer(edgeTemplate));
        DispPolyline.setLevel(polyline, DispEdgeTemplate.level(edgeTemplate));

        DispPolyline.setLineWidth(
            polyline,
            DispEdgeTemplate.lineWidth(edgeTemplate)
        );
        DispPolyline.setLineColor(
            polyline,
            DispEdgeTemplate.lineColor(edgeTemplate)
        );
        DispPolyline.setLineStyle(
            polyline,
            DispEdgeTemplate.lineStyle(edgeTemplate)
        );

        DispPolyline.setEndEndType(
            polyline,
            DispEdgeTemplate.endEndType(edgeTemplate)
        );
        DispPolyline.setStartEndType(
            polyline,
            DispEdgeTemplate.startEndType(edgeTemplate)
        );
    }

    // ---------------
    // Represent the disp as a user friendly string

    static makeShapeStr(disp: DispPolylineT): string {
        let center = DispPolyline.center(disp);
        return (
            DispBase.makeShapeStr(disp) +
            `\nAt : ${parseInt(<any>center.x)}x${parseInt(<any>center.y)}`
        );
    }

    // ---------------
    // Generate a list of handles to edit this shape

    static isStartHandle(disp, handleIndex: number): boolean {
        if (DispBase.typeOf(disp) != DispType.polyline) return false;

        return handleIndex == 0;
    }

    static isEndHandle(disp, handleIndex: number): boolean {
        if (DispBase.typeOf(disp) != DispType.polyline) return false;

        return handleIndex == DispPolyline.geom(disp).length / 2 - 1;
    }

    static handlePoints(disp, margin: number): DispHandleI[] {
        let result = [];

        let points = DispPolyline.geom(disp);

        function addHandle(p, ref) {
            let adj = p.x - ref.x;
            let opp = p.y - ref.y;
            let hypot = Math.sqrt(Math.pow(adj, 2) + Math.pow(opp, 2));

            let multiplier = margin / hypot;

            result.push({
                disp: disp,
                center: {
                    x: p.x + adj * multiplier,
                    y: p.y + opp * multiplier,
                },
                handleType: DispHandleTypeE.movePoint,
            });
        }

        //function rotatePoint(point, theta) {
        //    // Rotates the given polygon which consists of corners represented as (x,y),
        //    // around the ORIGIN, clock-wise, theta degrees
        //    let simTheta = Math.sin(theta);
        //    let cosTheta = Math.cos(theta);
        //
        //    return {
        //        x: point.x * cosTheta - point.y * simTheta,
        //        y: point.y = point.x * simTheta + point.y * cosTheta
        //    };
        //}
        //
        // //
        // // Calculates the angle ABC (in radians)
        // //
        // // A first point
        // // C second point
        // // B center point
        // //
        //
        //
        //         function findAngle(A, B, C) {
        //            let AB = Math.hypot(B.x - A.x, B.y - A.y);
        //            let BC = Math.hypot(B.x - C.x, B.y - C.y);
        //            let AC = Math.hypot(C.x - A.x, C.y - A.y);
        //            return Math.acos((BC * BC + AB * AB - AC * AC) / (2 * BC * AB));
        //         }

        function pointForIndex(index: number) {
            index *= 2;
            return { x: points[index], y: points[index + 1] };
        }

        let firstXy = { x: points[0], y: points[1] };
        addHandle(pointForIndex(0), pointForIndex(1));

        let lastXy = firstXy;
        for (let i = 1; i < points.length / 2; ++i) {
            let thisXy = pointForIndex(i);
            let refXy = lastXy;

            // If this is not the last point
            if (i + 2 <= points.length / 2) {
                let nextXy = pointForIndex(i + 1);

                //let angle = findAngle(lastXy, thisXy, nextXy);
                //refXy = rotatePoint({x:lastXy.x - this.left, y:lastXy.y - this.top}, angle / 2);

                refXy = {
                    x: (lastXy.x + nextXy.x) / 2,
                    y: (lastXy.y + nextXy.y) / 2,
                };
            }
            addHandle(thisXy, refXy);
            lastXy = thisXy;
        }

        return result;
    }
}
