import { takeUntil } from "rxjs/operators";
import { Component, OnInit } from "@angular/core";
import { BalloonMsgService, HeaderService } from "@synerty/peek-plugin-base-js";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import {
    DeviceNavService,
    DeviceServerService,
    DeviceTupleService,
    ServerInfoTuple,
} from "@peek/peek_core_device/_private";
import { DeviceTypeEnum } from "@peek/peek_core_device/_private/hardware-info/hardware-info";
import { Capacitor } from "@capacitor/core";

@Component({
    selector: "core-device-enroll",
    templateUrl: "connect.component.web.html",
})
export class ConnectComponent extends NgLifeCycleEvents implements OnInit {
    server: ServerInfoTuple = new ServerInfoTuple();
    httpPortStr: string = ServerInfoTuple.DEFAULT_HTTP_PORT.toString();
    websocketPortStr: string =
        ServerInfoTuple.DEFAULT_WEBSOCKET_PORT.toString();
    deviceType: DeviceTypeEnum;
    isWeb: boolean;
    platform: string;

    constructor(
        private balloonMsg: BalloonMsgService,
        private headerService: HeaderService,
        private tupleService: DeviceTupleService,
        private nav: DeviceNavService,
        private deviceServerService: DeviceServerService
    ) {
        super();
        this.platform = Capacitor.getPlatform();
        this.deviceType = this.tupleService.hardwareInfo.deviceType();
        this.isWeb = this.tupleService.hardwareInfo.isWeb();

        this.deviceServerService.connInfoObserver
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((info: ServerInfoTuple) => {
                this.server = info;
            });

        // Make sure we're not on this page when things are fine.
        let sub = this.doCheckEvent
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe(() => {
                if (this.deviceServerService.isConnected) {
                    this.nav.toEnroll();
                    sub.unsubscribe();
                } else if (this.deviceServerService.isSetup) {
                    this.nav.toConnecting();
                    sub.unsubscribe();
                }
            });
    }

    ngOnInit() {
        this.headerService.setEnabled(false);
        this.headerService.setTitle("");
    }

    connectEnabled(): boolean {
        if (this.server != null) {
            if (this.server.host == null || !this.server.host.length)
                return false;

            if (!parseInt(this.websocketPortStr)) return false;

            if (!parseInt(this.httpPortStr)) return false;
        }
        return true;
    }

    connectClicked() {
        try {
            this.server.httpPort = parseInt(this.httpPortStr);
            this.server.websocketPort = parseInt(this.websocketPortStr);
        } catch (e) {
            this.balloonMsg.showError("Port numbers must be integers.");
            return;
        }

        this.deviceServerService
            .setServer(this.server)
            .then(() => this.nav.toConnecting());
    }

    setUseSsl(val: boolean) {
        this.server.useSsl = val;
    }
}
