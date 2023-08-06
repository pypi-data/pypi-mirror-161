import { DispBase, DispBaseT, PointI } from "./DispBase";
import { DispColor, DispTextStyle } from "@peek/peek_plugin_diagram/lookups";
import {
    PeekCanvasShapePropsContext,
    ShapeProp,
    ShapePropType,
} from "../canvas/PeekCanvasShapePropsContext";
import { ModelCoordSet } from "@peek/peek_plugin_diagram/_private/tuples";

export enum CurvedTextVerticalAlign {
    top = -1,
    center = 0,
    bottom = 1,
}

export enum CurvedTextHorizontalAlign {
    left = -1,
    center = 0,
    right = 1,
}

export interface DispCurvedTextT extends DispBaseT {
    // Text Style
    fs: number;
    fsl: DispTextStyle;

    // Colour
    c: number;
    cl: DispColor;

    // Vertical Alignment
    va: number;

    // Horizontal Alignment
    ha: number;

    // Text
    te: string;

    // Text Height (Optional)
    th: number | null;

    // Horizontal Stretch (default 1)
    hs: number;

    // Spacing Between Text Factor
    sbt: number;
}

export class DispCurvedText extends DispBase {
    static textStyle(disp: DispCurvedTextT): DispTextStyle {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        return disp.fsl;
    }

    static setTextStyle(disp: DispCurvedTextT, val: DispTextStyle): void {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        disp.fsl = val;
        disp.fs = val == null ? null : val.id;
    }

    static color(disp: DispCurvedTextT): DispColor {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        return disp.cl;
    }

    static setColor(disp: DispCurvedTextT, val: DispColor): void {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        disp.cl = val;
        disp.c = val == null ? null : val.id;
    }

    static verticalAlign(disp: DispCurvedTextT): CurvedTextVerticalAlign {
        let val = disp.va;
        if (val == CurvedTextVerticalAlign.top)
            return CurvedTextVerticalAlign.top;
        if (val == CurvedTextVerticalAlign.bottom)
            return CurvedTextVerticalAlign.bottom;
        return CurvedTextVerticalAlign.center;
    }

    static horizontalAlign(disp: DispCurvedTextT): CurvedTextHorizontalAlign {
        let val = disp.ha;
        if (val == CurvedTextHorizontalAlign.left)
            return CurvedTextHorizontalAlign.left;
        if (val == CurvedTextHorizontalAlign.right)
            return CurvedTextHorizontalAlign.right;
        return CurvedTextHorizontalAlign.center;
    }

    static text(disp: DispCurvedTextT): string {
        return disp.te;
    }

    static setText(disp: DispCurvedTextT, val: string): void {
        disp.te = val;
        DispBase.setBoundsNull(disp);
    }

    static height(disp: DispCurvedTextT): number | null {
        return disp.th;
    }

    static horizontalStretch(disp: DispCurvedTextT): number {
        return disp.hs;
    }

    static centerPointX(disp: DispCurvedTextT): number {
        return disp.g[0];
    }

    static centerPointY(disp: DispCurvedTextT): number {
        return disp.g[1];
    }

    static center(disp: DispCurvedTextT): PointI {
        return { x: disp.g[0], y: disp.g[1] };
    }

    static setCenterPoint(disp: DispCurvedTextT, x: number, y: number): void {
        disp.g = [x, y];
        DispBase.setBoundsNull(disp);
    }

    static spacingBetweenTexts(disp: DispCurvedTextT): number {
        return disp.sbt;
    }

    static create(coordSet: ModelCoordSet): DispCurvedTextT {
        let newDisp = {
            ...DispBase.create(coordSet, DispBase.TYPE_DT),
            // From Text
            va: CurvedTextVerticalAlign.center, // CurvedTextVerticalAlign.center
            ha: CurvedTextHorizontalAlign.center, // CurvedTextHorizontalAlign.center
            r: 0, // number
            th: null, // number | null
            hs: 1, // number | null
        };

        DispCurvedText.setSelectable(newDisp, true);
        DispCurvedText.setText(newDisp, "New Text");

        let dispTextStyle = new DispTextStyle();
        dispTextStyle.id = coordSet.editDefaultTextStyleId;

        let dispColor = new DispColor();
        dispColor.id = coordSet.editDefaultColorId;

        DispCurvedText.setTextStyle(newDisp, dispTextStyle);
        DispCurvedText.setColor(newDisp, dispColor);

        DispCurvedText.setText(newDisp, "New Text");
        DispCurvedText.setCenterPoint(newDisp, 0, 0);

        return newDisp;
    }

    static makeShapeContext(context: PeekCanvasShapePropsContext): void {
        DispBase.makeShapeContext(context);

        context.addProp(
            new ShapeProp(
                ShapePropType.MultilineString,
                DispCurvedText.text,
                DispCurvedText.setText,
                "Text"
            )
        );

        context.addProp(
            new ShapeProp(
                ShapePropType.TextStyle,
                DispCurvedText.textStyle,
                DispCurvedText.setTextStyle,
                "Text Style"
            )
        );

        context.addProp(
            new ShapeProp(
                ShapePropType.Color,
                DispCurvedText.color,
                DispCurvedText.setColor,
                "Color"
            )
        );
    }

    // ---------------
    // Represent the disp as a user friendly string

    static makeShapeStr(disp: DispCurvedTextT): string {
        let center = DispCurvedText.center(disp);
        return (
            DispBase.makeShapeStr(disp) +
            `\nText : ${DispCurvedText.text(disp)}` +
            `\nAt : ${parseInt(<any>center.x)}x${parseInt(<any>center.y)}`
        );
    }
}
