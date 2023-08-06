import { platformBrowserDynamic } from "@angular/platform-browser-dynamic";
import { enableProdMode } from "@angular/core";
import { environment } from "./environments/environment";
import { VortexService } from "@synerty/vortexjs";
import { AppModule } from "./app/app.module";
import { Payload, PayloadDelegateWeb } from "@synerty/vortexjs";

const protocol = location.protocol.toLowerCase() === "https:" ? "wss" : "ws";
VortexService.setVortexUrl(
    `${protocol}://${location.hostname}:${location.port}/vortexws`
);
VortexService.setVortexClientName("peek-office-app");

Payload.setWorkerDelegate(new PayloadDelegateWeb());
if (environment.production) {
    enableProdMode();
}

platformBrowserDynamic().bootstrapModule(AppModule);
