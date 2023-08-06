import { takeUntil } from "rxjs/operators";
import { Component, EventEmitter, Input, OnInit, Output } from "@angular/core";
import { EventDBPropertyTuple } from "@peek/peek_plugin_eventdb/tuples";
import { PrivateEventDBService } from "@peek/peek_plugin_eventdb/_private/PrivateEventDBService";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";

export interface ColumnI {
    selectedProps: EventDBPropertyTuple[];
}

@Component({
    selector: "plugin-eventdb-event-column",
    templateUrl: "event-column.component.web.html",
    styleUrls: ["../event-common.component.web.scss"],
})
export class EventDBColumnComponent
    extends NgLifeCycleEvents
    implements OnInit
{
    @Input("modelSetKey")
    modelSetKey: string;

    @Output("columnChange")
    columnChange = new EventEmitter<ColumnI>();

    isVisible = false;
    isOkLoading = false;
    allProps: EventDBPropertyTuple[] = [];
    selectedProps: EventDBPropertyTuple[] = [];
    private propByKey: { [key: string]: EventDBPropertyTuple } = {};
    private lastRouteParams: string | null = null;

    constructor(
        private balloonMsg: BalloonMsgService,
        private eventService: PrivateEventDBService
    ) {
        super();
    }

    get columnPropKeys(): string[] {
        const result = [];
        for (let prop of this.selectedProps) {
            result.push(prop.key);
        }
        return result;
    }

    get paramsForRoute(): string {
        const propKeys = [];
        for (let prop of this.selectedProps) {
            propKeys.push(prop.key);
        }
        return propKeys.join();
    }

    set paramsForRoute(params: string) {
        this.lastRouteParams = params;
        // Give the change detection a chance to run
        setTimeout(() => this.applyRouteParams(), 100);
    }

    ngOnInit() {
        this.eventService
            .propertyTuples(this.modelSetKey)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((props: EventDBPropertyTuple[]) => {
                this.allProps = props
                    .filter((prop) => prop.useForDisplay)
                    .sort((a, b) => a.order - b.order);

                this.propByKey = {};
                for (let prop of this.allProps) {
                    this.propByKey[prop.key] = prop;
                }

                // Give the change detection a chance to run
                setTimeout(() => this.applyRouteParams(), 100);
            });
    }

    showModal(): void {
        this.isVisible = true;
    }

    onOkClicked(): void {
        this.isOkLoading = true;

        this.updateColumns();

        setTimeout(() => {
            this.isVisible = false;
            this.isOkLoading = false;
        }, 500);
    }

    resetDefaults(): void {
        this.isOkLoading = true;

        this.selectedProps = this.allProps.filter(
            (prop) => prop.displayByDefaultOnDetailView
        );
    }

    onCancelClicked(): void {
        this.selectedProps = [];
        this.isVisible = false;
    }

    private applyRouteParams() {
        if (this.allProps.length == 0) return;

        if (this.lastRouteParams == null) return;

        if (this.lastRouteParams.length == 0) {
            this.selectedProps = this.allProps.filter(
                (prop) => prop.displayByDefaultOnDetailView
            );
        } else {
            const propKeys = this.lastRouteParams.split(",");
            this.selectedProps = [];

            for (let propKey of propKeys) {
                const prop: EventDBPropertyTuple = this.propByKey[propKey];
                if (prop == null) continue;

                this.selectedProps.push(prop);
            }
        }

        // Clear the route data
        this.lastRouteParams = null;

        // Update the filter
        this.updateColumns();
    }

    private updateColumns() {
        this.columnChange.emit({
            selectedProps: this.selectedProps,
        });
    }
}
