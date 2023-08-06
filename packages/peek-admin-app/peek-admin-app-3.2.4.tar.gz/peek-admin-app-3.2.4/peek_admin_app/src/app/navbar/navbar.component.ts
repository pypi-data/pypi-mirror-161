import { takeUntil } from "rxjs/operators";
import { Component, OnInit } from "@angular/core";
import {
    NgLifeCycleEvents,
    Payload,
    Tuple,
    VortexService,
    VortexStatusService,
} from "@synerty/vortexjs";
import { dashboardRoute } from "../app-routing.module";
import { homeLinks } from "@_peek/plugin-home-links";
import { peekAppEnvironment } from "../../environments/peek-app-environment";

class UserTuple extends Tuple {
    supportExceeded: boolean = false;
    demoExceeded: boolean = true;
    countsExceeded: boolean = true;
    username: string = "None";

    constructor() {
        super("peek_logic_service.PeekAdmNavbarUserTuple");
    }
}

@Component({
    selector: "app-navbar",
    templateUrl: "./navbar.component.html",
    styleUrls: ["./navbar.component.scss"],
})
export class NavbarComponent extends NgLifeCycleEvents implements OnInit {
    readonly appVersion: string = peekAppEnvironment.version;

    dashboardPath: string = dashboardRoute.path;
    user: UserTuple = new UserTuple();
    // Make it public because AppRouterModule uses it as well
    platformMenuData = [];

    // ----------- Load Core Plugin Menu Items
    // Make it public because AppRouterModule uses it as well
    pluginsMenuData = [];

    // ----------- Load Optional Plugin Menu Items
    vortexIsOnline: boolean = false;
    // -------------- Load User Details
    private readonly userDataFilt = {
        plugin: "peek_logic_service",
        key: "nav.adm.user.data",
    };
    private tupleLoader = null;

    constructor(
        vortexStatusService: VortexStatusService,
        private vortexService: VortexService
    ) {
        super();

        for (let homeLink of homeLinks) {
            if (homeLink.name.startsWith("peek_core")) {
                this.platformMenuData.push(homeLink);
            } else {
                this.pluginsMenuData.push(homeLink);
            }
        }

        vortexStatusService.isOnline
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((v) => (this.vortexIsOnline = v));
    }

    ngOnInit() {
        this.tupleLoader = this.vortexService
            .createTupleLoader(this, this.userDataFilt)
            .observable.subscribe(
                (tuples) => (this.user = <UserTuple>tuples[0])
            );
    }

    logoutClicked(): void {
        this.vortexService.sendPayload(
            new Payload(Object.assign({ logout: true }, this.userDataFilt))
        );
        setTimeout(() => location.reload(), 100);
    }
}
