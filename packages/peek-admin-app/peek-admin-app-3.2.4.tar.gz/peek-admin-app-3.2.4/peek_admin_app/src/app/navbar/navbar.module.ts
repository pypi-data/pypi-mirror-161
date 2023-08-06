import { NgModule } from "@angular/core";
import { CommonModule } from "@angular/common";
import { HttpClientModule } from "@angular/common/http";
import { RouterModule } from "@angular/router";
import { NavbarComponent } from "./navbar.component";
import { NzIconModule } from "ng-zorro-antd/icon";

@NgModule({
    exports: [NavbarComponent],
    imports: [NzIconModule, CommonModule, RouterModule, HttpClientModule],
    declarations: [NavbarComponent],
})
export class NavbarModule {}
