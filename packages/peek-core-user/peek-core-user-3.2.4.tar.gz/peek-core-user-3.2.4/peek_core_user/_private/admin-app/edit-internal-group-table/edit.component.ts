import { Component } from "@angular/core";
import {
    extend,
    NgLifeCycleEvents,
    TupleLoader,
    VortexService,
} from "@synerty/vortexjs";
import { userFilt } from "@peek/peek_core_user/_private";
import { InternalGroupTuple } from "../tuples/InternalGroupTuple";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";

@Component({
    selector: "pl-user-edit-internal-group",
    templateUrl: "./edit.component.html",
})
export class EditInternalGroupComponent extends NgLifeCycleEvents {
    items: InternalGroupTuple[] = [];
    itemsToDelete: InternalGroupTuple[] = [];
    loader: TupleLoader;

    // This must match the dict defined in the admin_backend handler
    private readonly filt = {
        key: "admin.Edit.InternalGroupTuple",
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

        this.loader.observable.subscribe((tuples: InternalGroupTuple[]) => {
            this.items = tuples;
            this.itemsToDelete = [];
        });
    }

    addRow() {
        let t = new InternalGroupTuple();
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
