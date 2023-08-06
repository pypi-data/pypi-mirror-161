import { filter, takeUntil } from "rxjs/operators";
import { Component, Input } from "@angular/core";
import { HeaderService } from "@synerty/peek-plugin-base-js";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { BranchDetailTuple, BranchService } from "@peek/peek_plugin_branch";
import { PrivateDiagramConfigService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramConfigService";
import { PrivateDiagramLookupService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramLookupService";
import { DiagramCoordSetService } from "@peek/peek_plugin_diagram/DiagramCoordSetService";
import { PrivateDiagramCoordSetService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramCoordSetService";
import { PeekCanvasConfig } from "../canvas/PeekCanvasConfig.web";
import { PrivateDiagramBranchService } from "@peek/peek_plugin_diagram/_private/branch";
import {
    DocDbPopupClosedReasonE,
    DocDbPopupService,
    DocDbPopupTypeE,
} from "@peek/peek_core_docdb";

@Component({
    selector: "pl-diagram-view-select-branches",
    templateUrl: "select-branches.component.web.html",
    styleUrls: ["select-branches.component.web.scss"],
})
export class SelectBranchesComponent extends NgLifeCycleEvents {
    @Input("coordSetKey")
    coordSetKey: string;

    @Input("modelSetKey")
    modelSetKey: string;

    @Input("config")
    config: PeekCanvasConfig;

    popupShown: boolean = false;
    items: BranchDetailTuple[] = [];
    enabledBranches: { [branchKey: string]: BranchDetailTuple } = {};
    selectedGlobalBranch: BranchDetailTuple | null = null;

    private coordSetService: PrivateDiagramCoordSetService;

    constructor(
        private objectPopupService: DocDbPopupService,
        private headerService: HeaderService,
        private lookupService: PrivateDiagramLookupService,
        private configService: PrivateDiagramConfigService,
        private branchService: PrivateDiagramBranchService,
        abstractCoordSetService: DiagramCoordSetService,
        private globalBranchService: BranchService
    ) {
        super();

        this.coordSetService = <PrivateDiagramCoordSetService>(
            abstractCoordSetService
        );

        this.configService
            .popupBranchesSelectionObservable()
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe(() => this.openPopup());

        this.objectPopupService
            .popupClosedObservable(DocDbPopupTypeE.summaryPopup)
            .pipe(
                filter(
                    (reason) =>
                        reason == DocDbPopupClosedReasonE.userClickedAction
                )
            )
            .subscribe(() => this.closePopupFull());

        this.objectPopupService
            .popupClosedObservable(DocDbPopupTypeE.detailPopup)
            .pipe(
                filter(
                    (reason) =>
                        reason == DocDbPopupClosedReasonE.userClickedAction
                )
            )
            .subscribe(() => this.closePopupFull());
    }

    closePopupFull(): void {
        this.clearBranchDetails();
        this.closePopup();
    }

    closePopup(): void {
        if (this.showBranchDetails()) {
            this.clearBranchDetails();
            return;
        }

        let branches = [];
        for (let key of Object.keys(this.enabledBranches)) {
            branches.push(this.enabledBranches[key]);
        }
        this.branchService.setVisibleBranches(branches);
        this.config.setModelNeedsCompiling();

        this.popupShown = false;

        // Discard the integration additions
        this.items = [];
    }

    noItems(): boolean {
        return this.items.length == 0;
    }

    toggleBranchEnabled(branchDetail: BranchDetailTuple): void {
        if (this.enabledBranches[branchDetail.key] == null) {
            this.enabledBranches[branchDetail.key] = branchDetail;
        } else {
            delete this.enabledBranches[branchDetail.key];
        }
    }

    isBranchEnabled(branchDetail: BranchDetailTuple): boolean {
        return this.enabledBranches[branchDetail.key] != null;
    }

    branchSelected(branchDetail: BranchDetailTuple): void {
        this.selectedGlobalBranch = branchDetail;
    }

    clearBranchDetails(): void {
        this.selectedGlobalBranch = null;
    }

    showBranchDetails(): boolean {
        return this.selectedGlobalBranch != null;
    }

    protected openPopup() {
        let coordSet = this.coordSetService.coordSetForKey(
            this.modelSetKey,
            this.coordSetKey
        );
        console.log("Opening Branch Select popup");

        // Get a list of existing diagram branches, if there are no matching diagram
        // branches, then don't show them
        let diagramKeys = this.branchService.getDiagramBranchKeys(coordSet.id);
        let diagramKeyDict = {};
        for (let key of diagramKeys) {
            diagramKeyDict[key] = true;
        }

        this.globalBranchService
            .branches(this.modelSetKey)
            .then((tuples: BranchDetailTuple[]) => {
                this.items = [];
                for (let item of tuples) {
                    if (diagramKeyDict[item.key] == null) continue;
                    this.items.push(item);
                    item["__enabled"] = this.enabledBranches[item.key] != null;
                }
            });
        this.items = [];

        this.popupShown = true;
    }
}
