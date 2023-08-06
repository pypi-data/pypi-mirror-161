import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { EditSettingComponent } from "./edit-setting-table/edit.component";
// Import our components
import { LiveDBComponent } from "./livedb.component";
import { StatusComponent } from "./status/status.component";
import {
    TupleActionPushNameService,
    TupleActionPushService,
    TupleDataObservableNameService,
    TupleDataObserverService,
    TupleDataOfflineObserverService,
    TupleOfflineStorageNameService,
    TupleOfflineStorageService,
} from "@synerty/vortexjs";

import {
    livedbActionProcessorName,
    livedbFilt,
    livedbObservableName,
    livedbTupleOfflineServiceName,
} from "@peek/peek_plugin_livedb/_private";

export function tupleActionPushNameServiceFactory() {
    return new TupleActionPushNameService(
        livedbActionProcessorName,
        livedbFilt
    );
}

export function tupleDataObservableNameServiceFactory() {
    return new TupleDataObservableNameService(livedbObservableName, livedbFilt);
}

export function tupleOfflineStorageNameServiceFactory() {
    return new TupleOfflineStorageNameService(livedbTupleOfflineServiceName);
}

// Define the routes for this Angular module
export const pluginRoutes: Routes = [
    {
        path: "",
        component: LiveDBComponent,
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
    declarations: [LiveDBComponent, StatusComponent, EditSettingComponent],
})
export class LiveDBModule {}
