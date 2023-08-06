import { takeUntil } from "rxjs/operators";
import { Component, Input, ViewChild } from "@angular/core";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { PeekCanvasConfig } from "../canvas/PeekCanvasConfig.web";
import { PeekDispRenderFactory } from "../canvas-render/PeekDispRenderFactory.web";
import { PeekCanvasRenderer } from "../canvas-render/PeekCanvasRenderer.web";
import { PeekCanvasInput } from "../canvas-input/PeekCanvasInput.web";
import { PeekCanvasModel } from "../canvas/PeekCanvasModel.web";
import { GridObservable } from "../cache/GridObservable.web";
import { PrivateDiagramLookupService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramLookupService";
import { PrivateDiagramConfigService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramConfigService";
import { DispBase, DispBaseT } from "../canvas-shapes/DispBase";
import { PeekCanvasBounds } from "../canvas/PeekCanvasBounds";
import { PositionUpdatedI } from "@peek/peek_plugin_diagram/DiagramPositionService";
import { DocDbPopupService } from "@peek/peek_core_docdb";
import { PrivateDiagramPositionService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramPositionService";
import { PrivateDiagramItemSelectService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramItemSelectService";
import { PrivateDiagramCoordSetService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramCoordSetService";
import { PeekCanvasEditor } from "../canvas/PeekCanvasEditor.web";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { PrivateDiagramBranchService } from "@peek/peek_plugin_diagram/_private/branch/PrivateDiagramBranchService";
import { PrivateDiagramSnapshotService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramSnapshotService";
import { PrivateDiagramOverrideService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramOverrideService";
import { PeekCanvasActioner } from "../canvas/PeekCanvasActioner";
import { CopyPasteService } from "../services/copy-paste.service";
import { ContextMenuService } from "../services/context-menu.service";
import { DiagramToolbarService } from "@peek/peek_plugin_diagram";
import { PrivateDiagramToolbarService } from "@peek/peek_plugin_diagram/_private/services";

/** Canvas Component
 *
 * This component ties in all the plain canvas TypeScript code with the Angular
 * services and the HTML <canvas> tag.
 */
@Component({
    selector: "pl-diagram-canvas",
    templateUrl: "canvas-component.web.html",
    styleUrls: ["canvas-component.web.scss"],
})
export class CanvasComponent extends NgLifeCycleEvents {
    @ViewChild("edittoolbar", { static: true }) editToolbarView;
    @ViewChild("canvas", { static: true }) canvasView;
    @ViewChild("editprops", { static: true }) editPropsView;

    @Input("modelSetKey")
    modelSetKey: string;

    showToolbar: boolean = true;

    config: PeekCanvasConfig;
    model: PeekCanvasModel;
    input: PeekCanvasInput;
    editor: PeekCanvasEditor;
    // This is toggled by the toolbars
    showPrintPopup = false;

    private canvas: any = null;
    // DoCheck last value variables
    private lastCanvasSize: string = "";
    private lastFrameSize: string = "";
    private renderer: PeekCanvasRenderer;
    private renderFactory: PeekDispRenderFactory;

    readonly isReadyCallable = () => this.isReady();

    protected privateToolbarService: PrivateDiagramToolbarService;

    constructor(
        private balloonMsg: BalloonMsgService,
        private gridObservable: GridObservable,
        private lookupService: PrivateDiagramLookupService,
        private coordSetCache: PrivateDiagramCoordSetService,
        private privatePosService: PrivateDiagramPositionService,
        private objectPopupService: DocDbPopupService,
        private itemSelectService: PrivateDiagramItemSelectService,
        private configService: PrivateDiagramConfigService,
        private branchService: PrivateDiagramBranchService,
        private overrideService: PrivateDiagramOverrideService,
        private snapshotService: PrivateDiagramSnapshotService,
        private copyPasteService: CopyPasteService,
        private contextMenuService: ContextMenuService,
        private toolbarService: DiagramToolbarService
    ) {
        super();

        // The config for the canvas
        this.config = new PeekCanvasConfig();
        this.privateToolbarService = <PrivateDiagramToolbarService>(
            toolbarService
        );
    }

    isEditing(): boolean {
        return this.editor != null && this.editor.isEditing();
    }

    isReady(): boolean {
        return (
            this.coordSetCache.isReady() &&
            this.gridObservable.isReady() &&
            this.lookupService != null
        );
    }

    get coordSetKey(): string | null {
        return this.config.controller.coordSet?.key;
    }

    ngOnInit() {
        this.initCanvas();

        this.canvas = this.canvasView.nativeElement;

        this.input.setCanvas(this.canvas);
        this.renderer.setCanvas(this.canvas);

        document.body.style.overflow = "hidden";

        // NOTE: If you're debugging diagram flickering, it might help to remove this.
        this.canvas.style.backgroundColor =
            this.config.renderer.backgroundColor;

        // Update the canvas height
        this.doCheckEvent.pipe(takeUntil(this.onDestroyEvent)).subscribe(() => {
            let frameSize = window.innerHeight.toString();

            let titleBarHeight = document.getElementsByClassName(
                "peek-header-component"
            )?.[0]?.clientHeight;

            frameSize += `;${titleBarHeight}`;

            if (this.lastFrameSize == frameSize) {
                return;
            }

            this.lastFrameSize = frameSize;

            let newHeight = window.innerHeight;

            if (titleBarHeight != null) {
                newHeight -= titleBarHeight;
            }

            this.canvas.style.height = `${newHeight}px`;
            this.config.invalidate();
        });

        // Watch the canvas window size
        this.doCheckEvent.pipe(takeUntil(this.onDestroyEvent)).subscribe(() => {
            const offset = {
                left: this.canvas.getBoundingClientRect().left,
                top: this.canvas.getBoundingClientRect().top,
            };
            const bounds = new PeekCanvasBounds(
                offset.left,
                offset.top,
                window.innerWidth,
                window.innerHeight
            );
            const thisCanvasSize = bounds.toString();

            if (this.lastCanvasSize == thisCanvasSize) {
                return;
            }

            this.lastCanvasSize = thisCanvasSize;

            this.canvas.height = this.canvas.clientHeight;
            this.canvas.width = this.canvas.clientWidth;

            this.config.updateCanvasWindow(bounds);
        });
    }

    mouseInfo(): string {
        let x = this.config.mouse.currentViewPortPosition.x.toFixed(2);
        let y = this.config.mouse.currentViewPortPosition.y.toFixed(2);
        let zoom = this.config.viewPort.zoom.toFixed(2);
        return `${x}x${y}X${zoom}, ${this.config.model.dispOnScreen} Items`;
    }

    coordSetIsValid(): boolean {
        return this.config.coordSet?.key != null;
    }

    connectSnapshotCallback(): void {
        this.snapshotService.setImageCaptureCallback(() => {
            return this.canvas.toDataURL();
        });

        this.onDestroyEvent.subscribe(() =>
            this.snapshotService.setImageCaptureCallback(null)
        );
    }

    connectPositionUpdateNotify(): void {
        let notify = () => {
            if (this.config.controller.coordSet == null) return;

            let editingBranch = null;
            if (this.config.editor.active)
                editingBranch = this.editor.branchContext.branchTuple.key;

            let data: PositionUpdatedI = {
                coordSetKey: this.config.controller.coordSet.key,
                x: this.config.viewPort.pan.x,
                y: this.config.viewPort.pan.y,
                zoom: this.config.viewPort.zoom,
                editingBranch: editingBranch,
            };

            this.privatePosService.positionUpdated(data);
        };

        this.config.viewPort.panChange
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe(notify);

        this.config.viewPort.zoomChange
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe(notify);

        this.config.controller.coordSetChange
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe(notify);

        this.config.editor.branchKeyChange
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe(notify);
    }

    connectCopyPasteService(): void {
        this.copyPasteService.setModel(this.model);
        this.copyPasteService.setConfig(this.config);
        this.copyPasteService.setEditor(this.editor);
    }

    connectItemSelectionService(): void {
        this.model.selection
            .selectionChangedObservable()
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((disps: DispBaseT[]) => {
                const items = [];
                for (const disp of disps) {
                    items.push({
                        modelSetKey: this.modelSetKey,
                        coordSetKey: this.config.controller.coordSet.key,
                        dispKey: DispBase.key(disps[0]),
                        dispData: DispBase.data(disps[0]),
                    });
                }

                this.itemSelectService.selectItems(items);
            });
    }

    private initCanvas(): void {
        // this.lookupService must not be null
        this.config.controller.modelSetKey = this.modelSetKey;

        // If the coord set ischanged, update our value

        // The model view the viewable items on the canvas
        this.model = new PeekCanvasModel(
            this.config,
            this.gridObservable,
            this.lookupService,
            this.branchService,
            this.overrideService,
            this
        );

        // The display renderer delegates
        this.renderFactory = new PeekDispRenderFactory(this.config, this.model);

        const actioner = new PeekCanvasActioner(
            this.modelSetKey,
            this.coordSetCache,
            this.lookupService,
            this.privatePosService
        );

        // The user interaction handler.
        this.input = new PeekCanvasInput(
            this.config,
            this.model,
            this.renderFactory,
            this,
            this.objectPopupService,
            this.copyPasteService,
            this.contextMenuService,
            actioner
        );

        // The canvas renderer
        this.renderer = new PeekCanvasRenderer(
            this.config,
            this.model,
            this.renderFactory,
            this
        );

        // The canvas renderer
        this.editor = new PeekCanvasEditor(
            this.balloonMsg,
            this.input,
            this.model,
            this.config,
            this.gridObservable,
            this.lookupService,
            this.privatePosService,
            this.branchService,
            this
        );

        // Add the mouse class to the renderers draw list
        this.renderer.drawEvent
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe(({ ctx, zoom, pan, drawMode }) =>
                this.input.draw(ctx, zoom, pan, drawMode)
            );

        // Hook up the item selection service
        this.connectItemSelectionService();

        // Hook up the config service
        this.connectConfigService();

        // Hook up the position serivce
        // SEE SetPositionComponent

        // Hook up the outward notification of position updates
        this.connectPositionUpdateNotify();

        // Hook up the Snapshot service
        this.connectSnapshotCallback();

        // Hook up the Copy and Paste service
        this.connectCopyPasteService();

        this.connectToolbarService();
    }

    private connectConfigService(): void {
        this.configService
            .usePolylineEdgeColorsObservable()
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((enabled: boolean) => {
                this.config.renderer.useEdgeColors = enabled;
                this.config.invalidate();
            });

        this.configService
            .layersUpdatedObservable()
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe(() => this.model.recompileModel());
    }

    private connectToolbarService(): void {
        this.privateToolbarService
            .showToolbarObservable()
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((enabled: boolean) => {
                this.showToolbar = enabled;
            });
    }
}
