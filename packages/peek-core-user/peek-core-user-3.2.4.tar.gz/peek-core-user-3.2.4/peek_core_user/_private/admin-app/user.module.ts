import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { EditInternalUserComponent } from "./edit-internal-user-table/edit.component";
import { EditInternalGroupComponent } from "./edit-internal-group-table/edit.component";
import { EditSettingComponent } from "./edit-setting-table/edit.component";
import { NzTabsModule } from "ng-zorro-antd/tabs";
import { NzButtonModule } from "ng-zorro-antd/button";
import { NzIconModule } from "ng-zorro-antd/icon";
import { HttpClientModule } from "@angular/common/http";
import {
    TupleActionPushNameService,
    TupleActionPushService,
    TupleDataObservableNameService,
    TupleDataObserverService,
    TupleDataOfflineObserverService,
    TupleOfflineStorageNameService,
    TupleOfflineStorageService,
} from "@synerty/vortexjs";
import { UserComponent } from "./user.component";
import {
    userActionProcessorName,
    userFilt,
    userObservableName,
    userTupleOfflineServiceName,
} from "@peek/peek_core_user/_private";

import { ManageLoggedInUserComponent } from "./logged-in-user/logged-in-user.component";
import { NzSwitchModule } from "ng-zorro-antd/switch";
import { EditLdapSettingComponent } from "./edit-ldap-setting-table/edit.component";

export function tupleDataObservableNameServiceFactory() {
    return new TupleDataObservableNameService(userObservableName, userFilt);
}

export function tupleActionPushNameServiceFactory() {
    return new TupleActionPushNameService(userActionProcessorName, userFilt);
}

export function tupleOfflineStorageNameServiceFactory() {
    return new TupleOfflineStorageNameService(userTupleOfflineServiceName);
}

// Define the routes for this Angular module.
export const pluginRoutes: Routes = [
    {
        path: "",
        component: UserComponent,
    },
];

@NgModule({
    imports: [
        CommonModule,
        RouterModule.forChild(pluginRoutes),
        FormsModule,
        NzTabsModule,
        NzSwitchModule,
        NzButtonModule,
        NzIconModule,
        HttpClientModule,
    ],
    exports: [],
    providers: [
        TupleActionPushService,
        {
            provide: TupleActionPushNameService,
            useFactory: tupleActionPushNameServiceFactory,
        },
        TupleOfflineStorageService,
        {
            provide: TupleOfflineStorageNameService,
            useFactory: tupleOfflineStorageNameServiceFactory,
        },
        TupleDataObserverService,
        TupleDataOfflineObserverService,
        {
            provide: TupleDataObservableNameService,
            useFactory: tupleDataObservableNameServiceFactory,
        },
    ],
    declarations: [
        UserComponent,
        ManageLoggedInUserComponent,
        EditInternalUserComponent,
        EditInternalGroupComponent,
        EditSettingComponent,
        EditLdapSettingComponent,
    ],
})
export class UserModule {}
