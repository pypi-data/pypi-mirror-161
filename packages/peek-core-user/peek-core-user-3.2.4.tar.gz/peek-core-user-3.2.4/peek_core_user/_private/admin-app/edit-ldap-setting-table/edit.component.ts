import { Component } from "@angular/core";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import {
    extend,
    NgLifeCycleEvents,
    TupleLoader,
    VortexService,
} from "@synerty/vortexjs";
import { userFilt } from "@peek/peek_core_user/_private";
import { LdapSettingTuple } from "../tuples/LdapSettingTuple";

@Component({
    selector: "pl-user-edit-ldap-setting",
    templateUrl: "./edit.component.html",
})
export class EditLdapSettingComponent extends NgLifeCycleEvents {
    items: LdapSettingTuple[] = [];
    itemsToDelete: LdapSettingTuple[] = [];
    loader: TupleLoader;

    // This must match the dict defined in the admin_backend handler
    private readonly filt = {
        key: "admin.Edit.LdapSetting",
    };

    constructor(
        private balloonMsg: BalloonMsgService,
        vortexService: VortexService
    ) {
        super();

        this.loader = vortexService.createTupleLoader(
            this,
            extend({}, this.filt, userFilt)
        );

        this.loader.observable.subscribe((tuples: LdapSettingTuple[]) => {
            this.items = tuples;
            this.itemsToDelete = [];
        });
    }

    addRow() {
        let t = new LdapSettingTuple();
        // Add any values needed for this list here, EG, for a lookup list you might add:
        // t.lookupName = this.lookupName;
        this.items.push(t);
    }

    removeRow(item) {
        if (item.id != null) this.itemsToDelete.push(item);

        let index: number = this.items.indexOf(item);
        if (index !== -1) {
            this.items.splice(index, 1);
        }
    }

    save() {
        let itemsToDelete = this.itemsToDelete;

        this.loader
            .save(this.items)
            .then(() => {
                if (itemsToDelete.length != 0) {
                    return this.loader.del(itemsToDelete);
                }
            })
            .then(() => this.balloonMsg.showSuccess("Save Successful"))
            .catch((e) => this.balloonMsg.showError(e));
    }
}
