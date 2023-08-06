import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { EditSettingComponent } from "./edit-setting-table/edit.component";
import {
    TupleActionPushNameService,
    TupleActionPushService,
    TupleDataObservableNameService,
    TupleDataObserverService,
    TupleOfflineStorageNameService,
    TupleOfflineStorageService,
    TupleDataOfflineObserverService,
} from "@synerty/vortexjs";
// Import our components
import { DiagramComponent } from "./diagram.component";
import { StatusComponent } from "./status/status.component";
import {
    diagramActionProcessorName,
    diagramFilt,
    diagramObservableName,
    diagramTupleOfflineServiceName,
} from "@peek/peek_plugin_diagram/_private";

export function tupleActionPushNameServiceFactory() {
    return new TupleActionPushNameService(
        diagramActionProcessorName,
        diagramFilt
    );
}

export function tupleDataObservableNameServiceFactory() {
    return new TupleDataObservableNameService(
        diagramObservableName,
        diagramFilt
    );
}

export function tupleOfflineStorageNameServiceFactory() {
    return new TupleOfflineStorageNameService(diagramTupleOfflineServiceName);
}

// Define the routes for this Angular module
export const pluginRoutes: Routes = [
    {
        path: "",
        component: DiagramComponent,
    },
];

// Define the module
@NgModule({
    imports: [CommonModule, RouterModule.forChild(pluginRoutes), FormsModule],
    exports: [],
    providers: [
        TupleActionPushService,
        {
            provide: TupleActionPushNameService,
            useFactory: tupleActionPushNameServiceFactory,
        },
        TupleOfflineStorageService,
        {
            provide: TupleOfflineStorageNameService,
            useFactory: tupleOfflineStorageNameServiceFactory,
        },
        TupleDataObserverService,
        TupleDataOfflineObserverService,
        {
            provide: TupleDataObservableNameService,
            useFactory: tupleDataObservableNameServiceFactory,
        },
    ],
    declarations: [DiagramComponent, StatusComponent, EditSettingComponent],
})
export class PeekPluginDiagramModule {}
