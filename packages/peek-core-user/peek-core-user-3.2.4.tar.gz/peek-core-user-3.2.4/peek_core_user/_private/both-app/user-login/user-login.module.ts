import { CommonModule } from "@angular/common";
import { NgModule } from "@angular/core";
import { UserLoginComponent } from "./user-login.component";
import { FormsModule } from "@angular/forms";
import { NzIconModule } from "ng-zorro-antd/icon";
import { HttpClientModule } from "@angular/common/http";

@NgModule({
    imports: [CommonModule, FormsModule, NzIconModule, HttpClientModule],
    exports: [UserLoginComponent],
    declarations: [UserLoginComponent],
})
export class UserLoginModule {}
