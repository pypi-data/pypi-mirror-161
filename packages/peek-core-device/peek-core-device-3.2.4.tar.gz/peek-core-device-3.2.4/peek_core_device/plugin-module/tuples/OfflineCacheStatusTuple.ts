import { addTupleType, Tuple } from "@synerty/vortexjs";
import { deviceTuplePrefix } from "../_private";

@addTupleType
export class OfflineCacheStatusTuple extends Tuple {
    public static readonly tupleName =
        deviceTuplePrefix + "OfflineCacheStatusTuple";

    pluginName: string;
    indexName: string;
    loadingQueueCount: number;
    totalLoadedCount: number;
    lastCheckDate: Date;
    initialFullLoadComplete: boolean;

    constructor() {
        super(OfflineCacheStatusTuple.tupleName);
    }

    get key(): string {
        return `${this.pluginName}.${this.indexName}`;
    }
}
