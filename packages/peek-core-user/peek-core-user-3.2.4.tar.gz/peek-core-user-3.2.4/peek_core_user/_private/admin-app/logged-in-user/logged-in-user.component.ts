import { takeUntil } from "rxjs/operators";
import { Component } from "@angular/core";
import {
    BalloonMsgLevel,
    BalloonMsgService,
    BalloonMsgType,
} from "@synerty/peek-plugin-base-js";
import {
    NgLifeCycleEvents,
    TupleActionPushService,
    TupleDataObserverService,
    TupleSelector,
} from "@synerty/vortexjs";
import {
    UserLogoutAction,
    UserLogoutResponseTuple,
} from "@peek/peek_core_user/tuples";
import { LoggedInUserStatusTuple } from "@peek/peek_core_user/_private";

@Component({
    selector: "pl-user-manage-logged-in-user",
    templateUrl: "./logged-in-user.component.html",
})
export class ManageLoggedInUserComponent extends NgLifeCycleEvents {
    items: LoggedInUserStatusTuple[] = [];

    constructor(
        private balloonMsg: BalloonMsgService,
        private actionService: TupleActionPushService,
        private tupleDataObserver: TupleDataObserverService
    ) {
        super();

        // Setup a subscription for the data
        const ts = new TupleSelector(LoggedInUserStatusTuple.tupleName, {});
        tupleDataObserver
            .subscribeToTupleSelector(ts)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: LoggedInUserStatusTuple[]) => {
                this.items = tuples;
            });
    }

    logoutUser(item: LoggedInUserStatusTuple) {
        let action = new UserLogoutAction();
        action.userName = item.userName;
        action.deviceToken = item.deviceToken;
        action.acceptedWarningKeys = [];

        console.log(action);

        this.balloonMsg
            .showMessage(
                "Are you sure you'd like to logout this user?",
                BalloonMsgLevel.Warning,
                BalloonMsgType.ConfirmCancel,
                { confirmText: "Yes", cancelText: "No" }
            )
            .then(() => {
                this.actionService
                    .pushAction(action)
                    .then((tuples: UserLogoutResponseTuple[]) => {
                        let one = tuples[0];
                        if (one.succeeded == true) {
                            this.balloonMsg.showSuccess("Logout Successful");
                            return;
                        }

                        if (one.errors.length != 0) {
                            this.balloonMsg.showError(
                                `Failed to logout user ${one.errors}`
                            );
                            return;
                        }

                        action.acceptedWarningKeys = Object.keys(one.warnings);

                        return this.actionService
                            .pushAction(action)
                            .then((tuples: UserLogoutResponseTuple[]) => {
                                let two = tuples[0];
                                if (two.succeeded == true) {
                                    this.balloonMsg.showSuccess(
                                        "Logout Successful"
                                    );
                                    return;
                                }
                                this.balloonMsg.showError(
                                    `Failed to logout user.`
                                );
                            });
                    })
                    .catch((e) => this.balloonMsg.showError(e));
            });
    }
}
