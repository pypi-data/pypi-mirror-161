import { Injectable } from "@angular/core";
import { DeviceServerService } from "./_private/device-server.service";
import { DeviceEnrolmentService } from "./device-enrolment.service";
import { Router } from "@angular/router";
import { deviceBaseUrl } from "./_private";

@Injectable()
export class DeviceStatusService {
    constructor(
        private router: Router,
        private enrolmentService: DeviceEnrolmentService,
        private deviceServerService: DeviceServerService
    ) {}

    get isLoading(): boolean {
        // If we're currently showing a peek_core_device route then, loading = false
        let index = this.router.url.indexOf(deviceBaseUrl);
        if (0 <= index && index <= 4)
            // allow for "/..." etc
            return false;

        return (
            this.enrolmentService.isLoading() ||
            this.deviceServerService.isLoading
        );
    }
}
