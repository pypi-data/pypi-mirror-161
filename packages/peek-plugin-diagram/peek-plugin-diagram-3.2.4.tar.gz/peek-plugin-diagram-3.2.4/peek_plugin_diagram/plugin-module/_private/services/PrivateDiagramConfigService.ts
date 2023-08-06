import { Injectable } from "@angular/core";
import { Observable, Subject } from "rxjs";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { PrivateDiagramLookupService } from "./PrivateDiagramLookupService";
import { DiagramConfigService } from "../../DiagramConfigService";
import { DiagramToolbarService } from "@peek/peek_plugin_diagram";

export interface PopupLayerSelectionArgsI {
    modelSetKey: string;
    coordSetKey: string;
}

export interface PopupBranchSelectionArgsI {
    modelSetKey: string;
    coordSetKey: string;
}

/** CoordSetCache
 *
 * This class is responsible for buffering the coord sets in memory.
 *
 * Typically there will be less than 20 of these.
 *
 */
@Injectable()
export class PrivateDiagramConfigService
    extends NgLifeCycleEvents
    implements DiagramConfigService
{
    private _popupLayerSelectionSubject: Subject<PopupLayerSelectionArgsI> =
        new Subject<PopupLayerSelectionArgsI>();

    private _popupBranchSelectionSubject: Subject<PopupBranchSelectionArgsI> =
        new Subject<PopupBranchSelectionArgsI>();

    private _useEdgeColorChangedSubject: Subject<boolean> =
        new Subject<boolean>();

    private _layersUpdatedSubject: Subject<void> = new Subject<void>();

    constructor(
        private lookupService: PrivateDiagramLookupService,
        private diagramToolbarService: DiagramToolbarService
    ) {
        super();
    }

    // ---------------
    // Layer Select Popup
    /** This method is called from the diagram-toolbar component */
    popupLayerSelection(modelSetKey: string, coordSetKey: string): void {
        this._popupLayerSelectionSubject.next({
            modelSetKey: modelSetKey,
            coordSetKey: coordSetKey,
        });
    }

    /** This observable is subscribed to by the select layer popup */
    popupLayerSelectionObservable(): Observable<PopupLayerSelectionArgsI> {
        return this._popupLayerSelectionSubject;
    }

    // ---------------
    // Branch Select Popup
    /** This method is called from the diagram-toolbar component */
    popupBranchesSelection(modelSetKey: string, coordSetKey: string): void {
        this._popupBranchSelectionSubject.next({
            modelSetKey: modelSetKey,
            coordSetKey: coordSetKey,
        });
    }

    /** This observable is subscribed to by the select branch popup */
    popupBranchesSelectionObservable(): Observable<PopupBranchSelectionArgsI> {
        return this._popupBranchSelectionSubject;
    }

    // ---------------
    // Use Polyline Edge Colors
    /** This is a published polyline */
    setUsePolylineEdgeColors(enabled: boolean): void {
        this._useEdgeColorChangedSubject.next(enabled);
    }

    /** This observable is subscribed to by the canvas component */
    usePolylineEdgeColorsObservable(): Observable<boolean> {
        return this._useEdgeColorChangedSubject;
    }

    // ---------------
    // Use Polyline Edge Colors
    /** This is a published polyline */
    setLayerVisible(
        modelSetKey: string,
        layerName: string,
        visible: boolean
    ): void {
        const layer = this.lookupService.layerForName(modelSetKey, layerName);
        if (layer == null) {
            throw new Error(
                "No layer exists for modelSetKey " +
                    `'${modelSetKey}' and name ${layerName}`
            );
        }
        layer.visible = visible;
        this._layersUpdatedSubject.next();
    }

    /** This observable is subscribed to by the canvas component */
    layersUpdatedObservable(): Observable<void> {
        return this._layersUpdatedSubject;
    }

    setToolbarVisible(enabled: boolean): void {
        this.diagramToolbarService.setToolbarVisible(enabled);
    }
}
