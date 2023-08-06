import { takeUntil } from "rxjs/operators";
import { PeekCanvasConfig } from "../canvas/PeekCanvasConfig.web";
import { PeekCanvasModel } from "../canvas/PeekCanvasModel.web";

import * as $ from "jquery";
import { PeekDispRenderFactory } from "../canvas-render/PeekDispRenderFactory.web";
import { PeekCanvasInputDelegate } from "./PeekCanvasInputDelegate.web";
import {
    CanvasInputPos,
    disableContextMenu,
    InputDelegateConstructorEditArgs,
    InputDelegateConstructorViewArgs,
} from "./PeekCanvasInputDelegateUtil.web";
import { PeekCanvasInputSelectDelegate } from "./PeekCanvasInputSelectDelegate.web";
import { EditorToolType } from "../canvas/PeekCanvasEditorToolType.web";
import { PointI } from "../canvas-shapes/DispBase";
import { DrawModeE } from "../canvas-render/PeekDispRenderDelegateABC.web";
import { PeekCanvasActioner } from "../canvas/PeekCanvasActioner";
import { CopyPasteService } from "../services/copy-paste.service";
import { ContextMenuService } from "../services/context-menu.service";

/** Peek Canvas Input
 *
 * This class manages the user input of the canvas
 *
 */
export class PeekCanvasInput {
    private _delegate: PeekCanvasInputDelegate = null;

    private canvas = null;

    // These offsets are calculated on the size and position of the canvas in the HTML
    // page. When added to the mouse event coordinates, they convert the mouse event
    // coordinates to be relative to the center of the canvas.
    private mouseOffsetX: number = 0;
    private mouseOffsetY: number = 0;

    constructor(
        private config: PeekCanvasConfig,
        private model: PeekCanvasModel,
        private renderFactory: PeekDispRenderFactory,
        private lifecycleEventEmitter,
        private objectPopupService,
        private copyPasteService: CopyPasteService,
        private contextMenuService: ContextMenuService,
        private actioner: PeekCanvasActioner
    ) {
        this.delegateFinished();
    }

    setDelegate(
        Delegate,
        editArgs: InputDelegateConstructorEditArgs | null = null
    ) {
        if (this._delegate) this._delegate.shutdown();

        let viewDelegateArgs: InputDelegateConstructorViewArgs = {
            input: this,
            config: this.config,
            model: this.model,
            renderFactory: this.renderFactory,
            objectPopupService: this.objectPopupService,
            copyPasteService: this.copyPasteService,
            contextMenuService: this.contextMenuService,
            actioner: this.actioner,
        };

        this._delegate = new Delegate(viewDelegateArgs, editArgs);

        this.config.mouse.currentDelegateName = Delegate.TOOL_NAME;

        // console.log(`Delegate = ${Delegate.TOOL_NAME}`);
    }

    delegateFinished() {
        // let PeekCanvasInputSelectDelegate =
        //     require("PeekCanvasInputSelectDelegate")["PeekCanvasInputSelectDelegate"];
        this.setDelegate(PeekCanvasInputSelectDelegate);
    }

    selectedDelegateType(): EditorToolType {
        return this.config.mouse.currentDelegateName;
    }

    selectedDelegate(): PeekCanvasInputDelegate {
        return this._delegate;
    }

    // Creates an object with x and y defined, set to the mouse position relative to
    // the state's canvas
    // If you want to be super-correct this can be tricky, we have to worry about
    // padding and borders
    _getMouse(e): CanvasInputPos {
        let pageX = e.pageX;
        let pageY = e.pageY;

        if (pageX == null) {
            if (e.changedTouches != null && e.changedTouches.length >= 0) {
                let touch = e.changedTouches[0];
                pageX = touch.pageX;
                pageY = touch.pageY;
            } else {
                console.log("ERROR: Failed to determine pan coordinates");
            }
        }

        let mx = pageX - this.mouseOffsetX;
        let my = pageY - this.mouseOffsetY;

        let clientX = mx;
        let clientY = my;

        // Apply canvas scale and pan
        let zoom = this.config.viewPort.zoom;
        let pan = this.config.viewPort.pan;
        mx = mx / zoom + pan.x;
        my = my / zoom + pan.y;

        if (isNaN(mx)) console.log("mx IS NaN");

        this.config.mouse.currentViewPortPosition = { x: mx, y: my };
        this.config.mouse.currentCanvasPosition = { x: clientX, y: clientY };

        // We return a simple javascript object (a hash) with x and y defined
        return {
            x: mx,
            y: my,
            clientX: clientX,
            clientY: clientY,
            time: new Date(),
        };
    }

    setCanvas(canvas) {
        this.canvas = canvas;

        canvas.addEventListener(
            "keydown",
            (e) => {
                this._delegate.keyDown(e);
            },
            true
        );

        canvas.addEventListener(
            "keypress",
            (e) => {
                this._delegate.keyPress(e);
            },
            true
        );

        canvas.addEventListener(
            "keyup",
            (e) => {
                this._delegate.keyUp(e);
            },
            true
        );

        canvas.addEventListener(
            "mousedown",
            (e) => {
                if (!(e instanceof MouseEvent)) return;
                this._delegate.mouseDown(e, this._getMouse(e));
            },
            true
        );

        canvas.addEventListener(
            "mousemove",
            (e) => {
                if (!(e instanceof MouseEvent)) return;
                this._delegate.mouseMove(e, this._getMouse(e));
            },
            true
        );

        canvas.addEventListener(
            "mouseup",
            (e) => {
                if (!(e instanceof MouseEvent)) return;
                this._delegate.mouseUp(e, this._getMouse(e));
            },
            true
        );

        canvas.addEventListener(
            "dblclick",
            (e) => {
                if (!(e instanceof MouseEvent)) return;
                this._delegate.mouseDoubleClick(e, this._getMouse(e));
            },
            true
        );

        canvas.addEventListener(
            "mousewheel",
            (e) => {
                if (!(e instanceof MouseEvent)) return;
                this._delegate.mouseWheel(e, this._getMouse(e));

                e.preventDefault();
                return false;
            },
            true
        );

        canvas.addEventListener(
            "touchstart",
            (e) => {
                if (!(e instanceof TouchEvent)) return;
                this._delegate.touchStart(e, this._getMouse(e));
                disableContextMenu(e);
            },
            true
        );

        canvas.addEventListener(
            "touchmove",
            (e) => {
                if (!(e instanceof TouchEvent)) return;
                this._delegate.touchMove(e, this._getMouse(e));
                disableContextMenu(e);
            },
            true
        );

        canvas.addEventListener(
            "touchend",
            (e) => {
                if (!(e instanceof TouchEvent)) return;
                this._delegate.touchEnd(e, this._getMouse(e));
                disableContextMenu(e);
            },
            true
        );

        canvas.addEventListener(
            "selectstart",
            (e) => {
                //this_._delegate.mouseSelectStart(e, this_._getMouse(e));
                e.preventDefault();
                return false;
            },
            true
        );

        canvas.addEventListener("contextmenu", disableContextMenu, true);

        this.config.canvas.windowChange
            .pipe(takeUntil(this.lifecycleEventEmitter.onDestroyEvent))
            .subscribe(() => this.updateCanvasSize());
    }

    /**
     * Draw Called by the renderer during a redraw.
     */
    draw(ctx, zoom: number, pan: PointI, drawMode: DrawModeE) {
        if (this._delegate) this._delegate.draw(ctx, zoom, pan, drawMode);
    }

    private updateCanvasSize() {
        let jqCanvas = $(this.canvas);
        let element: any = this.canvas;

        let width = jqCanvas.width();
        let height = jqCanvas.height();

        // This complicates things a little but but fixes mouse co-ordinate
        // problems
        // when there's a border or padding. See getMouse for more detail
        let stylePaddingLeft = parseInt(jqCanvas.css("padding-left")) || 0;
        let stylePaddingTop = parseInt(jqCanvas.css("padding-top")) || 0;
        let styleBorderLeft = parseInt(jqCanvas.css("border-left-width")) || 0;
        let styleBorderTop = parseInt(jqCanvas.css("border-top-width")) || 0;

        // Some pages have fixed-position bars (like the stumbleupon bar) at the
        // top or left of the page
        // They will mess up mouse coordinates and this fixes that
        let html: any = document.body.parentNode;
        let htmlTop = html.offsetTop;
        let htmlLeft = html.offsetLeft;

        this.mouseOffsetX = 0;
        this.mouseOffsetY = 0;

        // Compute the total offset
        if (element.offsetParent != null) {
            do {
                this.mouseOffsetX += element.offsetLeft;
                this.mouseOffsetY += element.offsetTop;
            } while ((element = element.offsetParent));
        }

        // Add padding and border style widths to offset
        // Also add the <html> offsets in case there's a position:fixed bar
        this.mouseOffsetX +=
            stylePaddingLeft + styleBorderLeft + htmlLeft + width / 2;
        this.mouseOffsetY +=
            stylePaddingTop + styleBorderTop + htmlTop + height / 2;
    }
}
