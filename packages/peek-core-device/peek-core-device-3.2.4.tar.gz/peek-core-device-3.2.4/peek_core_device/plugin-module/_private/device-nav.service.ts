import { Injectable } from "@angular/core";
import { deviceBaseUrl } from "./PluginNames";

import { ActivatedRoute, Router, UrlSegment } from "@angular/router";

@Injectable()
export class DeviceNavService {
    homeUrl: UrlSegment[] = [];

    constructor(private route: ActivatedRoute, private router: Router) {
        // This is intended to route the web pages back to what ever URL
        // they have been routed from.
        this.route.url.subscribe((segments: UrlSegment[]) => {
            if (segments.length == 0) return;

            if (segments[0].path == deviceBaseUrl) return;

            if (segments[0].path == "") return;

            this.homeUrl = segments;
        });
    }

    toHome() {
        if (this.homeUrl.length != 0) this.router.navigate(this.homeUrl);
        else this.router.navigate([""]);
    }

    toConnect() {
        this.router.navigate([deviceBaseUrl, "connect"]);
    }

    toConnecting() {
        this.router.navigate([deviceBaseUrl, "connecting"]);
    }

    toEnroll() {
        this.router.navigate([deviceBaseUrl, "enroll"]);
    }

    toEnrolling() {
        this.router.navigate([deviceBaseUrl, "enrolling"]);
    }
}
