import { Component } from "@angular/core";
import {
    extend,
    NgLifeCycleEvents,
    TupleActionPushService,
} from "@synerty/vortexjs";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import * as moment from "moment";
import { AdminSendTestTaskActionTuple } from "@peek/peek_plugin_inbox/_private";

@Component({
    selector: "active-task-send-test-task",
    templateUrl: "send-test-task.component.html",
    styleUrls: ["send-test-task.component.css"],
})
export class SendTestTaskComponent extends NgLifeCycleEvents {
    task = {
        uniqueId: null,
        userId: null,
        title: null,
        iconPath: null,
        description: null,
        routePath: null,
        routeParamJson: null,
        notificationRequiredFlags: 0,
        notifyByPopup: false,
        notifyBySound: false,
        notifyBySms: false,
        notifyByEmail: false,
        notifyByDialog: false,
        displayAs: 0,
        displayPriority: 1,
        autoComplete: 0,
        autoDelete: 0,
        actions: [],
        autoDeleteDateTime: moment().add(1, "days").format("YYYY-MM-DDTHH:mm"),
    };

    constructor(
        private tupleActionPush: TupleActionPushService,
        private balloonMsg: BalloonMsgService
    ) {
        super();
    }

    addAction() {
        this.task.actions.push({});
    }

    send() {
        this.task.notificationRequiredFlags = 0;

        if (this.task.notifyByPopup) this.task.notificationRequiredFlags += 1;
        if (this.task.notifyBySound) this.task.notificationRequiredFlags += 2;
        if (this.task.notifyBySms) this.task.notificationRequiredFlags += 4;
        if (this.task.notifyByEmail) this.task.notificationRequiredFlags += 8;
        if (this.task.notifyByDialog) this.task.notificationRequiredFlags += 16;

        let taskCopy = extend({}, this.task);
        delete taskCopy.notifyByPopup;
        delete taskCopy.notifyBySound;
        delete taskCopy.notifyBySms;
        delete taskCopy.notifyByEmail;
        delete taskCopy.notifyByDialog;
        taskCopy.autoDeleteDateTime = moment(
            taskCopy.autoDeleteDateTime
        ).toDate();
        taskCopy.displayAs = parseInt(taskCopy.displayAs);
        taskCopy.displayPriority = parseInt(taskCopy.displayPriority);

        let action = new AdminSendTestTaskActionTuple();
        action.formData = taskCopy;
        this.tupleActionPush
            .pushAction(action)
            .then(() =>
                this.balloonMsg.showSuccess("Task created successfully")
            )
            .catch((e) =>
                this.balloonMsg.showError(`Failed to create task ${e}`)
            );
    }
}
