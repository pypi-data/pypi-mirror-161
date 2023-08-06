import { addTupleType, TupleActionABC } from "@synerty/vortexjs";
import { deviceTuplePrefix } from "../PluginNames";
import { OfflineCacheStatusTuple } from "../../tuples/OfflineCacheStatusTuple";

@addTupleType
export class OfflineCacheStatusAction extends TupleActionABC {
    public static readonly tupleName =
        deviceTuplePrefix + "OfflineCacheStatusAction";

    deviceToken: string;
    cacheStatusList: OfflineCacheStatusTuple[] = [];

    constructor() {
        super(OfflineCacheStatusAction.tupleName);
    }
}
