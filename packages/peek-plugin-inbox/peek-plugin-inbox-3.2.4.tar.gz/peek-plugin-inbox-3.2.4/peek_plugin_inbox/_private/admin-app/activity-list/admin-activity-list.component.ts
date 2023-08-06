import {
    NgLifeCycleEvents,
    TupleDataObserverService,
    TupleSelector,
} from "@synerty/vortexjs";
import { Component } from "@angular/core";
import { ActivityTuple } from "@peek/peek_plugin_inbox/tuples/ActivityTuple";

@Component({
    selector: "admin-inbox-activity-list",
    templateUrl: "./admin-activity-list.component.html",
})
export class AdminActivityListComponent extends NgLifeCycleEvents {
    activities: ActivityTuple[] = [];
    userId: string = "";
    subscription: any = null;

    constructor(private observerService: TupleDataObserverService) {
        super();
    }

    update() {
        // Load Activities  ------------------

        let tupleSelector = new TupleSelector(ActivityTuple.tupleName, {
            userId: this.userId,
        });

        if (this.subscription != null) this.subscription.unsubscribe();

        this.subscription = this.observerService
            .subscribeToTupleSelector(tupleSelector)
            .subscribe((tuples: ActivityTuple[]) => {
                this.activities = tuples.sort(
                    (o1, o2) => o2.dateTime.getTime() - o1.dateTime.getTime()
                );
            });
        this.onDestroyEvent.subscribe(() => this.subscription.unsubscribe());
    }
}
