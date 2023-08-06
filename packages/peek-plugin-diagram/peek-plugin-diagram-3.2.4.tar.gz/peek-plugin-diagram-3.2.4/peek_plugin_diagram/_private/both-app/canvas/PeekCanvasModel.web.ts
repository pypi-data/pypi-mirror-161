import { takeUntil } from "rxjs/operators";
import { PeekCanvasConfig } from "./PeekCanvasConfig.web";
import { GridObservable } from "../cache/GridObservable.web";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { LinkedGrid } from "../cache/LinkedGrid.web";
import { dateStr, dictKeysFromObject, dictSetFromArray } from "../DiagramUtil";
import { PrivateDiagramLookupService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramLookupService";
import { DispBase, DispBaseT, DispType } from "../canvas-shapes/DispBase";
import { PrivateDiagramBranchService } from "@peek/peek_plugin_diagram/_private/branch/PrivateDiagramBranchService";
import { PeekCanvasModelQuery } from "./PeekCanvasModelQuery.web";
import { PeekCanvasModelSelection } from "./PeekCanvasModelSelection.web";
import {
    OverrideUpdateDataI,
    PrivateDiagramOverrideService,
} from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramOverrideService";
import { DispGroupPointerT } from "../canvas-shapes/DispGroupPointer";
import { PeekCanvasModelOverrideA } from "../canvas-override/PeekCanvasModelOverrideA";
import { PeekCanvasModelOverrideColor } from "../canvas-override/PeekCanvasModelOverrideColor";
import { PeekCanvasModelOverrideHighlight } from "../canvas-override/PeekCanvasModelOverrideHighlight";

// import 'rxjs/add/operator/takeUntil';

function now(): any {
    return new Date();
}

interface GridOrBranchI {
    disps: any[];
    key: string;
    isBranch: boolean;
}

/**
 * Peek Canvas Model
 *
 * This class stores and manages the model of the NodeCoord and ConnCoord
 * objects that are within the viewable area.
 *
 */

export class PeekCanvasModel {
    private _modelSetId = null;
    private _coordSetId = null;

    // Grid Buffer
    private _gridBuffer = {};

    // The grid keys  SET in the viewable area from the last check
    private _viewingGridKeysDict = {};

    // The grid keys STRING in the viewable area from the last check
    private _viewingGridKeysStr: string = "";

    // Objects to be drawn on the display
    private _visibleDisps = [];

    // Does the model need an update?
    private needsUpdate = false;

    // Does the display array need recompiling?
    private needsCompiling = false;

    // Is the model currently updating
    private isUpdating = false;

    private readonly _query: PeekCanvasModelQuery;
    private readonly _selection: PeekCanvasModelSelection;
    private readonly _overrides: PeekCanvasModelOverrideA[];

    constructor(
        private config: PeekCanvasConfig,
        private gridObservable: GridObservable,
        private lookupCache: PrivateDiagramLookupService,
        private branchService: PrivateDiagramBranchService,
        private overrideService: PrivateDiagramOverrideService,
        private lifecycleEventEmitter: NgLifeCycleEvents
    ) {
        this._query = new PeekCanvasModelQuery(this);
        this._selection = new PeekCanvasModelSelection(this, this.config);
        this._overrides = [
            new PeekCanvasModelOverrideColor(config, lookupCache),
            new PeekCanvasModelOverrideHighlight(config, lookupCache),
        ];

        this.needsUpdate = false;

        // Start the gridKey checker timer.
        setInterval(
            () => this._checkGridKeysForArea(),
            this.config.controller.updateInterval
        );

        // Start the draw timer.
        setInterval(
            () => this._compileDisps(),
            this.config.controller.updateInterval
        );

        // Subscribe to grid updates, when the data store gets and update
        // from the server, we will

        this.gridObservable
            .observableForCanvas(this.config.canvasId)
            .pipe(takeUntil(this.lifecycleEventEmitter.onDestroyEvent))
            .subscribe((grid: LinkedGrid) => this._receiveGrid([grid]));

        this.lifecycleEventEmitter.onDestroyEvent.subscribe(() =>
            this.gridObservable.unsubscribeCanvas(this.config.canvasId)
        );

        // Hook up the trigger to recompile the model
        this.config.model.needsCompiling
            .pipe(takeUntil(this.lifecycleEventEmitter.onDestroyEvent))
            .subscribe(() => (this.needsCompiling = true));

        // Watch for changes to the config that effect us
        this.config.controller.coordSetChange
            .pipe(takeUntil(this.lifecycleEventEmitter.onDestroyEvent))
            .subscribe((coordSet) => {
                if (coordSet == null) {
                    this._modelSetId = null;
                    this._coordSetId = null;
                } else {
                    this._modelSetId = coordSet.modelSetId;
                    this._coordSetId = coordSet.id;
                }

                this.reset();
                this.selection.reset();
                this.needsUpdate = true;
            });

        // Watch the canvas settings, if they change then request and update from
        // the cache
        this.config.viewPort.windowChange
            .pipe(takeUntil(this.lifecycleEventEmitter.onDestroyEvent))
            .subscribe(() => (this.needsUpdate = true));

        // Watch the overrides, if the overrides change, then
        this.overrideService.overridesUpdatedObservable
            .pipe(takeUntil(this.lifecycleEventEmitter.onDestroyEvent))
            .subscribe((data: OverrideUpdateDataI) => {
                for (const override of this._overrides) {
                    override.setOverrides(data.overrides);
                }

                this.needsCompiling = true;
                if (data.overridesRemoved) {
                    // Force the updates to load when they come back
                    for (const gridKey of Object.keys(this._gridBuffer)) {
                        this._gridBuffer[gridKey].lastUpdate = null;
                    }
                    // Flush the cache and reload the grid keys
                    this.gridObservable.updateDiagramWatchedGrids(
                        this.config.canvasId,
                        Object.keys(this._viewingGridKeysDict),
                        true
                    );
                }
            });
    }

    // -------------------------------------------------------------------------
    // reset

    get query(): PeekCanvasModelQuery {
        return this._query;
    }

    // -------------------------------------------------------------------------
    // Request Display Updates

    get selection(): PeekCanvasModelSelection {
        return this._selection;
    }

    // -------------------------------------------------------------------------
    // Process Display Updates

    viewableDisps() {
        return this._visibleDisps;
    }

    // -------------------------------------------------------------------------
    // Get Overrides
    get overrides(): PeekCanvasModelOverrideA[] {
        return this._overrides;
    }

    // -------------------------------------------------------------------------
    // Display Items
    // -------------------------------------------------------------------------

    recompileModel(): void {
        this._compileDisps(true);
    }

    protected _compileDisps(force = false) {
        if (!this.needsCompiling && !force) return;

        this.needsCompiling = false;

        if (this._modelSetId == null || this._coordSetId == null) return;

        let startTime = now();

        const levelsOrderedByOrder = this.lookupCache.levelsOrderedByOrder(
            this._coordSetId
        );
        const layersOrderedByOrder = this.lookupCache.layersOrderedByOrder(
            this._modelSetId
        );
        const viewingBranchIds = this.branchService.getVisibleBranchIds(
            this._coordSetId
        );

        let dispIndexByGridKey = {};

        let disps = [];
        let dispHashIdsAdded = {};
        let branchIdsActive = {};
        let viewingBranchesActive = viewingBranchIds.length != 0;

        for (let id of viewingBranchIds) {
            branchIdsActive[id] = true;
        }

        // Get the grids we're going to compile
        let gridsOrBranchesToCompile: GridOrBranchI[] = [];
        for (let gridKey of Object.keys(this._viewingGridKeysDict)) {
            let grid = this._gridBuffer[gridKey];

            if (grid == null) continue;

            gridsOrBranchesToCompile.push({
                key: grid.gridKey,
                disps: grid.disps,
                isBranch: false,
            });
        }

        // Include the active branch
        let isEditorActive = this.config.editor.active;
        let activeBranch = this.config.editor.activeBranchTuple;
        if (activeBranch != null) {
            for (let branchDisp of activeBranch.disps)
                dispHashIdsAdded[DispBase.replacesHashId(branchDisp)] = true;

            // Make sure it's not showing when we edit the branch
            delete branchIdsActive[activeBranch.id];

            gridsOrBranchesToCompile.push({
                key: activeBranch.key,
                disps: activeBranch.disps,
                isBranch: true,
            });
        }

        // For all the disps we're going to add,
        // Add all the replacesHashId so that the disps being replaced don't show.
        for (let gridOrBranch of gridsOrBranchesToCompile) {
            for (let disp of gridOrBranch.disps) {
                // TODO Restrict for Branch Stage
                // If the branch is showing, and it replaces a hash,
                // then add the hash it replaces
                let replacesHashId = DispBase.replacesHashId(disp);
                if (
                    branchIdsActive[disp.bi] == true &&
                    replacesHashId != null
                ) {
                    dispHashIdsAdded[replacesHashId] = true;
                }
            }
        }

        for (const level of levelsOrderedByOrder) {
            for (const layer of layersOrderedByOrder) {
                // If it's not visible (enabled), continue
                if (!layer.visible && !isEditorActive) continue;

                for (let gridOrBranch of gridsOrBranchesToCompile) {
                    let gridOrBranchDisps = gridOrBranch.disps;

                    // If this is the first iteration, initialise to 0
                    let nextIndex = dispIndexByGridKey[gridOrBranch.key];
                    if (nextIndex == null) nextIndex = 0;

                    // If we've processed all the disps in this grid, continue to next
                    if (nextIndex >= gridOrBranchDisps.length) continue;

                    for (; nextIndex < gridOrBranchDisps.length; nextIndex++) {
                        const disp = gridOrBranchDisps[nextIndex];

                        // Filter out overlay disps if we need to
                        if (
                            (isEditorActive ||
                                viewingBranchesActive ||
                                !this.config.model.overlayEnabled) &&
                            DispBase.isOverlay(disp)
                        )
                            continue;

                        // Level first, as per the sortDisps function
                        let dispLevel = DispBase.level(disp);
                        if (dispLevel.order < level.order) continue;

                        if (level.order < dispLevel.order) break;

                        // Then Layer
                        let dispLayer = DispBase.layer(disp);
                        if (dispLayer.order < layer.order) continue;

                        if (layer.order < dispLayer.order) break;

                        // If the disp has already been added or is being replaced
                        // by a branch, then skip this one
                        if (dispHashIdsAdded[DispBase.hashId(disp)] === true)
                            continue;

                        // Is the branch showed from the "View Branches" menu
                        let isBranchViewable =
                            branchIdsActive[disp.bi] === true;

                        // If this is not apart of a branch, or ...
                        if (
                            disp.bi == null ||
                            isBranchViewable ||
                            gridOrBranch.isBranch
                        ) {
                            disps.push(disp);
                            dispHashIdsAdded[DispBase.hashId(disp)] = true;
                        }
                    }

                    dispIndexByGridKey[gridOrBranch.key] = nextIndex;
                }
            }
        }

        for (const override of this._overrides) {
            override.compile(disps);
        }

        if (isEditorActive) this.relinkDispGroups(disps);

        this._visibleDisps = disps;
        this.selection.applyTryToSelect();
        this.config.model.dispOnScreen = disps.length;
        this.config.invalidate();

        let timeTaken = now() - startTime;

        console.log(
            `${dateStr()} Model: compileDisps took ${timeTaken}ms` +
                ` for ${disps.length} disps` +
                ` and ${gridsOrBranchesToCompile.length} grids/branches`
        );
    }

    // -------------------------------------------------------------------------
    private reset() {
        this.needsUpdate = false;
        this.isUpdating = false;

        this._visibleDisps = []; // Objects to be drawn on the display
        this._gridBuffer = {}; // Store grids from the server by gridKey.

        this._viewingGridKeysDict = {};
        this._viewingGridKeysStr = "";
    }

    // -------------------------------------------------------------------------
    private _checkGridKeysForArea() {
        if (this._coordSetId == null) return;

        if (!this.lookupCache.isReady()) return;

        if (!this.needsUpdate) return;

        this.needsUpdate = false;

        let area = this.config.viewPort.window;
        let zoom = this.config.viewPort.zoom;

        let viewingGridKeys = this.config.controller.coordSet.gridKeysForArea(
            area,
            zoom
        );

        // If there is no change, then do nothing
        // Should these be sorted?
        if (viewingGridKeys.join() == this._viewingGridKeysStr) return;

        this._viewingGridKeysStr = viewingGridKeys.join();
        this._viewingGridKeysDict = dictSetFromArray(viewingGridKeys);

        // Remove grids we're no longer looking at.
        for (let gridKey of dictKeysFromObject(this._gridBuffer)) {
            if (!this._viewingGridKeysDict.hasOwnProperty(gridKey)) {
                delete this._gridBuffer[gridKey];
            }
        }

        // Notify the grid manager that the view has changed
        this.gridObservable.updateDiagramWatchedGrids(
            this.config.canvasId,
            viewingGridKeys
        );
    }

    // -------------------------------------------------------------------------
    /** Receive Grid
     *
     * NOTE: The grid data is not received in order,
     * and sometimes the ModelGrids don't have data when no
     * update from the server is requird.
     *
     * @param linkedGrids: A list of grids from the GridObservable
     * @private
     */
    private _receiveGrid(linkedGrids: LinkedGrid[]) {
        // Overwrite with all the new ones
        for (let linkedGrid of linkedGrids) {
            console.log(
                `PeekCanvasModel: Received grid ${linkedGrid.gridKey},  ${linkedGrid.lastUpdate}`
            );

            // If the grid now has no data, then clear it from the model.
            if (!linkedGrid.hasData()) {
                if (this._gridBuffer[linkedGrid.gridKey] != null) {
                    console.log(
                        `PeekCanvasModel: Clearing grid ${linkedGrid.gridKey}`
                    );
                    delete this._gridBuffer[linkedGrid.gridKey];
                    this.needsCompiling = true;
                }
                continue;
            }

            // If we're not viewing this grid any more, discard the data.
            if (this._viewingGridKeysDict[linkedGrid.gridKey] == null) continue;

            // If it's not an update, also ignore it.
            let currentGrid = this._gridBuffer[linkedGrid.gridKey];
            if (
                currentGrid != null &&
                currentGrid.lastUpdate == linkedGrid.lastUpdate
            )
                continue;

            console.log(
                `PeekCanvasModel: Applying grid ${linkedGrid.gridKey},  ${linkedGrid.lastUpdate}`
            );
            this._gridBuffer[linkedGrid.gridKey] = linkedGrid;
            this.needsCompiling = true;
        }
    }

    private relinkDispGroups(disps: DispBaseT[]): void {
        // Setup the disp group links
        const dispGroupsById: { [id: number]: DispGroupPointerT } = {};
        const allDispsById = {};
        for (const disp of disps) {
            allDispsById[disp.id] = disp;
            if (DispBase.typeOf(disp) != DispType.groupPointer) continue;

            dispGroupsById[disp.id] = <DispGroupPointerT>disp;
            (<DispGroupPointerT>disp).disps = [];
        }

        for (const disp of disps) {
            // Reset all bounds
            DispBase.setBoundsNull(disp);

            const groupId = DispBase.groupId(disp);
            if (groupId == null) continue;

            const dispGroup = dispGroupsById[groupId];
            if (dispGroup == null) {
                // console.log(`Group for groupId ${groupId} doesn't exist.`);

                if (allDispsById[groupId] != null)
                    console.log(allDispsById[groupId]);
                continue;
            }
            (<DispBaseT>disp).dispGroup = dispGroup;
            dispGroup.disps.push(disp);
        }
    }
}
