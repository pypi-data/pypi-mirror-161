import { enableProdMode } from "@angular/core";
import { platformBrowserDynamic } from "@angular/platform-browser-dynamic";

import { AppModule } from "./app.module";
import { environment } from "./environments/environment";
import { Payload, PayloadDelegateWeb, VortexService } from "@synerty/vortexjs";

const protocol = location.protocol.toLowerCase() == "https:" ? "wss" : "ws";
VortexService.setVortexUrl(
    `${protocol}://${location.hostname}:${location.port}/vortexws`
);
VortexService.setVortexClientName("peek-admin-app");

Payload.setWorkerDelegate(new PayloadDelegateWeb());
if (environment.production) {
    enableProdMode();
}

platformBrowserDynamic().bootstrapModule(AppModule);
