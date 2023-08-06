import { takeUntil } from "rxjs/operators";
import { Component } from "@angular/core";
import { HeaderService } from "@synerty/peek-plugin-base-js";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { Router } from "@angular/router";
import { ActivityTuple, PluginInboxRootService } from "@peek/peek_plugin_inbox";
import { PrivateInboxTupleProviderService } from "@peek/peek_plugin_inbox/_private/private-inbox-tuple-provider.service";
import * as moment from "moment";

@Component({
    selector: "plugin-inbox-activity-list",
    templateUrl: "activity-list.component.web.html",
})
export class ActivityListComponent extends NgLifeCycleEvents {
    activities: ActivityTuple[] = [];

    constructor(
        headerService: HeaderService,
        private rootService: PluginInboxRootService,
        private router: Router,
        private tupleService: PrivateInboxTupleProviderService
    ) {
        super();
        headerService.setTitle("My Activity");

        // Load Activities ------------------

        this.activities = this.tupleService.activities;
        this.tupleService
            .activityTupleObservable()
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: ActivityTuple[]) => (this.activities = tuples));
    }

    noItems(): boolean {
        return this.activities == null || this.activities.length == 0;
    }

    // Display methods

    hasRoute(activity: ActivityTuple) {
        return activity.routePath != null && activity.routePath.length;
    }

    dateTime(activity: ActivityTuple) {
        return moment(activity.dateTime).format("HH:mm DD-MMM");
    }

    timePast(activity: ActivityTuple) {
        return moment
            .duration(new Date().getTime() - activity.dateTime.getTime())
            .humanize();
    }

    nsTimeStr(activity) {
        return `${this.dateTime(activity)}, ${this.timePast(activity)} ago`;
    }

    // User Actions

    activityClicked(activity: ActivityTuple) {
        if (this.hasRoute(activity)) this.router.navigate([activity.routePath]);
    }
}
