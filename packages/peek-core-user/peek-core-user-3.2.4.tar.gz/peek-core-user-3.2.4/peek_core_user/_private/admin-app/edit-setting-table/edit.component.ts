import { Component } from "@angular/core";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import {
    extend,
    NgLifeCycleEvents,
    TupleLoader,
    VortexService,
} from "@synerty/vortexjs";
import { userFilt } from "@peek/peek_core_user/_private";
import { SettingPropertyTuple } from "../tuples/SettingPropertyTuple";

@Component({
    selector: "pl-user-edit-setting",
    templateUrl: "./edit.component.html",
})
export class EditSettingComponent extends NgLifeCycleEvents {
    items: SettingPropertyTuple[] = [];
    loader: TupleLoader;
    settingsType: string = "Global";

    // This must match the dict defined in the admin_backend handler
    private readonly filt = {
        key: "admin.Edit.SettingProperty",
    };

    constructor(
        private balloonMsg: BalloonMsgService,
        vortexService: VortexService
    ) {
        super();

        this.loader = vortexService.createTupleLoader(this, () =>
            extend({ settingType: this.settingsType }, this.filt, userFilt)
        );

        this.loader.observable.subscribe(
            (tuples: SettingPropertyTuple[]) => (this.items = tuples)
        );
    }

    saveClicked() {
        this.loader
            .save()
            .then(() => this.balloonMsg.showSuccess("Save Successful"))
            .catch((e) => this.balloonMsg.showError(e));
    }

    resetClicked() {
        this.loader
            .load()
            .then(() => this.balloonMsg.showSuccess("Reset Successful"))
            .catch((e) => this.balloonMsg.showError(e));
    }

    settingTypeChanged() {
        this.loader.load();
    }
}
