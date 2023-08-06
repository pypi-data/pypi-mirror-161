import { Component } from "@angular/core";
import {
    extend,
    NgLifeCycleEvents,
    TupleLoader,
    VortexService,
} from "@synerty/vortexjs";
import {
    docDbGenericMenuFilt,
    DocDbGenericMenuTuple,
} from "@peek/peek_plugin_docdb_generic_menu/_private";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";

@Component({
    selector: "pl-docdb-generic-menu-edit-docdb-generic-menu",
    templateUrl: "./edit.component.html",
})
export class EditDocDbGenericMenuComponent extends NgLifeCycleEvents {
    items: DocDbGenericMenuTuple[] = [];
    itemsToDelete: DocDbGenericMenuTuple[] = [];
    loader: TupleLoader;
    // This must match the dict defined in the admin_backend handler
    private readonly filt = {
        key: "admin.Edit.DocDbGenericMenuTuple",
    };

    constructor(
        vortexService: VortexService,
        private balloonMsg: BalloonMsgService
    ) {
        super();

        this.loader = vortexService.createTupleLoader(
            this,
            extend({}, this.filt, docDbGenericMenuFilt)
        );

        this.loader.observable.subscribe((tuples: DocDbGenericMenuTuple[]) => {
            this.items = tuples;
            this.itemsToDelete = [];
        });
    }

    addRow() {
        let t = new DocDbGenericMenuTuple();
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
        for (const item of this.items) {
            if (item.showCondition != null && item.showCondition.length != 0) {
                if (
                    item.showCondition.indexOf("==") == -1 &&
                    item.showCondition.indexOf("!=") == -1
                ) {
                    this.balloonMsg.showWarning(
                        "Failed to save, all conditions that are" +
                            " set must have '==' or '!=' in them"
                    );
                    return;
                }
            }

            if (item.url == null || item.url.length == 0) {
                this.balloonMsg.showWarning(
                    "Failed to save, all menus must have a url set"
                );
                return;
            }
        }

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
