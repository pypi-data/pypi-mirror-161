import {
    addTupleType,
    deepCopy,
    SerialiseUtil,
    Tuple,
} from "@synerty/vortexjs";
import { diagramTuplePrefix } from "../PluginNames";
import * as moment from "moment";
import { BranchLiveEditTuple } from "./BranchLiveEditTuple";
import { PrivateDiagramLookupService } from "../services/PrivateDiagramLookupService";

let serUril = new SerialiseUtil();
declare var require: any;

interface UndoDataI {
    disps: any[];
    anchors: any[];
    updatedByUser: string;
    lastStage: number;
    needsSave: boolean;
    replacementIds: {};
}

export interface BranchLastEditPositionI {
    x: number;
    y: number;
    zoom: number;
    coordSetKey: string;
}

/** Diagram Branch Tuple
 *
 * This tuple is used internally to transfer branches from the client tuple provider,
 * and transfer branches to the client wrapped in a TupleAction.
 *
 */
@addTupleType
export class BranchTuple extends Tuple {
    public static readonly tupleName = diagramTuplePrefix + "BranchTuple";
    private static readonly __ID_NUM = 0;
    private static readonly __COORD_SET_ID_NUM = 1;
    private static readonly __KEY_NUM = 2;
    private static readonly __VISIBLE_NUM = 3;
    private static readonly __UPDATED_DATE = 4;
    private static readonly __CREATED_DATE = 5;
    private static readonly __DISPS_NUM = 6;
    private static readonly __ANCHOR_DISP_KEYS_NUM = 7;
    private static readonly __UPDATED_BY_USER_NUM = 8;
    private static readonly __NEEDS_SAVE_NUM = 9; // Not stored in DB
    private static readonly __LAST_EDIT_POSITION = 10;
    private static readonly __LAST_INDEX_NUM = 10;
    // The list of deltas for this branch
    packedJson__: any[] = [];
    protected _rawJonableFields = ["packedJson__"];

    // This structure stores IDs that need to be updated, from disps that have been
    // cloned from disps their replacing (their ID is re-assigned)
    // This is only a temporary structure only needed during an editing session.
    private _replacementIds = {};
    private _dispsById = {};
    private _lastStage = 1;
    private _contextUpdateCallback:
        | ((modelUpdateRequired: boolean) => void)
        | null;

    // Undo / Redo
    private undoQueue: string[] = [];
    private redoQueue: string[] = [];
    private readonly MAX_UNDO = 20;

    constructor() {
        super(BranchTuple.tupleName);
        for (
            let i = this.packedJson__.length;
            i < BranchTuple.__LAST_INDEX_NUM + 1;
            i++
        )
            this.packedJson__.push(null);
    }

    get needsSave(): boolean {
        return this.packedJson__[BranchTuple.__NEEDS_SAVE_NUM];
    }

    get id(): number {
        return this.packedJson__[BranchTuple.__ID_NUM];
    }

    get coordSetId(): number {
        return this.packedJson__[BranchTuple.__COORD_SET_ID_NUM];
    }

    get key(): string {
        return this.packedJson__[BranchTuple.__KEY_NUM];
    }

    get updatedByUser(): string {
        return this.packedJson__[BranchTuple.__UPDATED_BY_USER_NUM];
    }

    set updatedByUser(val: string) {
        this.packedJson__[BranchTuple.__UPDATED_BY_USER_NUM] = val;
    }

    get lastEditPosition(): BranchLastEditPositionI | null {
        const jsonStr = this.packedJson__[BranchTuple.__LAST_EDIT_POSITION];
        if (jsonStr == null || jsonStr.length == 0) return null;
        return JSON.parse(jsonStr);
    }

    set lastEditPosition(position: BranchLastEditPositionI) {
        this.packedJson__[BranchTuple.__LAST_EDIT_POSITION] =
            JSON.stringify(position);
    }

    get disps(): any[] {
        return this._array(BranchTuple.__DISPS_NUM).slice();
    }

    get anchorDispKeys(): string[] {
        return this._array(BranchTuple.__ANCHOR_DISP_KEYS_NUM).slice();
    }

    get visible(): boolean {
        return this.packedJson__[BranchTuple.__VISIBLE_NUM];
    }

    set visible(value: boolean) {
        this.packedJson__[BranchTuple.__VISIBLE_NUM] = value;
    }

    get updatedDate(): Date | null {
        let packedDate = this.packedJson__[BranchTuple.__UPDATED_DATE];
        if (packedDate == null) return packedDate;

        return serUril.fromStr(packedDate, SerialiseUtil.T_DATETIME);
    }

    get createdDate(): Date {
        return serUril.fromStr(
            this.packedJson__[BranchTuple.__CREATED_DATE],
            SerialiseUtil.T_DATETIME
        );
    }

    static createBranch(coordSetId: number, branchKey: string): any {
        let branch = new BranchTuple();
        branch.packedJson__[BranchTuple.__ID_NUM] = this._makeUniqueId();
        branch.packedJson__[BranchTuple.__COORD_SET_ID_NUM] = coordSetId;
        branch.packedJson__[BranchTuple.__KEY_NUM] = branchKey;
        branch.packedJson__[BranchTuple.__VISIBLE_NUM] = true;
        branch.setUpdatedDate(null);
        branch.setCreatedDate(new Date());
        branch.packedJson__[BranchTuple.__DISPS_NUM] = [];
        branch.packedJson__[BranchTuple.__ANCHOR_DISP_KEYS_NUM] = [];
        branch.packedJson__[BranchTuple.__UPDATED_BY_USER_NUM] = null;
        branch.packedJson__[BranchTuple.__NEEDS_SAVE_NUM] = false;
        branch.resetUndo();
        return branch;
    }

    static unpackJson(packedJsonStr: string): BranchTuple {
        // Create the new object
        let newSelf = new BranchTuple();
        newSelf.packedJson__ = JSON.parse(packedJsonStr);
        newSelf.assignIdsToDisps();
        newSelf.sortDisps();
        newSelf.resetUndo();
        return newSelf;
    }

    private static _makeUniqueId(index = -1): any {
        return <any>`NEW_${new Date().getTime()}_${index}`;
    }

    private static _setNewDispId(disp, index): void {
        let DispBase =
            require("@_peek/peek_plugin_diagram/canvas-shapes/DispBase")[
                "DispBase"
            ];
        let newId = this._makeUniqueId(index);

        if (DispBase.id(disp) == null) DispBase.setId(disp, newId);

        if (DispBase.hashId(disp) == null) DispBase.setHashId(disp, newId);
    }

    branchHasBeenSaved(): void {
        this.packedJson__[BranchTuple.__NEEDS_SAVE_NUM] = false;
    }

    addStage(): number {
        return this._lastStage++;
    }

    /** Add or Update Disps
     *
     * This method adds an array of disps to the branch.
     *
     * @param disps: An array of disps to add.
     * @param preventModelUpdate: Prevents this update from calling model compile.
     */
    addOrUpdateDisps(disps: any, preventModelUpdate = false): any[] {
        let modelUpdateRequired = false;
        let returnedDisps = [];

        for (let disp of disps) {
            let result = this.addOrUpdateSingleDisp(disp);
            modelUpdateRequired =
                modelUpdateRequired || result.modelUpdateRequired;
            returnedDisps.push(result.disp);
        }

        for (let disp of returnedDisps) this.updateReplacedIds(disp);

        this.sortDisps();
        this.touchUpdateDate(modelUpdateRequired && !preventModelUpdate);
        return returnedDisps;
    }

    /** Add or Update Disp
     *
     * This method adds the disp to the branch if it's new.
     *
     * If the disp is existing, but in a different stage, it clones and returns the disp
     * in the new stage.
     *
     * @param disp
     * @param preventModelUpdate: Prevents this update from calling model compile.
     */
    addOrUpdateDisp(disp: any, preventModelUpdate = false): any {
        let result = this.addOrUpdateSingleDisp(disp);
        this.updateReplacedIds(result);
        this.sortDisps();
        this.touchUpdateDate(result.modelUpdateRequired && !preventModelUpdate);
        return result.disp;
    }

    isDispInBranch(disp: any): boolean {
        // @ts-ignore
        let DispBase =
            require("@_peek/peek_plugin_diagram/canvas-shapes/DispBase")[
                "DispBase"
            ];
        return (
            this._dispsById[DispBase.id(disp)] != null ||
            this._replacementIds[DispBase.id(disp)] != null
        );
    }

    /** Add New Disps
     *
     * This method adds newly created disps to tbe branch in bulk.
     *
     * @param disps
     */
    addNewDisps(disps: any[]): void {
        // @ts-ignore
        let DispBase =
            require("@_peek/peek_plugin_diagram/canvas-shapes/DispBase")[
                "DispBase"
            ];
        let array = this._array(BranchTuple.__DISPS_NUM);

        for (let disp of disps) {
            BranchTuple._setNewDispId(disp, array.length);
            DispBase.setBranchStage(disp, this._lastStage);
            this._dispsById[DispBase.id(disp)] = disp;
            array.push(disp);
        }
        this.sortDisps();
        this.touchUpdateDate(true);
    }

    removeDisps(disps: any[]): void {
        // @ts-ignore
        let DispBase =
            require("@_peek/peek_plugin_diagram/canvas-shapes/DispBase")[
                "DispBase"
            ];
        // @ts-ignore
        let DispNull =
            require("@_peek/peek_plugin_diagram/canvas-shapes/DispNull")[
                "DispNull"
            ];

        let dispIdsToRemove = {};
        for (let disp of disps) {
            dispIdsToRemove[DispBase.id(disp)] = disp;
        }

        let array = this._array(BranchTuple.__DISPS_NUM);
        let branchDispsToBeConvertedToNullDisps = [];

        // Filter out disps in this branch that we're deleting
        // If the disp we're deleting replacing anoter disp (not in this branch)
        //      make a note of that.
        this.packedJson__[BranchTuple.__DISPS_NUM] = array.filter((disp) => {
            let id = DispBase.id(disp);
            if (dispIdsToRemove[id] != null) {
                if (DispBase.replacesHashId(disp) != null)
                    branchDispsToBeConvertedToNullDisps.push(disp);
                delete dispIdsToRemove[id];
                return false;
            }
            return true;
        });

        // Update the dispId dict to remove the disps we just filtered out
        this.assignIdsToDisps();

        // For all the Disps that are not part of this branch, we need to add a DispNull
        // to make it's deletion

        let nullDispsToCreate = [];

        function createNullDisp(dispToDelete, replacesHashId) {
            if (dispToDelete.bounds == null)
                throw new Error("Can not delete a disp with no bounds");

            let nullDisp = {
                // Type
                _tt: DispBase.TYPE_DN,

                // Level
                le: dispToDelete.le,
                lel: dispToDelete.lel,

                // Layer
                la: dispToDelete.la,
                lal: dispToDelete.lal,
            };

            DispNull.setGeomFromBounds(nullDisp, dispToDelete.bounds);
            DispBase.setReplacesHashId(nullDisp, replacesHashId);
            nullDispsToCreate.push(nullDisp);
        }

        // For all the Disps that are not part of this branch, we need to add a DispNull
        // to make it's deletion
        // Create NULL disps for disps being deleted that are not part of this branch
        for (let dispId of Object.keys(dispIdsToRemove)) {
            let disp = dispIdsToRemove[dispId];
            createNullDisp(disp, DispBase.hashId(disp));
        }

        // For all disps that are part of this branch, but replace other disps,
        // Create NULL disps for disps in this branch that replace other disps
        for (let disp of branchDispsToBeConvertedToNullDisps) {
            createNullDisp(disp, DispBase.replacesHashId(disp));
        }

        if (nullDispsToCreate.length != 0) this.addNewDisps(nullDispsToCreate);
        else this.touchUpdateDate(false);
    }

    addAnchorDispKey(key: string): void {
        let anchors = this._array(BranchTuple.__ANCHOR_DISP_KEYS_NUM);
        if (anchors.filter((k) => k == key).length != 0) return;

        this.touchUpdateDate(false);
        anchors.push(key);
    }

    touchUpdateDate(modelUpdateRequired: boolean = false): void {
        this.setNeedsSave();
        this.setUpdatedDate(new Date());
        if (this._contextUpdateCallback != null)
            this._contextUpdateCallback(modelUpdateRequired);
    }

    touchUndo(): void {
        const current = this.serialiseDisps();

        // If there is no change, queue nothing
        const len = this.undoQueue.length;
        if (len != 0 && this.undoQueue[len - 1] == current) return;

        this.undoQueue.push(current);
        this.resetRedo();

        while (this.undoQueue.length > this.MAX_UNDO) this.undoQueue.shift();
    }

    get canUndo(): boolean {
        return this.undoQueue.length > 1;
    }

    doUndo(lookupService: PrivateDiagramLookupService): void {
        if (this.undoQueue.length <= 1) return;

        const len = this.undoQueue.length;
        this.redoQueue.push(this.undoQueue.pop());
        this.restoreSerialisedDisps(this.undoQueue[len - 2]);

        this.linkDisps(lookupService);
        this.touchUpdateDate(true);
    }

    get canRedo(): boolean {
        return this.redoQueue.length !== 0;
    }

    doRedo(lookupService: PrivateDiagramLookupService): void {
        if (this.redoQueue.length == 0) return;

        const redo = this.redoQueue.pop();
        this.undoQueue.push(redo);
        this.restoreSerialisedDisps(redo);

        this.linkDisps(lookupService);
        this.touchUpdateDate(true);
    }

    toJsonField(
        value: any,
        jsonDict: {} | null = null,
        name: string | null = null
    ): any {
        // @ts-ignore
        const DispBase =
            require("@_peek/peek_plugin_diagram/canvas-shapes/DispBase")[
                "DispBase"
            ];
        if (name != "packedJson__")
            return Tuple.prototype.toJsonField(value, jsonDict, name);

        const convertedValue = deepCopy(
            value,
            DispBase.DEEP_COPY_FIELDS_TO_IGNORE
        );

        let disps = convertedValue[BranchTuple.__DISPS_NUM];

        this.cleanClonedDisps(disps);

        /* Now assign the value and it's value type if applicable */
        if (name != null && jsonDict != null) jsonDict[name] = convertedValue;

        return convertedValue;
    }

    linkDisps(lookupService: PrivateDiagramLookupService) {
        for (let disp of this.disps) {
            lookupService._linkDispLookups(disp);
        }
    }

    setContextUpdateCallback(
        contextUpdateCallback: ((modelUpdateRequired: boolean) => void) | null
    ) {
        this._contextUpdateCallback = contextUpdateCallback;
    }

    applyLiveUpdate(liveEditTuple: BranchLiveEditTuple): boolean {
        let liveUpdateTuple = liveEditTuple.branchTuple;

        if (
            this.updatedDate == null ||
            moment(this.updatedDate).isBefore(liveUpdateTuple.updatedDate) ||
            liveEditTuple.updateFromSave
        ) {
            this.packedJson__ = liveUpdateTuple.packedJson__;
            this.assignIdsToDisps();
            this.resetUndo();
            this.resetRedo();
            return true;
        }
        return false;
    }

    private assignIdsToDisps(): void {
        // @ts-ignore
        let DispBase =
            require("@_peek/peek_plugin_diagram/canvas-shapes/DispBase")[
                "DispBase"
            ];
        let array = this._array(BranchTuple.__DISPS_NUM);
        for (let i = 0; i < array.length; ++i) {
            let disp = array[i];
            BranchTuple._setNewDispId(disp, i);
            this._dispsById[DispBase.id(disp)] = disp;
            if (this._lastStage < DispBase.branchStage(disp))
                this._lastStage = DispBase.branchStage(disp);
        }
    }

    private _array(num: number): any[] {
        if (this.packedJson__[num] == null) this.packedJson__[num] = [];
        return this.packedJson__[num];
    }

    private resetUndo(): void {
        this.undoQueue = [this.serialiseDisps()];
    }

    private resetRedo(): void {
        this.redoQueue = [];
    }

    private setNeedsSave(): void {
        this.packedJson__[BranchTuple.__NEEDS_SAVE_NUM] = true;
    }

    private updateReplacedIds(disp) {
        // @ts-ignore
        let DispBase =
            require("@_peek/peek_plugin_diagram/canvas-shapes/DispBase")[
                "DispBase"
            ];
        let newGroupId = this._replacementIds[DispBase.groupId(disp)];
        if (newGroupId != null) DispBase.setGroupId(disp, newGroupId);
    }

    private addOrUpdateSingleDisp(disp: any): {
        disp: any;
        modelUpdateRequired: boolean;
    } {
        // @ts-ignore
        let DispBase =
            require("@_peek/peek_plugin_diagram/canvas-shapes/DispBase")[
                "DispBase"
            ];
        // @ts-ignore
        let DispGroupPointer =
            require("@_peek/peek_plugin_diagram/canvas-shapes/DispGroupPointer")[
                "DispGroupPointer"
            ];
        let array = this._array(BranchTuple.__DISPS_NUM);

        // If we've already replaced this Disp, then just return the replacement disp
        // This can happen when the select delegates call addOrUpdate disp multiple
        // times. (They have a selected and related array)
        if (this._replacementIds[DispBase.id(disp)] != null) {
            let newId = this._replacementIds[DispBase.id(disp)];
            return { disp: this._dispsById[newId], modelUpdateRequired: false };
        }

        // Find out if the disp is in this branch
        let dispInBranch = this._dispsById[DispBase.id(disp)];

        // If the Disp has an ID and it's not in this branch, then:
        // 1) we make a copy of the disp
        // 2) we set its "replacesHashId" to the "hashId" it's replacing.
        if (DispBase.id(disp) != null && dispInBranch == null) {
            let branchDisp = DispBase.cloneDisp(disp);

            DispBase.setReplacesHashId(branchDisp, DispBase.hashId(disp));
            DispGroupPointer.setTargetGroupId(branchDisp, null);
            DispBase.setHashId(branchDisp, null);

            // Deal with the new updated ID
            DispBase.setId(branchDisp, null);
            BranchTuple._setNewDispId(branchDisp, array.length);
            this._replacementIds[DispBase.id(disp)] = DispBase.id(branchDisp);

            disp = branchDisp;
        }

        BranchTuple._setNewDispId(disp, array.length);

        if (dispInBranch == null) {
            DispBase.setBranchStage(disp, this._lastStage);
            this._dispsById[DispBase.id(disp)] = disp;
            array.push(disp);
            return { disp: disp, modelUpdateRequired: true };
        }

        if (DispBase.branchStage(dispInBranch) == DispBase.branchStage(disp)) {
            return { disp: disp, modelUpdateRequired: false };
        }

        // Else, it's a new stage, clone the disp.

        this._dispsById[DispBase.id(disp)] = disp;
        array.push(disp);
        return { disp: disp, modelUpdateRequired: true };
    }

    private sortDisps(): void {
        // @ts-ignore
        const sortDisps =
            require("@_peek/peek_plugin_diagram/canvas/PeekCanvasModelUtil.web")[
                "sortDisps"
            ];

        let array = this._array(BranchTuple.__DISPS_NUM);
        this.packedJson__[BranchTuple.__DISPS_NUM] = sortDisps(array);
    }

    private setUpdatedDate(value: Date | null): void {
        if (value == null) this.packedJson__[BranchTuple.__UPDATED_DATE] = null;
        else
            this.packedJson__[BranchTuple.__UPDATED_DATE] =
                serUril.toStr(value);
    }

    private setCreatedDate(value: Date): void {
        this.packedJson__[BranchTuple.__CREATED_DATE] = serUril.toStr(value);
    }

    private serialiseDisps(): string {
        // @ts-ignore
        const DispBase =
            require("@_peek/peek_plugin_diagram/canvas-shapes/DispBase")[
                "DispBase"
            ];

        const disps = deepCopy(
            this._array(BranchTuple.__DISPS_NUM),
            DispBase.DEEP_COPY_FIELDS_TO_IGNORE
        );
        this.cleanClonedDisps(disps);

        let data: UndoDataI = {
            disps: disps,
            anchors: this.anchorDispKeys,
            updatedByUser: this.updatedByUser,
            lastStage: this._lastStage,
            needsSave: this.needsSave,
            replacementIds: this._replacementIds,
        };

        return JSON.stringify(data);
    }

    private restoreSerialisedDisps(undoJsonStr: string): void {
        const data: UndoDataI = JSON.parse(undoJsonStr);

        this.packedJson__[BranchTuple.__DISPS_NUM] = data.disps;
        this.packedJson__[BranchTuple.__ANCHOR_DISP_KEYS_NUM] = data.anchors;
        this.packedJson__[BranchTuple.__UPDATED_BY_USER_NUM] =
            data.updatedByUser;
        this.packedJson__[BranchTuple.__NEEDS_SAVE_NUM] = data.needsSave;

        this._replacementIds = data.replacementIds;
        this._lastStage = data.lastStage;
        this.assignIdsToDisps();
    }

    private cleanClonedDisps(disps: any[]): void {
        for (let disp of disps) {
            for (let key of Object.keys(disp)) {
                let dispval = disp[key];

                // Nulls are not included
                if (dispval == null) delete disp[key];
                // Delete all the linked lookups, we just want the IDs
                else if (dispval["__rst"] != null)
                    // VortexJS Serialise Class Type
                    delete disp[key];
            }
        }
    }
}
