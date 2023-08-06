import {
    CanvasInputPos,
    InputDelegateConstructorViewArgs,
    PeekCanvasInputDelegate,
} from "./PeekCanvasInputDelegate.web";
import { EditorToolType } from "../canvas/PeekCanvasEditorToolType.web";
import { DispPoly } from "../canvas-shapes/DispPoly";
import { DispBaseT, DispHandleTypeE, PointI } from "../canvas-shapes/DispBase";
import { DispPolygon } from "../canvas-shapes/DispPolygon";
import {
    DispPolyline,
    DispPolylineEndTypeE,
} from "../canvas-shapes/DispPolyline";
import { DrawModeE } from "../canvas-render/PeekDispRenderDelegateABC.web";
import { PeekCanvasBounds } from "../canvas/PeekCanvasBounds";
import { InputDelegateConstructorEditArgs } from "./PeekCanvasInputDelegateUtil.web";

/**
 * This input delegate handles :
 * Zooming (touch and mouse)
 * Panning (touch and mouse)
 * Selecting at a point (touch and mouse)
 *
 */
export class PeekCanvasInputEditMakeDispPolyDelegate extends PeekCanvasInputDelegate {
    // Stores the rectangle being created
    protected _creating = null;

    // Used to detect dragging and its the mouse position we use
    protected _startMousePos: CanvasInputPos | null = null;
    protected _startNodeDisp = null;
    protected _endNodeDisp = null;

    protected _nodes = []; //canvasInput._scope.pageData.modelRenderables;

    constructor(
        viewArgs: InputDelegateConstructorViewArgs,
        editArgs: InputDelegateConstructorEditArgs,
        tool: EditorToolType
    ) {
        super(viewArgs, editArgs, tool);

        this.viewArgs.model.selection.clearSelection();
        this._reset();
    }

    _reset() {
        this._creating = null;
        this._startNodeDisp = null;
        this._endNodeDisp = null;

        // See mousedown and mousemove events for explanation
        this._startMousePos = null;
        this._lastMousePos = new CanvasInputPos();
    }

    keyUp(event) {
        if (!this._creating) return;

        // Cancel creating object
        if (
            event.keyCode == 46 || // delete
            event.keyCode == 27
        ) {
            // escape
            this._reset();
            return;
        }

        if (event.keyCode == 8) {
            // Backspace
            // We want to keep at least two points at all times
            if (DispPoly.pointCount(this._creating) < 3) return;
            // Remove last point
            DispPoly.popPoint(this._creating);
            this.viewArgs.config.invalidate();
            return;
        }

        if (event.keyCode == 13) {
            // Enter
            this._finaliseCreate();
            return;
        }
    }

    // Map mouse events
    mouseDown(event: MouseEvent, inputPos: CanvasInputPos) {
        this.inputStart(inputPos);
    }

    // ---------------

    mouseMove(event: MouseEvent, inputPos: CanvasInputPos) {
        this.inputMove(inputPos);
    }

    mouseUp(event: MouseEvent, inputPos: CanvasInputPos) {
        if (event.button == 2) {
            this._finaliseCreate();
            return;
        }
        this.inputEnd(inputPos, event.shiftKey);
    }

    mouseDoubleClick(event: MouseEvent, inputPos: CanvasInputPos) {
        // The double click will cause two "MouseUp" events
        DispPoly.popPoint(this._creating);
        DispPoly.popPoint(this._creating);
        this._finaliseCreate();
    }

    // Map touch events
    touchStart(event: TouchEvent, inputPos: CanvasInputPos) {
        if (event.touches.length == 2) {
            this._finaliseCreate();
            return;
        }

        this.inputStart(inputPos);
    }

    // ---------------

    touchMove(event: TouchEvent, inputPos: CanvasInputPos) {
        this.inputMove(inputPos);
    }

    touchEnd(event: TouchEvent, inputPos: CanvasInputPos) {
        this.inputEnd(inputPos);
    }

    delegateWillBeTornDown() {
        //this._finaliseCreate();
    }

    // ---------------

    draw(ctx, zoom: number, pan: PointI, drawMode: DrawModeE) {}

    protected createDisp(inputPos: CanvasInputPos) {
        // Create the Disp
        if (this.NAME == EditorToolType.EDIT_MAKE_POLYGON)
            this._creating = DispPolygon.create(this.viewArgs.config.coordSet);
        else
            this._creating = DispPolyline.create(this.viewArgs.config.coordSet);

        if (this.NAME == EditorToolType.EDIT_MAKE_LINE_WITH_ARROW)
            DispPolyline.setEndEndType(
                this._creating,
                DispPolylineEndTypeE.Arrow
            );

        DispPoly.addPoint(this._creating, this._startMousePos);
        this._setLastMousePos(this._startMousePos);

        DispPoly.addPoint(this._creating, inputPos);

        // Link the Disp
        this.editArgs.lookupService._linkDispLookups(this._creating);

        // Add the shape to the branch
        this._creating =
            this.editArgs.branchContext.branchTuple.addOrUpdateDisp(
                this._creating,
                true
            );

        // TODO, Snap the coordinates if required
        // if (this.viewArgs.config.editor.snapToGrid)
        //     DispText.snap(this._creating, this.viewArgs.config.editor.snapSize);

        // Let the canvas editor know something has happened.
        // this.editArgs.dispPropsUpdated();

        this.viewArgs.model.recompileModel();

        this.viewArgs.model.selection.replaceSelection(this._creating);

        this._addBranchAnchor(inputPos.x, inputPos.y);
    }

    private _nodeDispClickedOn(point: PointI): DispBaseT | null {
        for (let i = this._nodes.length - 1; 0 <= i; i--) {
            let disp = this._nodes[i];
            if (disp.bounds != null && disp.bounds.contains(point.x, point.y)) {
                return disp;
            }
        }

        return null;
    }

    // Start logic
    private inputStart(inputPos: CanvasInputPos) {
        /*
         if (this._startNodeDisp) {
         this._startMousePos = inputPos;
         return;
         }
         
         
         this._startNodeDisp = this._nodeDispClickedOn(inputPos);
         
         if (!this._startNodeDisp) {
         this.editArgs.balloonMsg.showWarning("A conductor must start on a node");
         this._reset();
         // this.canvasInput._scope.pageMethods.cableCreateCallback();
         return;
         }
         */
        this._lastMousePos = inputPos;
        if (!this._creating) {
            this._startMousePos = inputPos;
            this.createDisp(inputPos);
        }
    }

    private inputMove(inputPos: CanvasInputPos) {
        if (this._startMousePos == null) return;

        const handleBounds = new PeekCanvasBounds(inputPos.x, inputPos.y, 0, 0);
        const delta = this._setLastMousePos(inputPos);
        DispPoly.deltaMoveHandle(
            {
                disp: this._creating,
                center: handleBounds.center(),
                box: handleBounds,
                handleType: DispHandleTypeE.movePoint,
                handleIndex: DispPoly.pointCount(this._creating) - 1,
            },
            delta.dx,
            delta.dy
        );
        this.viewArgs.config.invalidate();
    }

    private inputEnd(inputPos: CanvasInputPos, shiftKey: boolean = false) {
        if (!this._startMousePos) return;

        if (!this._hasPassedDragThreshold(this._startMousePos, inputPos))
            return;

        if (
            this.NAME == EditorToolType.EDIT_MAKE_LINE_WITH_ARROW &&
            DispPoly.pointCount(this._creating) == 2
        ) {
            this._finaliseCreate();
        } else {
            let point = this._coord(this._lastMousePos, shiftKey);
            DispPoly.addPoint(this._creating, point);
        }

        this.viewArgs.config.invalidate();
    }

    private _finaliseCreate() {
        if (this._creating == null) return;

        let poly = this._creating;
        let startNodeDisp = this._startNodeDisp;
        let endNodeDisp = null;

        this._reset();

        if (poly) {
            let lastPointCoord = DispPoly.lastPoint(poly);
            endNodeDisp = this._nodeDispClickedOn(lastPointCoord);
        }

        if (!endNodeDisp) {
            // this.editArgs.balloonMsg.showWarning("A conductor must end on a node");
            poly = null;
        }

        // this.canvasInput._scope.pageMethods.cableCreateCallback(poly, startNodeDisp, endNodeDisp);

        this.editArgs.branchContext.branchTuple.touchUpdateDate(true);
        this.editArgs.branchContext.branchTuple.touchUndo();
        this.viewArgs.config.invalidate();
        this.editArgs.setEditorSelectTool();
    }

    private _coord(mouse: CanvasInputPos, shiftKey: boolean = false): PointI {
        let point = { x: mouse.x, y: mouse.y };

        // When the shift key is pressed, we will align to x or y axis
        if (this._creating != null && shiftKey) {
            let lastPoint = DispPoly.lastPoint(this._creating);
            let dx = Math.abs(point.x - lastPoint.x);
            let dy = Math.abs(point.y - lastPoint.y);

            if (dx > dy) point.y = lastPoint.y;
            else point.x = lastPoint.x;
        }

        // return
        return point;
    }
}
