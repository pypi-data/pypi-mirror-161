import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { NgModule } from "@angular/core";
import { PluginInboxAdminComponent } from "./plugin-inbox-admin.component";
import { RouterModule, Routes } from "@angular/router";
import { SendTestTaskComponent } from "./send-test-task/send-test-task.component";
import { SendTestActivityComponent } from "./send-test-activity/send-test-activity.component";
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
    inboxActionProcessorName,
    inboxFilt,
    inboxObservableName,
    inboxTupleOfflineServiceName,
} from "@peek/peek_plugin_inbox/plugin-inbox-names";
import { AdminSettingListComponent } from "./setting-list/admin-setting-list.component";
import { AdminTaskListComponent } from "./task-list/admin-task-list.component";
import { AdminActivityListComponent } from "./activity-list/admin-activity-list.component";

/**
 * Created by peek on 5/12/16.
 *
 */

export const pluginRoutes: Routes = [
    {
        path: "",
        component: PluginInboxAdminComponent,
    },
];

export function tupleDataObservableNameServiceFactory() {
    return new TupleDataObservableNameService(inboxObservableName, inboxFilt);
}

export function tupleActionPushNameServiceFactory() {
    return new TupleActionPushNameService(inboxActionProcessorName, inboxFilt);
}

export function tupleOfflineStorageNameServiceFactory() {
    return new TupleOfflineStorageNameService(inboxTupleOfflineServiceName);
}

@NgModule({
    imports: [CommonModule, FormsModule, RouterModule.forChild(pluginRoutes)],
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
    declarations: [
        PluginInboxAdminComponent,
        SendTestTaskComponent,
        SendTestActivityComponent,
        AdminSettingListComponent,
        AdminTaskListComponent,
        AdminActivityListComponent,
    ],
})
export class PluginInboxAdminModule {}
