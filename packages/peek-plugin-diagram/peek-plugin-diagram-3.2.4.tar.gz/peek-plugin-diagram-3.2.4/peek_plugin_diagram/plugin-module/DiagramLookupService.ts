import {
    DispColor,
    DispLayer,
    DispLevel,
    DispLineStyle,
    DispTextStyle,
} from "./lookups";
import { Observable } from "rxjs";

/** Lookup Cache
 *
 * This class provides handy access to the lookup objects
 *
 * Typically there will be only a few hundred of these.
 *
 */
export abstract class DiagramLookupService {
    abstract isReady(): boolean;

    abstract isReadyObservable(): Observable<boolean>;

    // ============================================================================
    // Accessors

    abstract levelForId(levelId: number): DispLevel;

    abstract layerForId(layerId: number): DispLayer;

    abstract layerForName(modelSetKey: string, layerName: string): DispLayer;

    /** Color for Name
     *
     * Returns a DispColor if there is one where .color == name
     * @param modelSetKeyOrId
     * @param name
     */
    abstract colorForName(
        modelSetKeyOrId: string | number,
        name: string
    ): DispColor | null;

    abstract colorForId(colorId: number): DispColor;

    abstract textStyleForId(textStyleId: number): DispTextStyle;

    abstract lineStyleForId(lineStyleId: number): DispLineStyle;

    abstract layersOrderedByOrder(
        modelSetKeyOrId: number | string
    ): DispLayer[];

    abstract levelsOrderedByOrder(coordSetId: number): DispLevel[];

    abstract colorsOrderedByName(modelSetKeyOrId: number | string): DispColor[];

    abstract textStylesOrderedByName(
        modelSetKeyOrId: number | string
    ): DispTextStyle[];

    abstract lineStylesOrderedByName(
        modelSetKeyOrId: number | string
    ): DispLineStyle[];
}
