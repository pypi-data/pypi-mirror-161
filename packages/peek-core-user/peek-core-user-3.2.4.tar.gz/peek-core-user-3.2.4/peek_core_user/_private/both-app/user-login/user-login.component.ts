import { BehaviorSubject } from "rxjs";
import { filter, takeUntil } from "rxjs/operators";
import { Router } from "@angular/router";
import {
    UserListItemTuple,
    UserLoginAction,
    UserLoginResponseTuple,
    UserService,
} from "@peek/peek_core_user";
import { UserTupleService } from "@peek/peek_core_user/_private/user-tuple.service";
import { Component } from "@angular/core";
import { NgLifeCycleEvents, TupleSelector } from "@synerty/vortexjs";
import { BalloonMsgService, HeaderService } from "@synerty/peek-plugin-base-js";
import { UserLoginUiSettingTuple } from "../tuples/UserLoginUiSettingTuple";
import { DeviceEnrolmentService } from "@peek/peek_core_device";
import { DeviceOnlineService } from "@peek/peek_core_device/_private";

@Component({
    selector: "./peek-core-user-login",
    templateUrl: "./user-login.component.dweb.html",
    styleUrls: ["../scss/plugin-user.dweb.scss"],
})
export class UserLoginComponent extends NgLifeCycleEvents {
    users: Array<UserListItemTuple> = [];
    selectedUser: UserLoginAction = new UserLoginAction();
    test: any = "";
    errors: string[] = [];
    warnings: string[] = [];
    warningKeys: string[] = [];
    setting: UserLoginUiSettingTuple = new UserLoginUiSettingTuple();
    isAuthenticating$ = new BehaviorSubject<boolean>(false);

    constructor(
        private balloonMsg: BalloonMsgService,
        private deviceEnrolmentService: DeviceEnrolmentService,
        private tupleService: UserTupleService,
        private userService: UserService,
        private router: Router,
        private deviceOnlineService: DeviceOnlineService,
        headerService: HeaderService
    ) {
        super();

        headerService.setTitle("User Login");

        let selectAUser = new UserListItemTuple();
        selectAUser.displayName = "Select a User";

        let ts = new TupleSelector(UserLoginUiSettingTuple.tupleName, {});
        this.tupleService.observer
            .subscribeToTupleSelector(ts)
            .pipe(takeUntil(this.onDestroyEvent))
            .pipe(filter((items) => items.length != 0))
            .subscribe((tuples: UserLoginUiSettingTuple[]) => {
                this.setting = tuples[0];
                if (this.setting.showUsersAsList) this.loadUsersList();
            });
    }

    get isAuthenticating(): boolean {
        return this.isAuthenticating$.getValue();
    }

    set isAuthenticating(value) {
        this.isAuthenticating$.next(value);
    }

    isSelectedUserNull(): boolean {
        return (
            this.selectedUser.userName == null ||
            this.selectedUser.userName === ""
        );
    }

    isUserSelected(item: UserListItemTuple): boolean {
        if (this.isSelectedUserNull()) return false;
        return this.selectedUser.userName == item.userId;
    }

    webDisplayText(item: UserListItemTuple): string {
        if (item.userId == null || item.userId === "") return item.displayName; // For the --select-- case

        return `${item.displayName} (${item.userId})`;
    }

    loginText() {
        return "Login";
    }

    isLoginEnabled(): boolean {
        const isPassSet =
            this.selectedUser.password &&
            this.selectedUser.password.length != 0;

        const isVehicleSet =
            !this.setting.showVehicleInput ||
            (this.selectedUser.vehicleId &&
                this.selectedUser.vehicleId.length != 0) ||
            !this.deviceEnrolmentService.isFieldService();

        return (
            !this.isSelectedUserNull() &&
            !this.isAuthenticating &&
            isPassSet &&
            isVehicleSet
        );
    }

    doLogin() {
        if (!this.isLoginEnabled()) return;

        let tupleAction = this.selectedUser;

        // Add any warnings
        tupleAction.acceptedWarningKeys = this.warningKeys;

        this.isAuthenticating = true;
        this.userService
            .login(tupleAction)
            .then((response: UserLoginResponseTuple) => {
                this.isAuthenticating = false;

                if (response.succeeded) {
                    this.deviceOnlineService.setDeviceOnline();
                    this.balloonMsg.showSuccess("Login Successful");
                    this.router.navigate([""]);
                    return;
                }

                this.balloonMsg.showWarning(
                    "Login Failed, check the warnings and try again"
                );

                this.errors = response.errors;
                this.warnings = [];
                for (let key in response.warnings) {
                    if (!response.warnings.hasOwnProperty(key)) continue;
                    for (let item of response.warnings[key].split("\n")) {
                        this.warnings.push(item);
                    }
                    this.warningKeys.push(key);
                }
            })
            .catch((err) => {
                this.isAuthenticating = false;
                if (err.toString().startsWith("Timed out")) {
                    alert("Login Failed. The server didn't respond.");
                    return;
                } else if (err.toString().length == 0) {
                    alert("An error occurred when logging in.");
                }
                alert(err);
            });
    }

    private loadUsersList(): void {
        let tupleSelector = new TupleSelector(UserListItemTuple.tupleName, {});
        this.tupleService.observer
            .subscribeToTupleSelector(tupleSelector)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: UserListItemTuple[]) => {
                const blank = new UserListItemTuple();
                blank.displayName = "--- select ---";
                this.users = [blank];
                this.users.add(tuples);
                this.users.sort((a, b) =>
                    a.displayName < b.displayName ? -1 : 1
                );
            });
    }
}
