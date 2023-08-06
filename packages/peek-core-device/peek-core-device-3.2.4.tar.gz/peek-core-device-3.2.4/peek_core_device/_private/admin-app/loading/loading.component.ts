import { Component } from "@angular/core";

/* This file is here to make the admin site compile, since there is a public
 angular module that depends on it.
 */

@Component({
    selector: "core-device-loading",
    template: "<p>nothing</p>",
})
export class LoadingComponent {
    constructor() {}
}
