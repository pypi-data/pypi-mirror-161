import { PeekCanvasConfig } from "../canvas/PeekCanvasConfig.web";
import {
    DrawModeE,
    PeekDispRenderDelegateABC,
} from "./PeekDispRenderDelegateABC.web";
import {
    DispText,
    DispTextT,
    TextHorizontalAlign,
    TextVerticalAlign,
} from "../canvas-shapes/DispText";
import { pointToPixel } from "../DiagramUtil";
import { PeekCanvasBounds } from "../canvas/PeekCanvasBounds";
import { DispBaseT, PointI } from "../canvas-shapes/DispBase";
import { PeekCanvasModel } from "../canvas/PeekCanvasModel.web";

export class PeekDispRenderDelegateText extends PeekDispRenderDelegateABC {
    private textMeasureCtx;

    constructor(config: PeekCanvasConfig, model: PeekCanvasModel) {
        super(config, model);

        // Create a canvas element for measuring text
        let canvas = document.createElement("canvas");
        this.textMeasureCtx = canvas.getContext("2d");
    }

    updateBounds(disp: DispBaseT, zoom: number): void {
        this.drawAndCalcBounds(
            <DispTextT>disp,
            this.textMeasureCtx,
            zoom,
            true
        );
    }

    /** Draw
     *
     * NOTE: The way the text is scaled and drawn must match _calcTextSize(..)
     * in python module DispCompilerTask.py
     */
    draw(disp: DispTextT, ctx, zoom: number, pan: PointI, drawMode: DrawModeE) {
        this.drawAndCalcBounds(disp, ctx, zoom, false);
    }

    drawSelected(disp, ctx, zoom: number, pan: PointI, drawMode: DrawModeE) {
        let bounds = disp.bounds;
        if (bounds == null) return;

        // DRAW THE SELECTED BOX
        let selectionConfig =
            this.config.getSelectionDrawDetailsForDrawMode(drawMode);

        // Move the selection line a bit away from the object
        let offset = (selectionConfig.width + selectionConfig.lineGap) / zoom;

        let twiceOffset = 2 * offset;
        let x = bounds.x - offset;
        let y = bounds.y - offset;
        let w = bounds.w + twiceOffset;
        let h = bounds.h + twiceOffset;

        ctx.dashedRect(x, y, w, h, selectionConfig.dashLen / zoom);
        ctx.strokeStyle = selectionConfig.color;
        ctx.lineWidth = selectionConfig.width / zoom;
        ctx.stroke();
    }

    drawEditHandles(disp, ctx, zoom: number, pan: PointI) {
        /*
         // DRAW THE EDIT HANDLES
         ctx.fillStyle = CanvasRenderer.SELECTION_COLOR;
         let handles = this.handles();
         for (let i = 0; i < handles.length; ++i) {
         let handle = handles[i];
         ctx.fillRect(handle.x, handle.y, handle.w, handle.h);
         }
         */
    }

    /** Draw
     *
     * NOTE: The way the text is scaled and drawn must match _calcTextSize(..)
     * in python module DispCompilerTask.py
     */
    private drawAndCalcBounds(
        disp: DispTextT,
        ctx,
        zoom: number,
        updateBounds: boolean
    ) {
        // Give meaning to our short names
        let rotationRadian = (DispText.rotation(disp) / 180.0) * Math.PI;

        let fontStyle = DispText.textStyle(disp);
        let fillColor = DispText.color(disp);

        // Null colors are also not drawn
        fillColor = fillColor && fillColor.color ? fillColor : null;

        // TODO, Draw a box around the text, based on line style

        let horizontalStretchFactor = DispText.horizontalStretch(disp);
        let textHeight = DispText.height(disp);

        let fontSize = fontStyle.fontSize * fontStyle.scaleFactor;

        if (textHeight != null) fontSize = textHeight;

        const font =
            (fontStyle.fontStyle || "") +
            " " +
            fontSize +
            "px " +
            fontStyle.fontName;

        let lineHeight = pointToPixel(fontSize);

        let textAlign = null;
        let horizontalAlignEnum = DispText.horizontalAlign(disp);
        if (horizontalAlignEnum == TextHorizontalAlign.left)
            textAlign = "start";
        else if (horizontalAlignEnum == TextHorizontalAlign.center)
            textAlign = "center";
        else if (horizontalAlignEnum == TextHorizontalAlign.right)
            textAlign = "end";

        let textBaseline = null;
        let verticalAlignEnum = DispText.verticalAlign(disp);
        if (verticalAlignEnum == TextVerticalAlign.top) textBaseline = "top";
        else if (verticalAlignEnum == TextVerticalAlign.center)
            textBaseline = "middle";
        else if (verticalAlignEnum == TextVerticalAlign.bottom)
            textBaseline = "bottom";

        const centerX = DispText.centerPointX(disp);
        const centerY = DispText.centerPointY(disp);

        // save state
        ctx.save();
        ctx.translate(centerX, centerY);
        ctx.rotate(rotationRadian); // Degrees to radians

        ctx.textAlign = textAlign;
        ctx.textBaseline = textBaseline;
        ctx.font = font;

        if (!fontStyle.scalable) {
            let unscale = 1.0 / zoom;
            ctx.scale(unscale, unscale);
        }

        if (horizontalStretchFactor != 1) {
            ctx.scale(horizontalStretchFactor, 1);
        }

        // Bounds can get serliased in branches, so check to see if it's actually the
        // class or just the restored object that it serialises to.
        if (updateBounds) {
            disp.bounds = new PeekCanvasBounds();
            disp.bounds.w = 0;
        }

        let lines = DispText.text(disp).split("\n");
        for (let lineIndex = 0; lineIndex < lines.length; ++lineIndex) {
            let line = lines[lineIndex];
            let yOffset = lineHeight * lineIndex;

            // Measure the width
            if (updateBounds) {
                let thisWidth = ctx.measureText(line).width / zoom;
                if (disp.bounds.w < thisWidth) disp.bounds.w = thisWidth;
            }

            if (fillColor) {
                ctx.fillStyle = fillColor.color;
                ctx.fillText(line, 0, yOffset);
            }

            //if (disp.lineColor) {
            //    ctx.lineWidth = disp.lineSize;
            //    ctx.strokeStyle = disp.lineColor;
            //    ctx.strokeText(line, 0, yOffset);
            //}
        }

        let singleLineHeight = lineHeight / zoom;
        if (updateBounds) {
            disp.bounds.h = singleLineHeight * lines.length;
        }

        // restore to original state
        ctx.restore();

        if (updateBounds) {
            if (horizontalAlignEnum == TextHorizontalAlign.left)
                disp.bounds.x = centerX;
            else if (horizontalAlignEnum == TextHorizontalAlign.center)
                disp.bounds.x = centerX - disp.bounds.w / 2;
            else if (horizontalAlignEnum == TextHorizontalAlign.right)
                disp.bounds.x = centerX - disp.bounds.w;

            if (verticalAlignEnum == TextVerticalAlign.top)
                disp.bounds.y = centerY;
            else if (verticalAlignEnum == TextVerticalAlign.center)
                disp.bounds.y = centerY - singleLineHeight / 2;
            else if (verticalAlignEnum == TextVerticalAlign.bottom)
                disp.bounds.y = centerY - singleLineHeight;
        }
    }
}
