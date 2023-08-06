import { takeUntil } from "rxjs/operators";
import { Component } from "@angular/core";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import {
    extend,
    NgLifeCycleEvents,
    TupleDataObserverService,
    TupleLoader,
    TupleSelector,
    VortexService,
} from "@synerty/vortexjs";
import { eventdbFilt } from "../PluginNames";
import { EventDBPropertyTableTuple } from "../tuples/EventDBPropertyTableTuple";
import { EventDBModelSetTableTuple } from "../tuples/EventDBModelSetTableTuple";
import { EventDBPropertyValueTableTuple } from "../tuples/EventDBPropertyValueTableTuple";

@Component({
    selector: "pl-eventdb-edit-property",
    templateUrl: "./edit.component.html",
    styles: [
        `
            nz-select {
                min-width: 110pt;
            }
        `,
    ],
})
export class EditPropertyComponent extends NgLifeCycleEvents {
    modelSets: EventDBModelSetTableTuple[] = [];
    items: EventDBPropertyTableTuple[] = [];
    loader: TupleLoader;
    showFilterAsOptions = [
        { num: 1, text: "Free Text" },
        { num: 2, text: "Select Many" },
        { num: 3, text: "Select One" },
    ];
    // This must match the dict defined in the admin_backend handler
    private readonly filt = {
        key: "admin.Edit.EventDBPropertyTuple",
    };

    constructor(
        private balloonMsg: BalloonMsgService,
        vortexService: VortexService,
        private tupleObserver: TupleDataObserverService
    ) {
        super();

        this.loader = vortexService.createTupleLoader(this, () =>
            extend({}, this.filt, eventdbFilt)
        );

        this.loader.observable.subscribe(
            (tuples: EventDBPropertyTableTuple[]) => {
                this.items = tuples;
                for (let item of this.items) {
                    item.uiExpandValues = false;
                }
            }
        );

        let ts = new TupleSelector(EventDBModelSetTableTuple.tupleName, {});
        this.tupleObserver
            .subscribeToTupleSelector(ts)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: EventDBModelSetTableTuple[]) => {
                this.modelSets = tuples.sort((a, b) =>
                    a.name < b.name ? -1 : a.name > b.name ? 1 : 0
                );
            });
    }

    addClicked() {
        let newItem = new EventDBPropertyTableTuple();
        newItem.modelSetId = this.modelSets[0].id;
        newItem.order = 0;
        newItem.showFilterAs = 1;
        this.items = [...this.items, newItem];
    }

    removeClicked(itemIndex: number) {
        this.items = this.items.splice(itemIndex - 1, 1);
    }

    saveClicked() {
        for (let item of this.items) {
            if (!item.isValid) {
                this.balloonMsg.showWarning(
                    "Some properties are invalid, please fix them"
                );
                return;
            }
            if (!item.enableValues) item.valuesFromAdminUi = [];
        }
        this.loader
            .save(this.items)
            .then(() => this.balloonMsg.showSuccess("Save Successful"))
            .catch((e) => this.balloonMsg.showError(e));
    }

    resetClicked() {
        this.loader
            .load()
            .then(() => this.balloonMsg.showSuccess("Reset Successful"))
            .catch((e) => this.balloonMsg.showError(e));
    }

    addValueClicked(item: EventDBPropertyTableTuple) {
        if (item.valuesFromAdminUi == null) item.valuesFromAdminUi = [];

        let newItem = new EventDBPropertyValueTableTuple();
        item.valuesFromAdminUi = [...item.valuesFromAdminUi, newItem];
    }

    removeValueClicked(item: EventDBPropertyTableTuple, itemIndex: number) {
        item.valuesFromAdminUi = item.valuesFromAdminUi.splice(
            itemIndex - 1,
            1
        );
    }
}
