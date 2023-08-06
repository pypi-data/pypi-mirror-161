import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { NgModule } from "@angular/core";
import { CoreEmailAdminComponent } from "./core-email-admin.component";
import { RouterModule, Routes } from "@angular/router";
import {
    TupleActionPushNameService,
    TupleActionPushService,
    TupleDataObservableNameService,
    TupleDataObserverService,
} from "@synerty/vortexjs";

import {
    coreEmailActionProcessorName,
    coreEmailFilt,
    coreEmailObservableName,
} from "./PluginNames";
import { AdminSettingListComponent } from "./setting-list/admin-setting-list.component";

/**
 * Created by peek on 5/12/16.
 *
 */

export const pluginRoutes: Routes = [
    {
        path: "",
        component: CoreEmailAdminComponent,
    },
];

export function tupleDataObservableNameServiceFactory() {
    return new TupleDataObservableNameService(
        coreEmailObservableName,
        coreEmailFilt
    );
}

export function tupleActionPushNameServiceFactory() {
    return new TupleActionPushNameService(
        coreEmailActionProcessorName,
        coreEmailFilt
    );
}

@NgModule({
    imports: [CommonModule, FormsModule, RouterModule.forChild(pluginRoutes)],
    exports: [],
    providers: [
        TupleDataObserverService,
        {
            provide: TupleDataObservableNameService,
            useFactory: tupleDataObservableNameServiceFactory,
        },
        TupleActionPushService,
        {
            provide: TupleActionPushNameService,
            useFactory: tupleActionPushNameServiceFactory,
        },
    ],
    declarations: [CoreEmailAdminComponent, AdminSettingListComponent],
})
export class CoreEmailAdminModule {}
