import { Component } from "@angular/core";
import { HeaderService } from "@synerty/peek-plugin-base-js";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import {
    DeviceOfflineCacheService,
    OfflineCacheStatusTuple,
} from "@peek/peek_core_device";
import { DeviceTupleService } from "@peek/peek_core_device/_private";
import { BehaviorSubject } from "rxjs";

@Component({
    selector: "peek-core-device-cfg",
    templateUrl: "core-device-cfg.component.web.html",
})
export class CoreDeviceCfgComponent extends NgLifeCycleEvents {
    statusList$: BehaviorSubject<OfflineCacheStatusTuple[]>;

    constructor(
        private headerService: HeaderService,
        private tupleService: DeviceTupleService,
        private cacheController: DeviceOfflineCacheService
    ) {
        super();
        this.statusList$ = cacheController.cacheStatus$;

        this.headerService.setTitle("Core Device Config");
    }
}
