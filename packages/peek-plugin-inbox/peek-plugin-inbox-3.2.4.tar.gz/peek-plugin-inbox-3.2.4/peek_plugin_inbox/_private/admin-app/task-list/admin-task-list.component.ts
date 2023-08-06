import {
    NgLifeCycleEvents,
    TupleDataObserverService,
    TupleSelector,
} from "@synerty/vortexjs";
import { TaskTuple } from "@peek/peek_plugin_inbox/tuples/TaskTuple";
import { Component } from "@angular/core";

@Component({
    selector: "admin-inbox-task-list",
    templateUrl: "./admin-task-list.component.html",
})
export class AdminTaskListComponent extends NgLifeCycleEvents {
    tasks: TaskTuple[] = [];
    userId: string = "";
    subscription: any = null;

    constructor(private observerService: TupleDataObserverService) {
        super();
    }

    update() {
        // Load Tasks ------------------
        let tupleSelector = new TupleSelector(TaskTuple.tupleName, {
            userId: this.userId,
        });

        if (this.subscription != null) this.subscription.unsubscribe();

        this.subscription = this.observerService
            .subscribeToTupleSelector(tupleSelector)
            .subscribe((tuples: TaskTuple[]) => {
                this.tasks = tuples.sort(
                    (o1, o2) => o2.dateTime.getTime() - o1.dateTime.getTime()
                );
            });
        this.onDestroyEvent.subscribe(() => this.subscription.unsubscribe());
    }
}
