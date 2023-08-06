import { CommonModule } from "@angular/common";
import { NgModule } from "@angular/core";
import { UserLogoutComponent } from "./user-logout.component";
import { FormsModule } from "@angular/forms";
import { NzIconModule } from "ng-zorro-antd/icon";
import { HttpClientModule } from "@angular/common/http";

@NgModule({
    imports: [CommonModule, FormsModule, NzIconModule, HttpClientModule],
    exports: [UserLogoutComponent],
    declarations: [UserLogoutComponent],
})
export class UserLogoutModule {}
