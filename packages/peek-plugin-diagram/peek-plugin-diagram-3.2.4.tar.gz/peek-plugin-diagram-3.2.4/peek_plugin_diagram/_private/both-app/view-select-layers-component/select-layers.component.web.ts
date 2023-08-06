import { takeUntil } from "rxjs/operators";
import { Component, Input, OnInit } from "@angular/core";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { HeaderService } from "@synerty/peek-plugin-base-js";

import {
    PopupLayerSelectionArgsI,
    PrivateDiagramConfigService,
} from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramConfigService";
import { PrivateDiagramLookupService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramLookupService";
import { DiagramCoordSetService } from "@peek/peek_plugin_diagram/DiagramCoordSetService";
import { DispLayer } from "@peek/peek_plugin_diagram/lookups";

import { PrivateDiagramCoordSetService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramCoordSetService";
import { PeekCanvasConfig } from "../canvas/PeekCanvasConfig.web";
import { PeekCanvasModel } from "../canvas/PeekCanvasModel.web";

@Component({
    selector: "pl-diagram-view-select-layers",
    templateUrl: "select-layers.component.web.html",
    styleUrls: ["select-layers.component.web.scss"],
})
export class SelectLayersComponent extends NgLifeCycleEvents implements OnInit {
    popupShown: boolean = false;

    @Input("coordSetKey")
    coordSetKey: string;

    @Input("modelSetKey")
    modelSetKey: string;

    @Input("model")
    model: PeekCanvasModel;

    @Input("config")
    config: PeekCanvasConfig;
    items: DispLayer[] = [];
    private coordSetService: PrivateDiagramCoordSetService;

    constructor(
        private headerService: HeaderService,
        private lookupService: PrivateDiagramLookupService,
        private configService: PrivateDiagramConfigService,
        abstractCoordSetService: DiagramCoordSetService
    ) {
        super();

        this.coordSetService = <PrivateDiagramCoordSetService>(
            abstractCoordSetService
        );

        this.configService
            .popupLayerSelectionObservable()
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((v: PopupLayerSelectionArgsI) => this.openPopup(v));
    }

    ngOnInit() {}

    closePopup(): void {
        this.popupShown = false;
        this.items = [];
    }

    noItems(): boolean {
        return this.items.length == 0;
    }

    toggleLayerVisible(layer: DispLayer): void {
        layer.visible = !layer.visible;
        if (this.model != null) this.model.recompileModel();
    }

    protected openPopup({ coordSetKey, modelSetKey }) {
        let coordSet = this.coordSetService.coordSetForKey(
            modelSetKey,
            coordSetKey
        );
        console.log("Opening Layer Select popup");

        this.items = this.lookupService.layersOrderedByOrder(
            coordSet.modelSetId
        );
        this.items.sort((a, b) =>
            a.name == b.name ? 0 : a.name < b.name ? -1 : 1
        );

        this.popupShown = true;
    }
}
