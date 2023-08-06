import { addTupleType, Tuple } from "@synerty/vortexjs";
import { deviceTuplePrefix } from "../PluginNames";

@addTupleType
export class OfflineCacheSettingTuple extends Tuple {
    public static readonly tupleName =
        deviceTuplePrefix + "OfflineCacheSettingTuple";

    offlineEnabled: boolean = false;
    offlineCacheSyncSeconds: number = 0;

    constructor() {
        super(OfflineCacheSettingTuple.tupleName);
    }
}
