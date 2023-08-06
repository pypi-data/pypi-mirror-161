import { Component } from "@angular/core";
import {
    BalloonMsgLevel,
    BalloonMsgService,
    BalloonMsgType,
} from "@synerty/peek-plugin-base-js";
import {
    NgLifeCycleEvents,
    TupleActionPushService,
    TupleDataObserverService,
    TupleSelector,
} from "@synerty/vortexjs";
import {
    AlterDeviceUpdateAction,
    DeviceUpdateTuple,
} from "@peek/peek_core_device/_private";

@Component({
    selector: "core-device-device-update",
    templateUrl: "./device-update.component.html",
})
export class DeviceUpdateComponent extends NgLifeCycleEvents {
    items: DeviceUpdateTuple[] = [];

    constructor(
        private balloonMsg: BalloonMsgService,
        private actionService: TupleActionPushService,
        private tupleDataObserver: TupleDataObserverService
    ) {
        super();

        // Setup a subscription for the data
        let sup = tupleDataObserver
            .subscribeToTupleSelector(
                new TupleSelector(DeviceUpdateTuple.tupleName, {})
            )
            .subscribe((tuples: DeviceUpdateTuple[]) => {
                this.items = tuples;
            });

        this.onDestroyEvent.subscribe(() => sup.unsubscribe());
    }

    deleteUpdateClicked(item) {
        let action = new AlterDeviceUpdateAction();
        action.updateId = item.id;
        action.remove = true;

        this.balloonMsg
            .showMessage(
                "Are you sure you'd like to delete this update?",
                BalloonMsgLevel.Warning,
                BalloonMsgType.ConfirmCancel,
                { confirmText: "Yes", cancelText: "No" }
            )
            .then(() => this.sendAction(action));
    }

    toggleUpdateEnabledClicked(item: DeviceUpdateTuple) {
        let action = new AlterDeviceUpdateAction();
        action.updateId = item.id;
        action.isEnabled = !item.isEnabled;

        let verb = item.isEnabled ? "DISABLE" : "enable";

        this.balloonMsg
            .showMessage(
                `Are you sure you'd like to ${verb} this update?`,
                BalloonMsgLevel.Warning,
                BalloonMsgType.ConfirmCancel,
                { confirmText: "Yes", cancelText: "No" }
            )
            .then(() => this.sendAction(action));
    }

    private sendAction(action: AlterDeviceUpdateAction) {
        this.actionService
            .pushAction(action)
            .then(() => this.balloonMsg.showSuccess("Success"))
            .catch((e) => this.balloonMsg.showError(e));
    }
}
