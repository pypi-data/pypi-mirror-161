import { Component } from "@angular/core";
import {
    extend,
    NgLifeCycleEvents,
    TupleActionPushService,
} from "@synerty/vortexjs";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import * as moment from "moment";
import { AdminSendTestActivityActionTuple } from "@peek/peek_plugin_inbox/_private";

@Component({
    selector: "active-task-send-test-activity",
    templateUrl: "send-test-activity.component.html",
    styleUrls: ["send-test-activity.component.css"],
})
export class SendTestActivityComponent extends NgLifeCycleEvents {
    activity = {
        uniqueId: null,
        userId: null,
        title: null,
        iconPath: null,
        description: null,
        routePath: null,
        routeParamJson: null,
        autoDeleteDateTime: moment().add(1, "days").format("YYYY-MM-DDTHH:mm"),
    };

    constructor(
        private tupleActionPush: TupleActionPushService,
        private balloonMsg: BalloonMsgService
    ) {
        super();
    }

    send() {
        let activityCopy = extend({}, this.activity);
        activityCopy.autoDeleteDateTime = moment(
            activityCopy.autoDeleteDateTime
        ).toDate();

        let action = new AdminSendTestActivityActionTuple();
        action.formData = activityCopy;
        this.tupleActionPush
            .pushAction(action)
            .then(() =>
                this.balloonMsg.showSuccess("Activity created successfully")
            )
            .catch((e) =>
                this.balloonMsg.showError(`Failed to create activity ${e}`)
            );
    }
}
