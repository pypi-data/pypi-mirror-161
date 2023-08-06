import { addTupleType, Tuple } from "@synerty/vortexjs";
import { deviceTuplePrefix } from "../PluginNames";

@addTupleType
export class ClientSettingsTuple extends Tuple {
    // The tuple name here should end in "Tuple" as well, but it doesn't, as it's a table
    public static readonly tupleName =
        deviceTuplePrefix + "ClientSettingsTuple";

    fieldEnrollmentEnabled: boolean;
    officeEnrollmentEnabled: boolean;

    constructor() {
        super(ClientSettingsTuple.tupleName);
    }
}
