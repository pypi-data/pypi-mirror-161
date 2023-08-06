import { takeUntil } from "rxjs/operators";
import { Component } from "@angular/core";
import {
    NgLifeCycleEvents,
    TupleDataObserverService,
    TupleSelector,
} from "@synerty/vortexjs";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { AdminStatusTuple } from "../tuples/AdminStatusTuple";

@Component({
    selector: "pl-eventdb-status",
    templateUrl: "./status.component.html",
})
export class StatusComponent extends NgLifeCycleEvents {
    item: AdminStatusTuple = new AdminStatusTuple();

    constructor(
        private balloonMsg: BalloonMsgService,
        private tupleObserver: TupleDataObserverService
    ) {
        super();

        let ts = new TupleSelector(AdminStatusTuple.tupleName, {});
        this.tupleObserver
            .subscribeToTupleSelector(ts)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: AdminStatusTuple[]) => (this.item = tuples[0]));
    }
}
