import { Component } from "@angular/core";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import {
    extend,
    NgLifeCycleEvents,
    TupleLoader,
    VortexService,
} from "@synerty/vortexjs";
import {
    BranchDetailTuple,
    branchFilt,
} from "@peek/peek_plugin_branch/_private";

@Component({
    selector: "pl-branch-edit-branch-detail",
    templateUrl: "./edit.component.html",
})
export class EditBranchDetailComponent extends NgLifeCycleEvents {
    items: BranchDetailTuple[] = [];
    itemsToDelete: BranchDetailTuple[] = [];
    loader: TupleLoader;
    // This must match the dict defined in the admin_backend handler
    private readonly filt = {
        key: "admin.Edit.BranchDetailTable",
    };

    constructor(
        private balloonMsg: BalloonMsgService,
        vortexService: VortexService
    ) {
        super();

        this.loader = vortexService.createTupleLoader(this, () => {
            let filt = extend({}, this.filt, branchFilt);
            // If we wanted to filter the data we get, we could add this
            // filt["lookupName"] = 'lookupType';
            return filt;
        });

        this.loader.observable.subscribe((tuples: BranchDetailTuple[]) => {
            this.items = tuples;
            this.itemsToDelete = [];
        });
    }

    addRow() {
        let t = new BranchDetailTuple();
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

    resetClicked() {
        this.loader
            .load()
            .then(() => this.balloonMsg.showSuccess("Reset Successful"))
            .catch((e) => this.balloonMsg.showError(e));
    }
}
