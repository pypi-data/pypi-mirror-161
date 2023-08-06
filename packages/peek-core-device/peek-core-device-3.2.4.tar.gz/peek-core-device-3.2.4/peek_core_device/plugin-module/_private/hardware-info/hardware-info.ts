import {
    addTupleType,
    Tuple,
    TupleOfflineStorageService,
    TupleSelector,
} from "@synerty/vortexjs";
import { deviceTuplePrefix } from "../PluginNames";
import { Md5 } from "ts-md5/dist/md5";
import { isField as isFieldStatic } from "./is-field.mweb";
import { Capacitor } from "@capacitor/core";
import { Device } from "@capacitor/device";

export enum DeviceTypeEnum {
    MOBILE_WEB,
    FIELD_IOS,
    FIELD_ANDROID,
    DESKTOP_WEB,
    DESKTOP_WINDOWS,
    DESKTOP_MACOS,
}

export function isWeb(type: DeviceTypeEnum): boolean {
    return (
        type == DeviceTypeEnum.MOBILE_WEB || type == DeviceTypeEnum.DESKTOP_WEB
    );
}

export function isField(type: DeviceTypeEnum): boolean {
    return (
        type == DeviceTypeEnum.MOBILE_WEB ||
        type == DeviceTypeEnum.FIELD_IOS ||
        type == DeviceTypeEnum.FIELD_ANDROID
    );
}

export function isOffice(type: DeviceTypeEnum): boolean {
    return (
        type == DeviceTypeEnum.DESKTOP_MACOS ||
        type == DeviceTypeEnum.DESKTOP_WINDOWS ||
        type == DeviceTypeEnum.DESKTOP_WEB
    );
}

@addTupleType
class DeviceUuidTuple extends Tuple {
    public static readonly tupleName = deviceTuplePrefix + "DeviceUuidTuple";

    uuid: string;

    constructor() {
        super(DeviceUuidTuple.tupleName);
    }
}

export class HardwareInfo {
    constructor(private tupleStorage: TupleOfflineStorageService) {}

    isWeb(): boolean {
        return isWeb(this.deviceType());
    }

    isField(): boolean {
        return isField(this.deviceType());
    }

    isOffice(): boolean {
        return isOffice(this.deviceType());
    }

    async uuid(): Promise<string> {
        return (await Device.getId()).uuid;
    }

    description(): string {
        return navigator.userAgent;
    }

    deviceType(): DeviceTypeEnum {
        // Field
        if (isFieldStatic) {
            switch (Capacitor.getPlatform()) {
                case "ios":
                    return DeviceTypeEnum.FIELD_IOS;
                case "android":
                    return DeviceTypeEnum.FIELD_ANDROID;
                case "web":
                default:
                    return DeviceTypeEnum.MOBILE_WEB;
            }
        }
        // Office
        else {
            return DeviceTypeEnum.DESKTOP_WEB;
        }
    }
}
