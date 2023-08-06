import { PeekCanvasConfig } from "../canvas/PeekCanvasConfig.web";
import {
    DrawModeE,
    PeekDispRenderDelegateABC,
} from "./PeekDispRenderDelegateABC.web";
import { DispPolygon } from "../canvas-shapes/DispPolygon";
import {
    DispBase,
    DispBaseT,
    DispType,
    PointI,
} from "../canvas-shapes/DispBase";
import { PeekCanvasBounds } from "../canvas/PeekCanvasBounds";
import {
    DispPolyline,
    DispPolylineEndTypeE,
    DispPolylineT,
} from "../canvas-shapes/DispPolyline";
import { DispPoly } from "../canvas-shapes/DispPoly";
import { PeekCanvasModel } from "../canvas/PeekCanvasModel.web";

export class PeekDispRenderDelegatePoly extends PeekDispRenderDelegateABC {
    constructor(config: PeekCanvasConfig, model: PeekCanvasModel) {
        super(config, model);
    }

    updateBounds(disp: DispBaseT): void {
        let geom = DispPolygon.geom(disp);
        disp.bounds = PeekCanvasBounds.fromGeom(geom);
    }

    draw(disp, ctx, zoom: number, pan: PointI, drawMode: DrawModeE) {
        let isPolygon = DispBase.typeOf(disp) == DispType.polygon;

        let fillColor = isPolygon ? DispPolygon.fillColor(disp) : null;
        let lineColor = DispPoly.lineColor(disp);
        let lineStyle = DispPoly.lineStyle(disp);
        let lineWidth = DispPoly.lineWidth(disp);

        if (!isPolygon && this.config.renderer.useEdgeColors) {
            let edgeColor = DispPolyline.edgeColor(<DispPolylineT>disp);
            if (edgeColor != null) lineColor = edgeColor;
        }

        let dashPattern = null;
        if (lineStyle != null && lineStyle.dashPatternParsed != null)
            dashPattern = lineStyle.dashPatternParsed;

        // Null colors are also not drawn
        fillColor = fillColor && fillColor.color ? fillColor : null;
        lineColor =
            lineStyle && lineColor && lineColor.color ? lineColor : null;

        let geom = DispPolygon.geom(disp);

        // If there are no colours defined then this is a selectable only shape
        if (!fillColor && !lineColor) return;

        let fillDirection = DispPolygon.fillDirection(disp);
        let fillPercentage = DispPolygon.fillPercent(disp);
        if (fillPercentage != null)
            fillPercentage = Math.min(100, fillPercentage);

        let firstPointX = geom[0]; // get details of point
        let firstPointY = geom[1]; // get details of point

        // Fill the background first, if required
        if (lineColor && lineStyle.backgroundFillDashSpace && dashPattern) {
            ctx.beginPath();
            ctx.moveTo(firstPointX, firstPointY);

            for (let i = 2; i < geom.length; i += 2) {
                let pointX = geom[i];
                let pointY = geom[i + 1];
                ctx.lineTo(pointX, pointY);
            }

            ctx.strokeStyle = this.config.renderer.backgroundColor;
            ctx.lineWidth = lineStyle.scalable ? lineWidth : lineWidth / zoom;
            ctx.lineJoin = lineStyle.joinStyle;
            ctx.lineCap = lineStyle.capStyle;
            ctx.stroke();
        }

        ctx.beginPath();
        ctx.moveTo(firstPointX, firstPointY);

        let lastPointX = firstPointX;
        let lastPointY = firstPointY;

        for (let i = 2; i < geom.length; i += 2) {
            let pointX = geom[i];
            let pointY = geom[i + 1];

            // Draw the segment
            this._drawLine(
                ctx,
                lastPointX,
                lastPointY,
                pointX,
                pointY,
                dashPattern,
                zoom,
                i / 2
            );

            lastPointX = pointX;
            lastPointY = pointY;
        }

        if (isPolygon) {
            if (lastPointX != firstPointX || lastPointY != firstPointY) {
                this._drawLine(
                    ctx,
                    lastPointX,
                    lastPointY,
                    firstPointX,
                    firstPointY,
                    dashPattern,
                    zoom,
                    geom.length
                );
            }
            ctx.closePath();
        }

        if (lineColor) {
            ctx.strokeStyle = lineColor.color;
            ctx.lineWidth = lineStyle.scalable ? lineWidth : lineWidth / zoom;
            ctx.lineJoin = lineStyle.joinStyle;
            ctx.lineCap = lineStyle.capStyle;
            ctx.stroke();
        }

        if (fillColor) {
            if (isPolygon && fillDirection != null && fillPercentage != null) {
                this._drawSquarePercentFill(
                    ctx,
                    PeekCanvasBounds.fromGeom(geom),
                    lineColor,
                    fillDirection,
                    fillPercentage
                );
            } else {
                ctx.fillStyle = fillColor.color;
                ctx.fill();
            }
        }

        // Draw the line ends
        if (!isPolygon && 4 <= geom.length) {
            this.drawPolyLineEnd(
                ctx,
                lineWidth / zoom,
                lineColor,
                geom[2],
                geom[3],
                geom[0],
                geom[1],
                DispPolyline.startEndType(disp)
            );

            let l = geom.length - 2;
            this.drawPolyLineEnd(
                ctx,
                lineWidth / zoom,
                lineColor,
                geom[l - 2],
                geom[l - 1],
                geom[l],
                geom[l + 1],
                DispPolyline.endEndType(disp)
            );
        }
    }

    drawSelected(disp, ctx, zoom: number, pan: PointI, drawMode: DrawModeE) {
        if (DispBase.typeOf(disp) == DispType.polygon)
            return this.drawSelectedPolygon(disp, ctx, zoom, pan, drawMode);
        return this.drawSelectedPolyline(disp, ctx, zoom, pan, drawMode);
    }

    drawEditHandles(disp, ctx, zoom: number, pan: PointI) {
        // DRAW THE EDIT HANDLES
        ctx.fillStyle = this.config.editor.selectionHighlightColor;
        const handles = this.handles(disp);
        for (const handle of handles) {
            const b = handle.box;
            ctx.beginPath();
            ctx.arc(b.x + b.w / 2, b.y + b.h / 2, b.h / 2, 0, 2 * Math.PI);
            ctx.fill();
        }
    }

    private _drawLine(
        ctx,
        x1: number,
        y1: number,
        x2: number,
        y2: number,
        dashPattern: null | number[],
        zoom: number,
        segmentNum: number
    ) {
        if (dashPattern == null) {
            ctx.lineTo(x2, y2);
            return;
        }

        let dashLen = dashPattern[segmentNum % dashPattern.length] / zoom;

        ctx.moveTo(x1, y1);

        let dX = x2 - x1;
        let dY = y2 - y1;
        let dashes = Math.floor(Math.sqrt(dX * dX + dY * dY) / dashLen);
        let dashX = dX / dashes;
        let dashY = dY / dashes;

        let q = 0;
        while (q++ < dashes) {
            x1 += dashX;
            y1 += dashY;
            ctx[q % 2 == 0 ? "moveTo" : "lineTo"](x1, y1);
        }
        ctx[q % 2 == 0 ? "moveTo" : "lineTo"](x2, y2);
    }

    private _drawSquarePercentFill(
        ctx,
        bounds,
        fillColor,
        fillDirection,
        fillPercentage
    ) {
        let FILL_TOP_TO_BOTTOM = 0;
        let FILL_BOTTOM_TO_TOP = 1;
        let FILL_RIGHT_TO_LEFT = 2;
        let FILL_LEFT_TO_RIGHT = 3;

        if (fillDirection == FILL_TOP_TO_BOTTOM) {
            bounds.h *= fillPercentage / 100.0;
        } else if (fillDirection == FILL_BOTTOM_TO_TOP) {
            let oldh = bounds.h;
            bounds.h *= fillPercentage / 100.0;
            bounds.y += oldh - bounds.h;
        } else if (fillDirection == FILL_RIGHT_TO_LEFT) {
            let oldw = bounds.w;
            bounds.w *= fillPercentage / 100.0;
            bounds.x += oldw - bounds.w;
        } else if (fillDirection == FILL_LEFT_TO_RIGHT) {
            bounds.w *= fillPercentage / 100.0;
        }

        ctx.fillStyle = fillColor.color;
        ctx.fillRect(bounds.x, bounds.y, bounds.w, bounds.h);
    }

    private drawSelectedPolygon(
        disp,
        ctx,
        zoom: number,
        pan: PointI,
        drawMode: DrawModeE
    ) {
        let geom = DispPolygon.geom(disp);

        let selectionConfig =
            this.config.getSelectionDrawDetailsForDrawMode(drawMode);

        // DRAW THE SELECTED BOX
        let bounds = PeekCanvasBounds.fromGeom(geom);

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

    private drawSelectedPolyline(
        disp,
        ctx,
        zoom: number,
        pan: PointI,
        drawMode: DrawModeE
    ) {
        let geom = DispPolygon.geom(disp);

        // This is in the too hard basket for now.
        if (geom.length > 4)
            return this.drawSelectedPolygon(disp, ctx, zoom, pan, drawMode);

        let selectionConfig =
            this.config.getSelectionDrawDetailsForDrawMode(drawMode);

        // Move the selection line a bit away from the object
        let offset = (selectionConfig.width + selectionConfig.lineGap) / zoom;

        // the line segment
        let x1 = geom[0],
            y1 = geom[1],
            x2 = geom[2],
            y2 = geom[3];

        let adj = x1 - x2;
        let opp = y1 - y2;
        let hypot = Math.hypot(adj, opp);

        let multiplier = offset / hypot;

        // Move the line ends a bit further our
        // x1 = x1 + adj * multiplier;
        // y1 = y1 + opp * multiplier;
        // x2 = x2 - adj * multiplier;
        // y2 = y2 - opp * multiplier;

        let px = y1 - y2; // as vector at 90 deg to the line
        let py = x2 - x1;
        const len = offset / Math.hypot(px, py);
        px *= len; // make leng 10 pixels
        py *= len;

        // draw line the start cap and end cap.
        ctx.beginPath();

        // this._drawLine(ctx, x1 + px, y1 + py,
        //     x1 - px, y1 - py,
        //     [selectionConfig.dashLen], zoom, 0);

        this._drawLine(
            ctx,
            x2 - px,
            y2 - py,
            x1 - px,
            y1 - py,
            [selectionConfig.dashLen],
            zoom,
            0
        );

        // this._drawLine(ctx, x2 + px, y2 + py,
        //     x2 - px, y2 - py,
        //     [selectionConfig.dashLen], zoom, 0);

        this._drawLine(
            ctx,
            x1 + px,
            y1 + py,
            x2 + px,
            y2 + py,
            [selectionConfig.dashLen],
            zoom,
            0
        );

        ctx.strokeStyle = selectionConfig.color;
        ctx.lineWidth = selectionConfig.width / zoom;
        ctx.stroke();
    }

    private drawPolyLineEnd(
        ctx,
        lineWidth: number,
        lineColor,
        fromX: number,
        fromY: number,
        toX: number,
        toY: number,
        endType: DispPolylineEndTypeE
    ): void {
        if (
            endType == DispPolylineEndTypeE.None ||
            lineColor == null ||
            !lineWidth
        )
            return;

        if (endType == DispPolylineEndTypeE.Dot) {
            let size = lineWidth * 3;
            ctx.beginPath();
            ctx.arc(toX, toY, size, 0, 2 * Math.PI);
            ctx.fillStyle = lineColor.color;
            ctx.fill();
            return;
        }

        if (endType == DispPolylineEndTypeE.Arrow) {
            let radians = Math.atan((fromY - toY) / (fromX - toX));
            radians += ((fromX >= toX ? -90 : 90) * Math.PI) / 180;

            let halfWidth = lineWidth * 3;
            let length = lineWidth * 12;

            ctx.save();
            ctx.translate(toX, toY);
            ctx.rotate(radians);

            ctx.beginPath();
            ctx.moveTo(0, 0);
            ctx.lineTo(halfWidth, length);
            ctx.lineTo(-halfWidth, length);
            ctx.closePath();

            ctx.fillStyle = lineColor.color;
            ctx.fill();

            ctx.restore();
            return;
        }

        throw new Error(`Unhandled line ending: ${endType}`);
    }
}
