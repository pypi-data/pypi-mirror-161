import { Component } from "@angular/core";
import {
    NgLifeCycleEvents,
    VortexService,
    VortexStatusService,
} from "@synerty/vortexjs";

interface Stat {
    desc: string;
    value: string;
}

@Component({
    selector: "app-dashboard-stats",
    templateUrl: "./dashboard-stats.component.html",
    styleUrls: ["./dashboard-stats.component.scss"],
})
export class DashboardStatsComponent extends NgLifeCycleEvents {
    private readonly statsFilt = {
        plugin: "peek_logic_service",
        key: "peakadm.dashboard.list.data",
    };

    // stats: Stat[] = [];
    // loader: TupleLoader;

    constructor(
        vortexService: VortexService,
        vortexStatus: VortexStatusService
    ) {
        super();

        // this.loader = vortexService.createTupleLoader(this, this.statsFilt);
        //
        //
        // vortexStatus
        //   .isOnline
        //   .pipe(filter(online => online))
        //   .pipe(first())
        //   .subscribe(() => {
        //     this.loader.observable.subscribe(
        //       tuples => {
        //         this.stats = <Stat[]>tuples;
        //         this.stats.sort((a, b) => {
        //           return (<Stat>a).desc.localeCompare((<Stat>b).desc);
        //         });
        //       });
        //   });
    }
}
