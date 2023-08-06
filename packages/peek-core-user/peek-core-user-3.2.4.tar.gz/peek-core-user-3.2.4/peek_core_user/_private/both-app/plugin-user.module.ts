import { NgModule } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { NzIconModule } from "ng-zorro-antd/icon";
import { RouterModule } from "@angular/router";
import { UserLoginModule } from "./user-login/user-login.module";
import { UserLogoutModule } from "./user-logout/user-logout.module";
import { pluginRoutes } from "./plugin-user.routes";
import { HttpClientModule } from "@angular/common/http";

@NgModule({
    imports: [
        CommonModule,
        RouterModule.forChild(pluginRoutes),
        FormsModule,
        HttpClientModule,
        NzIconModule,
        UserLoginModule,
        UserLogoutModule,
    ],
    declarations: [],
    providers: [],
})
export class PluginUserModule {}
