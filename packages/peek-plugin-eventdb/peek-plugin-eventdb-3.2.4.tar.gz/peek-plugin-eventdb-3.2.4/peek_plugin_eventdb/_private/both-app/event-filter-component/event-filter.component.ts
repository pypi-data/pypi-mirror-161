import { first, takeUntil } from "rxjs/operators";
import { Component, EventEmitter, Input, OnInit, Output } from "@angular/core";
import { PrivateEventDBService } from "@peek/peek_plugin_eventdb/_private/PrivateEventDBService";
import {
    EventDBPropertyCriteriaTuple,
    EventDBPropertyShowFilterAsEnum,
    EventDBPropertyTuple,
} from "@peek/peek_plugin_eventdb/tuples";
import { NgLifeCycleEvents, SerialiseUtil } from "@synerty/vortexjs";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { EventDateTimeRangeI } from "@peek/peek_plugin_eventdb";

import * as moment from "moment";

export interface FilterI {
    modelSetKey: string;
    alarmsOnly: boolean;
    dateTimeRange: EventDateTimeRangeI;
    criteria: EventDBPropertyCriteriaTuple[];
}

export interface RouteFilterI {
    live: boolean;
    alarmsOnly: boolean;
    cri: { [key: string]: string | string[] };
    from: string;
    to: string;
}

@Component({
    selector: "plugin-eventdb-event-filter",
    templateUrl: "event-filter.component.web.html",
    styleUrls: [
        "event-filter.component.web.scss",
        "../event-common.component.web.scss",
    ],
})
export class EventDBFilterComponent
    extends NgLifeCycleEvents
    implements OnInit
{
    @Input("modelSetKey")
    modelSetKey: string;

    @Output("filterChange")
    filterChange = new EventEmitter<FilterI>();

    isVisible = false;
    isOkLoading = false;
    filterProps: EventDBPropertyTuple[] = [];
    dateTimeRange: EventDateTimeRangeI;
    liveEnabled: boolean = true;
    alarmsOnlyEnabled: boolean = false;
    FilterAsEnum = EventDBPropertyShowFilterAsEnum;
    private allProps: EventDBPropertyTuple[] = [];
    private propByKey: { [key: string]: EventDBPropertyTuple } = {};
    private criteriaByPropKey: { [key: string]: EventDBPropertyCriteriaTuple } =
        {};
    private selectedCriterias: EventDBPropertyCriteriaTuple[] = [];
    private liveUpdateTimer: any;
    private lastFilter: FilterI;
    private lastRouteParams: RouteFilterI | null = null;

    constructor(
        private balloonMsg: BalloonMsgService,
        private eventService: PrivateEventDBService
    ) {
        super();
    }

    get filter(): FilterI {
        return this.lastFilter;
    }

    get paramsForRoute(): RouteFilterI {
        const tsUtil = new SerialiseUtil();
        const cri = {};
        for (let item of this.selectedCriterias) {
            cri[item.property.key] = item.value;
        }

        function dateToStr(dateIn) {
            if (dateIn == null) return null;
            return tsUtil.toStr(dateIn);
        }

        return {
            live: this.liveEnabled,
            alarmsOnly: this.alarmsOnlyEnabled,
            cri: cri,
            from: dateToStr(this.dateTimeRange.oldestDateTime),
            to: dateToStr(this.dateTimeRange.newestDateTime),
        };
    }

    set paramsForRoute(params: RouteFilterI) {
        this.lastRouteParams = params;

        // Give the change detection a chance to run
        setTimeout(() => this.applyRouteParams(), 100);
    }

    ngOnInit() {
        this.dateTimeRange = {
            oldestDateTime: this.defaultOldestDateTime(),
            newestDateTime: null,
        };

        this.eventService
            .propertyTuples(this.modelSetKey)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((props: EventDBPropertyTuple[]) => {
                this.allProps = props;

                // filter for default filter properties.
                this.filterProps = this.allProps
                    .filter((prop) => prop.useForFilter)
                    .sort((a, b) => a.order - b.order);

                this.propByKey = {};
                for (let prop of this.filterProps) {
                    this.propByKey[prop.key] = prop;
                }

                // Give the change detection a chance to run
                setTimeout(() => this.applyRouteParams(), 100);
            });

        // Setup a timer to update the last hour of data.
        // If someone leaves the alarm list over night, the earliest date won't update.
        this.liveUpdateTimer = setInterval(
            () => this.liveEnabledUpdateTimerCall(),
            10 * 60 * 1000
        );

        this.onDestroyEvent
            .pipe(first())
            .subscribe(() => clearInterval(this.liveUpdateTimer));
    }

    updateLive(liveEnabled: boolean): void {
        this.liveEnabled = liveEnabled;

        if (this.liveEnabled) {
            this.liveEnabledUpdateTimerCall();
        } else if (this.dateTimeRange.newestDateTime == null) {
            this.dateTimeRange.newestDateTime = moment().toDate();
            this.updateFilter();
        }
    }

    updateAlarmsOnly(alarmsOnlyEnabled: boolean): void {
        this.alarmsOnlyEnabled = alarmsOnlyEnabled;
        this.updateFilter();
    }

    criteria(prop: EventDBPropertyTuple): EventDBPropertyCriteriaTuple {
        if (this.criteriaByPropKey[prop.key] == null) {
            this.criteriaByPropKey[prop.key] =
                new EventDBPropertyCriteriaTuple();
            this.criteriaByPropKey[prop.key].property = prop;
        }
        return this.criteriaByPropKey[prop.key];
    }

    showModal(): void {
        this.isVisible = true;
    }

    onOkClicked(): void {
        const P = EventDBPropertyShowFilterAsEnum;
        this.isOkLoading = true;

        if (!this.liveEnabled) {
            if (this.dateTimeRange.oldestDateTime == null)
                this.dateTimeRange.oldestDateTime =
                    this.defaultOldestDateTime();

            if (this.dateTimeRange.newestDateTime == null)
                this.dateTimeRange.newestDateTime = moment().toDate();
        }

        this.selectedCriterias = [];
        for (let key of Object.keys(this.criteriaByPropKey)) {
            const criteria = this.criteriaByPropKey[key];

            // Don't add if value is blank.
            if (criteria.value == null || criteria.value.length == 0) continue;

            // These criteria types should both be arrays, make it so.
            if (
                criteria.property.showFilterAs == P.SHOW_FILTER_SELECT_MANY ||
                criteria.property.showFilterAs == P.SHOW_FILTER_SELECT_ONE
            ) {
                if (typeof criteria.value === "string") {
                    criteria.value = [criteria.value];
                }
            }

            // Add the Selected Criteria to the list
            this.selectedCriterias.push(criteria);
        }

        this.updateFilter();

        setTimeout(() => {
            this.isVisible = false;
            this.isOkLoading = false;
        }, 500);
    }

    resetDefaults(): void {
        this.criteriaByPropKey = {};
    }

    onCancelClicked(): void {
        this.isVisible = false;
    }

    private applyRouteParams() {
        if (this.allProps.length == 0) return;

        if (this.lastRouteParams == null) return;

        const tsUtil = new SerialiseUtil();

        // Reset the class data
        this.selectedCriterias = [];
        this.criteriaByPropKey = {};

        // Load in the criteria
        for (let propKey of Object.keys(this.lastRouteParams.cri || {})) {
            const prop: EventDBPropertyTuple = this.propByKey[propKey];
            if (prop == null) continue;

            const val = this.lastRouteParams.cri[prop.key];

            const criteria = this.criteria(prop);
            criteria.value = val;
            this.selectedCriterias.push(criteria);
        }

        // Load in the from/to datetimes
        function nullOrDateStr(strIn) {
            if (strIn == null) return null;
            return tsUtil.fromStr(strIn, SerialiseUtil.T_DATETIME);
        }

        if (
            this.lastRouteParams.from != null ||
            this.lastRouteParams.to != null
        ) {
            this.dateTimeRange = {
                oldestDateTime: nullOrDateStr(this.lastRouteParams.from),
                newestDateTime: nullOrDateStr(this.lastRouteParams.to),
            };
        }

        // Set the livedb value, null or true is true (default to true)
        this.liveEnabled = this.lastRouteParams.live !== false;

        // Set the livedb value, null or true is true (default to true)
        this.alarmsOnlyEnabled = this.lastRouteParams.alarmsOnly !== false;

        // Clear the route data
        this.lastRouteParams = null;

        // Update the filter
        this.updateFilter();
    }

    // noinspection JSMethodCanBeStatic
    private defaultOldestDateTime(): Date {
        // Round the datetime to the nearest 5 minutes.
        // This will help to reduce the calls for people just watching the events.
        let newDate = moment().subtract(2, "hours");
        let minute = newDate.minute();
        newDate = newDate.millisecond(0);
        newDate = newDate.seconds(0);
        newDate = newDate.minute(minute - (minute % 5));
        return newDate.toDate();
    }

    private liveEnabledUpdateTimerCall(): void {
        if (!this.liveEnabled) return;

        this.dateTimeRange = {
            oldestDateTime: this.defaultOldestDateTime(),
            newestDateTime: null,
        };

        this.updateFilter();
    }

    private updateFilter() {
        this.lastFilter = {
            modelSetKey: this.modelSetKey,
            alarmsOnly: this.alarmsOnlyEnabled,
            dateTimeRange: this.dateTimeRange,
            criteria: this.selectedCriterias,
        };
        this.filterChange.emit(this.lastFilter);
    }
}
