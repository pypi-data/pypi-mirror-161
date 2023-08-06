import { Observable, Subject } from "rxjs";
import { Injectable } from "@angular/core";
import {
    DiagramToolbarService,
    DiagramToolButtonI,
    ToolbarTypeE,
} from "../../DiagramToolbarService";

@Injectable()
export class PrivateDiagramToolbarService extends DiagramToolbarService {
    toolButtons: DiagramToolButtonI[] = [];
    editToolButtons: DiagramToolButtonI[] = [];
    private _toolButtonsUpdatedSubject = new Subject<DiagramToolButtonI[]>();
    private _editToolButtonsUpdatedSubject = new Subject<
        DiagramToolButtonI[]
    >();
    private _showToolbarObservable = new Subject<boolean>();

    constructor() {
        super();

        /*
         this.addToolButton(null,
         null,
         {
         name: "Mockup",
         tooltip: null,
         icon: 'pencil',
         callback: () => alert("Mockup feature is coming soon."),
         children: []
         }
         );
         
         this.addToolButton(null,
         null,
         {
         name: "Search",
         tooltip: null,
         icon: 'search',
         callback: () => alert("Search feature is coming soon."),
         children: []
         }
         );
         
         
         this.addToolButton(null,
         null,
         {
         name: "WP Home",
         tooltip: null,
         icon: 'home',
         callback: () => alert("This is an example web link"),
         children: []
         }
         );
         */
    }

    toolButtonsUpdatedObservable(): Observable<DiagramToolButtonI[]> {
        return this._toolButtonsUpdatedSubject;
    }

    addToolButton(
        modelSetKey: string | null,
        coordSetKey: string | null,
        toolButton: DiagramToolButtonI,
        toolbarType: ToolbarTypeE = ToolbarTypeE.ViewToolbar
    ) {
        if (toolbarType === ToolbarTypeE.ViewToolbar) {
            this.toolButtons.push(toolButton);
            this._toolButtonsUpdatedSubject.next(this.toolButtons);
        } else {
            this.editToolButtons.push(toolButton);
            this._editToolButtonsUpdatedSubject.next(this.editToolButtons);
        }
    }

    removeToolButton(
        buttonKey: string,
        toolbarType: ToolbarTypeE = ToolbarTypeE.ViewToolbar
    ) {
        function condition(item: DiagramToolButtonI): boolean {
            return item.key != buttonKey;
        }

        if (toolbarType === ToolbarTypeE.ViewToolbar) {
            this.toolButtons = this.toolButtons.filter(condition);
            this._toolButtonsUpdatedSubject.next(this.toolButtons);
        } else {
            this.editToolButtons = this.editToolButtons.filter(condition);
            this._editToolButtonsUpdatedSubject.next(this.editToolButtons);
        }
    }

    editToolButtonsUpdatedObservable(): Observable<DiagramToolButtonI[]> {
        return this._editToolButtonsUpdatedSubject;
    }

    showToolbarObservable() {
        return this._showToolbarObservable;
    }
    setToolbarVisible(enabled: boolean): void {
        this.showToolbarObservable().next(enabled);
    }
}
