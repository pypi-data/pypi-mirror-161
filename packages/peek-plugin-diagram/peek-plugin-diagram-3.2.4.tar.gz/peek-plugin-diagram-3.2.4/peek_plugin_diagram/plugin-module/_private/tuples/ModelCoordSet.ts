import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "../PluginNames";
import { ModelCoordSetGridSize } from "./ModelCoordSetGridSize";
import { PeekCanvasBounds } from "../PeekCanvasBounds";

/* Make Disp Group Grid Key
 
 Make the special disp group grid key name.
 This is used to store all of the DispGroups that are not specifically stored in a
 grid, with the DispGroupPtr that uses it.
 
 */
export function makeDispGroupGridKey(coordSetId: number): string {
    return `${coordSetId}|dispgroup`;
}

@addTupleType
export class ModelCoordSet extends Tuple {
    public static readonly tupleName = diagramTuplePrefix + "ModelCoordSet";

    id: number;
    key: string;
    name: string;
    initialPanX: number;
    initialPanY: number;
    initialZoom: number;

    // The pre-configured zoom level for this coord set to use when positioning.
    positionOnZoom: number;

    enabled: boolean;

    comment: string;

    modelSetId: number;

    minZoom: number;
    maxZoom: number;

    gridSizes: ModelCoordSetGridSize[];

    // Misc data holder
    data: { [key: string]: any } | null;

    // Show this Coord Set as a group of DispGroups to choose from in the Editor
    dispGroupTemplatesEnabled: boolean;

    // Show this Coord Set as a group of Line Templates to choose from in the Editor
    edgeTemplatesEnabled: boolean;

    // Show "Select Branches" button
    branchesEnabled: boolean;

    // Edit fields
    editEnabled: boolean;

    // Default Layer for new shapes
    editDefaultLayerId: number;

    // Default Level for new shapes
    editDefaultLevelId: number;

    // Default Color for new shapes
    editDefaultColorId: number;

    // Default Line for new shapes
    editDefaultLineStyleId: number;

    // Default Text for new shapes
    editDefaultTextStyleId: number;

    // Default Vertex/Node/Equipment Coord Set
    editDefaultVertexCoordSetId: number;
    editDefaultVertexGroupName: string;

    // Default Edge/Conductor Coord Set
    editDefaultEdgeCoordSetId: number;
    editDefaultEdgeGroupName: string;

    // is this the landing coord set?
    isLanding: boolean;

    constructor() {
        super(ModelCoordSet.tupleName);
    }

    /** Grid size for Zoom
     *
     * This method calculates which Z grid to use based on a zoom level
     */
    gridSizeForZoom(zoom: number): ModelCoordSetGridSize {
        if (zoom == null) throw new Error("Zoom can't be null");

        // Figure out the Z grid
        for (let gridSize of this.gridSizes) {
            if (gridSize.min <= zoom && zoom < gridSize.max) {
                return gridSize;
            }
        }
        throw new Error(`Unable to determine grid size for zoom ${zoom}`);
    }

    /** Grid Keys For Area
     *
     * This method returns the grids required for a certain area of a certain zoom level.
     *
     */
    gridKeysForArea(area: PeekCanvasBounds, zoom: number): string[] {
        function trunc(num: any) {
            return parseInt(num);
        }

        let gridSize = this.gridSizeForZoom(zoom);

        // Round the X min/max
        let minGridX = trunc(area.x / gridSize.xGrid);
        let maxGridX = trunc((area.x + area.w) / gridSize.xGrid) + 1;

        // Round the Y min/max
        let minGridY = trunc(area.y / gridSize.yGrid);
        let maxGridY = trunc((area.y + area.h) / gridSize.yGrid) + 1;

        // Iterate through and create the grids.
        let gridKeys = [];
        for (let x = minGridX; x < maxGridX; x++) {
            for (let y = minGridY; y < maxGridY; y++) {
                gridKeys.push(
                    this.id.toString() + "|" + gridSize.key + "." + x + "x" + y
                );
            }
        }

        return gridKeys;
    }
}
