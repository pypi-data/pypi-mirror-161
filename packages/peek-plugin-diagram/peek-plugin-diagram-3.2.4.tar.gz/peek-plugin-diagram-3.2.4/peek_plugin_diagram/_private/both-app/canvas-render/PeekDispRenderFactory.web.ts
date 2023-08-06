import { PeekDispRenderDelegatePoly } from "./PeekDispRenderDelegatePoly.web";
import { PeekDispRenderDelegateText } from "./PeekDispRenderDelegateText.web";
import { PeekDispRenderDelegateEllipse } from "./PeekDispRenderDelegateEllipse.web";
import { PeekDispRenderDelegateGroupPtr } from "./PeekDispRenderDelegateGroupPtr.web";
import { PeekCanvasConfig } from "../canvas/PeekCanvasConfig.web";
import {
    DispBase,
    DispHandleI,
    DispType,
    PointI,
} from "../canvas-shapes/DispBase";
import { PeekDispRenderDelegateNull } from "./PeekDispRenderDelegateNull.web";
import { DrawModeE } from "./PeekDispRenderDelegateABC.web";
import { PeekCanvasModel } from "../canvas/PeekCanvasModel.web";
import { DispGroupPointerT } from "../canvas-shapes/DispGroupPointer";
import { PeekDispRenderDelegateCurvedText } from "./PeekDispRenderDelegateCurvedText.web";

export class PeekDispRenderFactory {
    private _delegatesByType: {};

    constructor(
        private config: PeekCanvasConfig,
        private model: PeekCanvasModel
    ) {
        let polyDelegate = new PeekDispRenderDelegatePoly(config, model);
        let textDelegate = new PeekDispRenderDelegateText(config, model);
        let curvedTextDelegate = new PeekDispRenderDelegateCurvedText(
            config,
            model
        );
        let ellipseDelegate = new PeekDispRenderDelegateEllipse(config, model);
        let groupPtrDelegate = new PeekDispRenderDelegateGroupPtr(
            config,
            model
        );
        let nullDelegate = new PeekDispRenderDelegateNull(config, model);

        this._delegatesByType = {};
        this._delegatesByType[DispBase.TYPE_DT] = textDelegate;
        this._delegatesByType[DispBase.TYPE_DCT] = curvedTextDelegate;
        this._delegatesByType[DispBase.TYPE_DPG] = polyDelegate;
        this._delegatesByType[DispBase.TYPE_DPL] = polyDelegate;
        this._delegatesByType[DispBase.TYPE_DE] = ellipseDelegate;
        this._delegatesByType[DispBase.TYPE_DGP] = groupPtrDelegate;
        this._delegatesByType[DispBase.TYPE_DN] = nullDelegate;
    }

    draw(disp, ctx, zoom: number, pan: PointI, drawMode: DrawModeE) {
        let level = DispBase.level(disp);
        let layer = DispBase.layer(disp);

        let isVisible =
            level.isVisibleAtZoom(zoom) || this.config.editor.showAllLevels;

        isVisible =
            isVisible && (layer.visible || this.config.editor.showAllLayers);

        // Ignore everything not visible.
        if (drawMode == DrawModeE.ForView && !isVisible) return;

        let delegate = this._delegatesByType[disp._tt];
        if (delegate == null) {
            console.log(`ERROR: Unhandled render delegate for ${disp._tt}`);
            return;
        }

        // Draw only visible shapes
        if (isVisible) delegate.draw(disp, ctx, zoom, pan, drawMode);

        // Update the bounds of all shapes
        this.updateBounds(disp, delegate, zoom);

        // Show invisible objects
        if (drawMode == DrawModeE.ForEdit)
            this.drawInvisible(disp, ctx, zoom, pan);
    }

    drawSelected(disp, ctx, zoom: number, pan: PointI, drawMode: DrawModeE) {
        this._delegatesByType[disp._tt].drawSelected(
            disp,
            ctx,
            zoom,
            pan,
            drawMode
        );
    }

    drawEditHandles(disp, ctx, zoom: number, pan: PointI) {
        this._delegatesByType[disp._tt].drawEditHandles(disp, ctx, zoom, pan);
    }

    similarTo(disp, otherDispObj) {
        return false;
    }

    handles(disp): DispHandleI[] {
        return this._delegatesByType[disp._tt].handles(disp);
    }

    private updateBounds(disp, delegate, zoom): void {
        if (disp.bounds != null) return;

        delegate.updateBounds(disp, zoom);

        if (DispBase.typeOf(disp) != DispType.groupPointer) return;

        if ((<DispGroupPointerT>disp).disps == null) return;

        for (const childDisp of (<DispGroupPointerT>disp).disps) {
            const childDelegate = this._delegatesByType[disp._tt];
            this.updateBounds(childDisp, childDelegate, zoom);
            disp.bounds.increaseFromBounds(childDisp.bounds);
        }
    }

    private drawInvisible(disp, ctx, zoom: number, pan: PointI) {
        if (DispBase.groupId(disp) != null) return;

        if (DispBase.hasColor(disp)) return;

        if (!disp.bounds) return;

        if (DispBase.typeOf(disp) == DispType.null_) return;

        // DRAW THE invisible BOX
        let selectionConfig = this.config.renderer.invisible;

        let b = disp.bounds;

        ctx.dashedRect(b.x, b.y, b.w, b.h, selectionConfig.dashLen / zoom);
        ctx.strokeStyle = selectionConfig.color;
        ctx.lineWidth = selectionConfig.width / zoom;
        ctx.stroke();
    }
}
