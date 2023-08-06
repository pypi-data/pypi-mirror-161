import { addTupleType, Tuple } from "@synerty/vortexjs";
import { userTuplePrefix } from "../_private/PluginNames";

@addTupleType
export class UserListItemTuple extends Tuple {
    public static readonly tupleName = userTuplePrefix + "UserListItemTuple";
    userId: string;
    displayName: string;

    constructor() {
        super(UserListItemTuple.tupleName); // Matches server side
    }

    get userName(): string {
        return this.userId;
    }

    get userTitle(): string {
        return this.displayName;
    }
}
