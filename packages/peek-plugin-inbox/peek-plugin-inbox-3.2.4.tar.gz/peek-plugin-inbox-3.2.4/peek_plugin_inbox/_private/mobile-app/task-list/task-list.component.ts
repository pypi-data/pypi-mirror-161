import { takeUntil } from "rxjs/operators";
import { Component } from "@angular/core";
import { HeaderService } from "@synerty/peek-plugin-base-js";
import { NgLifeCycleEvents, TupleGenericAction } from "@synerty/vortexjs";
import { Router } from "@angular/router";
import { TaskActionTuple, TaskTuple } from "@peek/peek_plugin_inbox";
import { PluginInboxRootService } from "@peek/peek_plugin_inbox/_private/plugin-inbox-root.service";
import { PrivateInboxTupleProviderService } from "@peek/peek_plugin_inbox/_private/private-inbox-tuple-provider.service";
import * as moment from "moment";

@Component({
    selector: "plugin-inbox-task-list",
    templateUrl: "task-list.component.web.html",
})
export class TaskListComponent extends NgLifeCycleEvents {
    tasks: TaskTuple[] = [];

    constructor(
        headerService: HeaderService,
        private rootService: PluginInboxRootService,
        private router: Router,
        private tupleService: PrivateInboxTupleProviderService
    ) {
        super();

        headerService.setTitle("My Tasks");

        // Load Tasks ------------------

        this.tasks = this.tupleService.tasks;
        this.tupleService
            .taskTupleObservable()
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: TaskTuple[]) => (this.tasks = tuples));
    }

    noItems(): boolean {
        return this.tasks == null || this.tasks.length == 0;
    }

    // Display methods

    hasRoute(task: TaskTuple) {
        return task.routePath != null && task.routePath.length;
    }

    dateTime(task: TaskTuple) {
        return moment(task.dateTime).format("HH:mm DD-MMM");
    }

    timePast(task: TaskTuple) {
        return moment
            .duration(new Date().getTime() - task.dateTime.getTime())
            .humanize();
    }

    // User Actions

    taskClicked(task: TaskTuple) {
        if (this.hasRoute(task)) this.router.navigate([task.routePath]);

        this.rootService.taskSelected(task.id);
    }

    actionClicked(task: TaskTuple, taskAction: TaskActionTuple) {
        if (taskAction.confirmMessage) {
            if (!confirm(taskAction.confirmMessage)) return;
        }

        let action = new TupleGenericAction();
        action.key = TaskActionTuple.tupleName;
        action.data = { id: taskAction.id };
        this.tupleService.tupleOfflineAction
            .pushAction(action)
            .catch((err) => alert(err));

        this.rootService.taskActioned(task.id);
    }
}
