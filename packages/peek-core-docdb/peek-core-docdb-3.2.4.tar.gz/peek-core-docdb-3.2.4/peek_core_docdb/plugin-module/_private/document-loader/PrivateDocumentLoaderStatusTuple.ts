import { addTupleType, Tuple } from "@synerty/vortexjs";
import { docDbTuplePrefix } from "../PluginNames";

@addTupleType
export class PrivateDocumentLoaderStatusTuple extends Tuple {
    public static readonly tupleName =
        docDbTuplePrefix + "PrivateDocumentLoaderStatusTuple";

    cacheForOfflineEnabled: boolean = false;
    initialLoadComplete: boolean = false;
    loadProgress: number = 0;
    loadTotal: number = 0;
    lastCheck: Date;

    constructor() {
        super(PrivateDocumentLoaderStatusTuple.tupleName);
    }
}
