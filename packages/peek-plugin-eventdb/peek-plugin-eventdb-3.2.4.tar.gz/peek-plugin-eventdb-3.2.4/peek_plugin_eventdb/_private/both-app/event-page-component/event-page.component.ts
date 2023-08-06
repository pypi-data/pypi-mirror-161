import { takeUntil } from "rxjs/operators";
import { AfterViewInit, Component, ViewChild } from "@angular/core";
import { jsonOrderedStringify, NgLifeCycleEvents } from "@synerty/vortexjs";
import { HeaderService } from "@synerty/peek-plugin-base-js";
import { EventDBColumnComponent } from "../event-column-component/event-column.component";
import { EventDBFilterComponent } from "../event-filter-component/event-filter.component";
import { ActivatedRoute, Params, Router } from "@angular/router";
import { EventDBEventListComponent } from "../event-list-component/event-list.component";
import { PrivateEventDBService } from "@peek/peek_plugin_eventdb/_private/PrivateEventDBService";

@Component({
    selector: "plugin-eventdb-event-page",
    templateUrl: "event-page.component.web.html",
    styleUrls: ["../event-common.component.web.scss"],
})
export class EventDBPageComponent
    extends NgLifeCycleEvents
    implements AfterViewInit
{
    @ViewChild("eventFilter", { static: true })
    eventFilter: EventDBFilterComponent;

    @ViewChild("eventColumns", { static: true })
    eventColumns: EventDBColumnComponent;

    @ViewChild("eventList", { static: true })
    eventList: EventDBEventListComponent;

    modelSetKey = "pofDiagram";

    private routeUpdateTimer: any | null = null;

    constructor(
        private headerService: HeaderService,
        private route: ActivatedRoute,
        private router: Router,
        private eventService: PrivateEventDBService
    ) {
        super();

        headerService.setTitle("Alarm and Events");
    }

    get downloadUrl(): string {
        const columnPropKeys = this.eventColumns.columnPropKeys;
        const filter = this.eventFilter.filter;
        if (filter == null) return "";

        const tupleSelector = this.eventService.eventTupleSelector(
            this.modelSetKey,
            filter.dateTimeRange,
            filter.criteria,
            filter.alarmsOnly
        );
        tupleSelector.selector["columnPropKeys"] = columnPropKeys;

        return (
            "/peek_plugin_eventdb/download/events?tupleSelector=" +
            encodeURIComponent(tupleSelector.toOrderedJsonStr())
        );
    }

    ngAfterViewInit() {
        this.route.params
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((params: Params) => {
                let vars = {};

                if (typeof window !== "undefined") {
                    window.location.href.replace(
                        /[?&]+([^=&]+)=([^&]*)/gi,
                        (m, key, value) => (vars[key] = value)
                    );
                }

                let columns = params["columns"] || vars["columns"] || "";
                let filter = params["filter"] || vars["filter"] || "{}";
                const modelSetKey =
                    params["modelSetKey"] ||
                    vars["modelSetKey"] ||
                    this.modelSetKey; // HARDCODED
                const color = (params["color"] || vars["color"]) == "true";

                if (modelSetKey == null) return;

                filter = JSON.parse(filter);

                this.modelSetKey = modelSetKey;
                this.eventColumns.paramsForRoute = columns;
                this.eventFilter.paramsForRoute = filter;

                // Give the change detection a chance to run
                setTimeout(() => this.eventList.updateColors(color), 100);
            });
    }

    updateRoute(): void {
        // Delay updating to 500ms after the last reason to update the params.
        if (this.routeUpdateTimer != null) clearTimeout(this.routeUpdateTimer);
        this.routeUpdateTimer = setTimeout(() => this._updateRoute(), 500);
    }

    private _updateRoute(): void {
        this.routeUpdateTimer = null;

        let url = this.router.url.split(";")[0];

        // Sometimes it can try to position after we've navigated away
        if (url.indexOf("peek_plugin_eventdb") == -1) return;

        const params = {
            color: this.eventList.colorsEnabled,
            modelSetKey: this.modelSetKey,
            filter: jsonOrderedStringify(this.eventFilter.paramsForRoute),
            columns: this.eventColumns.paramsForRoute,
        };

        this.router.navigate([url, params]);
    }
}
