import { addTupleType, TupleActionABC } from "@synerty/vortexjs";
import { userTuplePrefix } from "../../_private/PluginNames";

@addTupleType
export class UserLoginAction extends TupleActionABC {
    public static readonly tupleName = userTuplePrefix + "UserLoginAction";
    userName: string;
    password: string = "";
    deviceToken: string;
    vehicleId: string = "";
    isFieldService: boolean = null;
    isOfficeService: boolean = null;
    // continues.
    acceptedWarningKeys: string[] = [];

    // A list of accepted warning keys
    // If any server side warnings occur and they are in this list then the logon

    constructor() {
        super(UserLoginAction.tupleName); // Matches server side
    }
}
