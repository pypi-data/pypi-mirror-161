import { takeUntil } from "rxjs/operators";
import { Component, Input, OnInit } from "@angular/core";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { PeekCanvasEditor } from "../canvas/PeekCanvasEditor.web";
import { DiagramCoordSetService } from "@peek/peek_plugin_diagram/DiagramCoordSetService";
import { BranchDetailTuple, BranchService } from "@peek/peek_plugin_branch";

import { PrivateDiagramCoordSetService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramCoordSetService";
import {
    PopupEditBranchSelectionArgs,
    PrivateDiagramBranchService,
} from "@peek/peek_plugin_diagram/_private/branch/PrivateDiagramBranchService";

import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { UserService } from "@peek/peek_core_user";

@Component({
    selector: "pl-diagram-start-edit",
    templateUrl: "start-edit.component.web.html",
    styleUrls: ["start-edit.component.web.scss"],
})
export class StartEditComponent extends NgLifeCycleEvents implements OnInit {
    popupShown: boolean = false;

    @Input("coordSetKey")
    coordSetKey: string;

    @Input("modelSetKey")
    modelSetKey: string;

    @Input("canvasEditor")
    canvasEditor: PeekCanvasEditor;
    items: BranchDetailTuple[] = [];
    NEW_TAB = 0;
    EXISTING_TAB = 1;
    barIndex: number = 0;
    selectedBranch: BranchDetailTuple = null;
    newBranch: BranchDetailTuple = new BranchDetailTuple();
    private coordSetService: PrivateDiagramCoordSetService;

    constructor(
        private branchService: PrivateDiagramBranchService,
        abstractCoordSetService: DiagramCoordSetService,
        private globalBranchService: BranchService,
        private balloonMsg: BalloonMsgService,
        private userService: UserService
    ) {
        super();

        this.coordSetService = <PrivateDiagramCoordSetService>(
            abstractCoordSetService
        );

        this.branchService.popupEditBranchSelectionObservable
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((v: PopupEditBranchSelectionArgs) => this.openPopup(v));
    }

    ngOnInit() {}

    closePopup(): void {
        this.popupShown = false;

        // Discard the integration additions
        this.items = [];
    }

    // --------------------
    //

    noItems(): boolean {
        return this.items.length == 0;
    }

    isBranchSelected(item: BranchDetailTuple): boolean {
        return (
            item != null &&
            this.selectedBranch != null &&
            item.id == this.selectedBranch.id
        );
    }

    selectBranch(item: BranchDetailTuple): void {
        this.selectedBranch = item;
    }

    startEditing() {
        let branchToEdit = null;

        if (this.barIndex == this.NEW_TAB) {
            let nb = this.newBranch;
            if (nb.name == null || nb.name.length == 0) {
                this.balloonMsg.showWarning(
                    "Name must be supplied to create a branch"
                );
                return;
            }

            nb.key = `${nb.userName}|${nb.createdDate.getTime()}|${nb.name}`;

            this.globalBranchService
                .createBranch(nb)
                .catch((e) =>
                    this.balloonMsg.showError(`Failed to create branch : ${e}`)
                );

            branchToEdit = this.newBranch;
        } else if (this.barIndex == this.EXISTING_TAB) {
            if (this.selectedBranch == null) {
                this.balloonMsg.showWarning("You must select a branch to edit");
                return;
            }

            branchToEdit = this.selectedBranch;
        }

        this.branchService.startEditing(
            this.modelSetKey,
            this.coordSetKey,
            branchToEdit.key
        );
        this.closePopup();
    }

    protected openPopup({ coordSetKey, modelSetKey }) {
        const userDetail = this.userService.userDetails;

        this.newBranch = new BranchDetailTuple();
        this.newBranch.modelSetKey = this.modelSetKey;
        this.newBranch.createdDate = new Date();
        this.newBranch.updatedDate = new Date();
        this.newBranch.userName = userDetail.userName;

        // let coordSet = this.coordSetService.coordSetForKey(coordSetKey);
        console.log("Opening Start Edit popup");

        this.globalBranchService
            .branches(this.modelSetKey)
            .then((tuples: BranchDetailTuple[]) => {
                this.items = tuples.sort(
                    (a, b) => b.createdDate.getTime() - a.createdDate.getTime()
                );
            })
            .catch((e) => `Failed to load branches ${e}`);

        this.items = [];

        this.popupShown = true;
    }
}
