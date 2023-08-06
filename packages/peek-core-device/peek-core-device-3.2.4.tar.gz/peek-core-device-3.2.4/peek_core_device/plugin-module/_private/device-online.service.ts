import { Injectable } from "@angular/core";
import { DeviceTupleService } from "./device-tuple.service";
import { UpdateDeviceOnlineAction } from "./tuples/UpdateDeviceOnlineAction";

@Injectable()
export class DeviceOnlineService {
    constructor(private tupleService: DeviceTupleService) {}

    // @ts-ignore
    async setDeviceOnline(): Promise<void> {
        const data = new UpdateDeviceOnlineAction();

        data.deviceId = await this.tupleService.hardwareInfo.uuid();
        data.deviceStatus = data.DEVICE_ONLINE;

        this.tupleService.tupleAction
            .pushAction(data)
            .catch((error) => console.error(error));
    }

    // @ts-ignore
    async setDeviceOffline(): Promise<void> {
        const data = new UpdateDeviceOnlineAction();

        data.deviceId = await this.tupleService.hardwareInfo.uuid();
        data.deviceStatus = data.DEVICE_OFFLINE;

        this.tupleService.tupleAction
            .pushAction(data)
            .catch((error) => console.error(error));
    }
}
