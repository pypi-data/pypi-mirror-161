import { takeUntil } from "rxjs/operators";
import { Component } from "@angular/core";
import {
    PrivateDiagramGridLoaderServiceA,
    PrivateDiagramGridLoaderStatusTuple,
} from "@peek/peek_plugin_diagram/_private/grid-loader";
import {
    PrivateDiagramLocationLoaderService,
    PrivateDiagramLocationLoaderStatusTuple,
} from "@peek/peek_plugin_diagram/_private/location-loader";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { PrivateDiagramTupleService } from "@peek/peek_plugin_diagram/_private/services";

@Component({
    selector: "peek-plugin-diagram-cfg",
    templateUrl: "diagram-cfg.component.web.html",
})
export class DiagramCfgComponent extends NgLifeCycleEvents {
    gridLoaderStatus: PrivateDiagramGridLoaderStatusTuple =
        new PrivateDiagramGridLoaderStatusTuple();
    locationLoaderStatus: PrivateDiagramLocationLoaderStatusTuple =
        new PrivateDiagramLocationLoaderStatusTuple();

    constructor(
        private gridLoader: PrivateDiagramGridLoaderServiceA,
        private locationLoader: PrivateDiagramLocationLoaderService,
        private tupleService: PrivateDiagramTupleService
    ) {
        super();

        this.gridLoaderStatus = this.gridLoader.status();
        this.gridLoader
            .statusObservable()
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((value) => (this.gridLoaderStatus = value));

        this.locationLoaderStatus = this.locationLoader.status();
        this.locationLoader
            .statusObservable()
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((value) => (this.locationLoaderStatus = value));
    }
}
