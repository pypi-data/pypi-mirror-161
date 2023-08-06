import { DispBase, DispBaseT } from "../canvas-shapes/DispBase";

/** Sort Disps
 *
 * This method sorts disps in the order needed for the model to compile them for the
 * renderer.
 *
 * This method was initially written for the BranchTuple.
 *
 * WARNING: Sorting disps is terrible for performance, this is only used while
 * the branch is being edited by the user.
 *
 * @param disps: A List of disps to sort
 * @returns: A list of sorted disps
 */
export function sortDisps(disps: DispBaseT[]): DispBaseT[] {
    function cmp(d1: DispBaseT, d2: DispBaseT): number {
        let levelDiff = DispBase.level(d1).order - DispBase.level(d2).order;
        if (levelDiff != 0) return levelDiff;

        let layerDiff = DispBase.layer(d1).order - DispBase.layer(d2).order;
        if (layerDiff != 0) return layerDiff;

        return DispBase.zOrder(d1) - DispBase.zOrder(d2);
    }

    return disps.sort(cmp);
}
