import { CommonModule } from "@angular/common";
import { HttpClientModule } from "@angular/common/http";
import { NgModule } from "@angular/core";
import { PluginInboxClientComponent } from "./plugin-inbox-client.component";
import { RouterModule, Routes } from "@angular/router";
import { FormsModule } from "@angular/forms";
import { NzIconModule } from "ng-zorro-antd/icon";
import { LoggedInGuard, } from "@peek/peek_core_user";
import { ActivityListComponent } from "./activity-list/activity-list.component";
import { TaskListComponent } from "./task-list/task-list.component";

export const pluginRoutes: Routes = [
    {
        path: "",
        component: PluginInboxClientComponent,
        canActivate: [LoggedInGuard],
    },
    {
        path: "**",
        component: PluginInboxClientComponent,
        canActivate: [LoggedInGuard],
    },
];

@NgModule({
    imports: [
        CommonModule,
        HttpClientModule,
        RouterModule.forChild(pluginRoutes),
        FormsModule,
        NzIconModule,
    ],
    exports: [],
    providers: [],
    declarations: [
        PluginInboxClientComponent,
        TaskListComponent,
        ActivityListComponent,
    ],
})
export class PluginInboxClientModule {}
