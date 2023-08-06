import { Component, Input, OnInit } from "@angular/core";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import {
    DiagramPositionByCoordSetI,
    DiagramPositionByKeyI,
    DiagramPositionI,
    PrivateDiagramPositionService,
} from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramPositionService";
import { takeUntil } from "rxjs/operators";
import { PrivateDiagramCoordSetService } from "@peek/peek_plugin_diagram/_private/services";
import { PeekCanvasConfig } from "../canvas/PeekCanvasConfig.web";
import { PrivateDiagramBranchService } from "@peek/peek_plugin_diagram/_private/branch";
import { PeekCanvasModel } from "../canvas/PeekCanvasModel.web";
import { ModelCoordSet } from "@peek/peek_plugin_diagram/_private/tuples";
import { OptionalPositionArgsI } from "@peek/peek_plugin_diagram/DiagramPositionService";
import { DispKeyLocationTuple } from "@peek/peek_plugin_diagram/_private/location-loader/DispKeyLocationTuple";
import { PrivateDiagramLocationLoaderService } from "@peek/peek_plugin_diagram/_private/location-loader";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";

interface PositionToSelectI {
    position: DispKeyLocationTuple;
    coordSet: ModelCoordSet;
    opts: OptionalPositionArgsI;
}

@Component({
    selector: "pl-diagram-set-position",
    templateUrl: "set-position.component.html",
    styleUrls: ["set-position.component.scss"],
})
export class SetPositionComponent extends NgLifeCycleEvents implements OnInit {
    @Input("modelSetKey")
    modelSetKey: string;

    @Input("isReadyCallable")
    isReadyCallable: any;

    @Input("config")
    config: PeekCanvasConfig;

    @Input("model")
    model: PeekCanvasModel;

    private _isVisible: boolean = false;

    positions: PositionToSelectI[] = [];

    constructor(
        private balloonMsg: BalloonMsgService,
        private privatePosService: PrivateDiagramPositionService,
        private coordSetService: PrivateDiagramCoordSetService,
        private branchService: PrivateDiagramBranchService,
        private locationIndexService: PrivateDiagramLocationLoaderService
    ) {
        super();
    }

    ngOnInit() {
        // Watch the positionByCoordSet observable
        this.privatePosService
            .positionByCoordSetObservable()
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((data: DiagramPositionByCoordSetI) =>
                this.positionByCoordSet(data)
            );

        // Watch the position observables
        this.privatePosService
            .positionByKeyObservable()
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((pos: DiagramPositionByKeyI) => {
                this.positionByKey(
                    pos.modelSetKey,
                    pos.coordSetKey,
                    pos.opts,
                    pos.dispKeyIndexes
                ) //
                    .catch((e) => this.balloonMsg.showError(e));
            });

        // Watch the position observables
        this.privatePosService
            .positionObservable()
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((pos: DiagramPositionI) => this.positionByXY(pos));

        // Watch the select observables
        this.privatePosService
            .selectKeysObservable()
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((keys: string[]) => {
                this.model.selection.tryToSelectKeys(keys);
            });
    }

    private positionByCoordSet(data: DiagramPositionByCoordSetI) {
        this._isVisible = false;

        if (this.modelSetKey !== data.modelSetKey) {
            console.log(
                "ERROR, positionByCoordSet was called for " +
                    `modelSet ${data.modelSetKey} but we're showing` +
                    `modelSet ` +
                    this.modelSetKey
            );
            return;
        }

        if (!this.isReadyCallable()) {
            console.log("ERROR, Position was called before canvas is ready");
            return;
        }

        this.switchToCoordSet(data.coordSetKey);

        // Inform the position service that it's ready to go.
        this.privatePosService.setReady(true);
    }

    private positionByXY(pos: DiagramPositionI) {
        this._isVisible = false;

        // Switch only if we need to
        if (
            this.config.controller.coordSet == null ||
            this.config.controller.coordSet.key != pos.coordSetKey
        ) {
            this.switchToCoordSet(pos.coordSetKey);
        }

        this.config.updateViewPortPan({ x: pos.x, y: pos.y }); // pos confirms to PanI
        this.config.updateViewPortZoom(pos.zoom);

        if (pos.opts.highlightKey != null)
            this.model.selection.tryToSelectKeys([pos.opts.highlightKey]);

        if (pos.opts.editingBranch != null) {
            this.branchService.startEditing(
                this.modelSetKey,
                this.config.coordSet.key,
                pos.opts.editingBranch
            );
        }

        // Inform the position service that it's ready to go.
        this.privatePosService.setReady(true);
    }

    private switchToCoordSet(coordSetKey: string) {
        this._isVisible = false;

        if (!this.isReadyCallable()) return;

        const coordSet = this.coordSetService.coordSetForKey(
            this.modelSetKey,
            coordSetKey
        );
        this.config.updateCoordSet(coordSet);

        this.privatePosService.setTitle(`Viewing ${coordSet.name}`);

        // Update
        this.config.updateCoordSet(coordSet);
    }

    async positionByKey(
        modelSetKey: string,
        coordSetKey: string | null,
        opts: OptionalPositionArgsI = {},
        dispKeyIndexes: DispKeyLocationTuple[] | null = null
    ): Promise<void> {
        if (!this.coordSetService.isReady()) {
            throw new Error(
                "positionByKey called before coordSetService is ready"
            );
        }

        if (opts.highlightKey == null || opts.highlightKey.length == 0) {
            throw new Error("positionByKey must be passed opts.highlightKey");
        }

        if (dispKeyIndexes == null) {
            dispKeyIndexes = await this.locationIndexService.getLocations(
                modelSetKey,
                opts.highlightKey
            );
        }

        if (dispKeyIndexes.length == 0) {
            this.balloonMsg.showError(
                `Can not locate display item ${opts.highlightKey}` +
                    ` in model set ${modelSetKey}`
            );
        }

        this.positions = [];

        for (let dispKeyIndex of dispKeyIndexes) {
            const coordSet = this.coordSetService.coordSetForKey(
                modelSetKey,
                dispKeyIndex.coordSetKey
            );

            if (coordSet == null) {
                throw new Error(
                    "Could not find coordSet for key=" +
                        dispKeyIndex.coordSetKey
                );
            }

            this.positions.push({
                position: dispKeyIndex,
                coordSet: coordSet,
                opts: opts,
            });
        }

        this._isVisible = true;
    }

    get isVisible(): boolean {
        return this._isVisible && (this.positions?.length || 0) !== 0;
    }

    set isVisible(value: boolean) {
        this._isVisible = false;
    }

    handlePositionSelected(selection: PositionToSelectI): void {
        this.positionByXY({
            coordSetKey: selection.coordSet.key,
            x: selection.position.x,
            y: selection.position.y,
            zoom: selection.coordSet.positionOnZoom,
            opts: selection.opts,
        });
        this._isVisible = false;
    }
}
