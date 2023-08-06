import { addTupleType, Tuple } from "@synerty/vortexjs";
import { deviceTuplePrefix } from "@peek/peek_core_device/_private";
import { OfflineCacheStatusTuple } from "@peek/peek_core_device/tuples/OfflineCacheStatusTuple";

@addTupleType
export class DeviceCacheStatusTuple extends Tuple {
    public static readonly tupleName =
        deviceTuplePrefix + "DeviceCacheStatusTuple";

    statusList: OfflineCacheStatusTuple[] = [];

    constructor() {
        super(DeviceCacheStatusTuple.tupleName);
    }
}
