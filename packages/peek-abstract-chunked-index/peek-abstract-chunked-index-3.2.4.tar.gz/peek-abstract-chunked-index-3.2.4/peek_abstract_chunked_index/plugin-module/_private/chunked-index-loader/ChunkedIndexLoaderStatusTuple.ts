import { addTupleType, Tuple } from "@synerty/vortexjs";
import { chunkedIndexTuplePrefix } from "../PluginNames";

@addTupleType
export class ChunkedIndexLoaderStatusTuple extends Tuple {
    public static readonly tupleName =
        chunkedIndexTuplePrefix + "ChunkedIndexLoaderStatusTuple";

    cacheForOfflineEnabled: boolean = false;
    initialLoadComplete: boolean = false;
    loadProgress: number = 0;
    loadTotal: number = 0;
    lastCheck: Date;

    constructor() {
        super(ChunkedIndexLoaderStatusTuple.tupleName);
    }
}
