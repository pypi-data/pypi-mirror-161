import { NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";
import { RouterModule } from "@angular/router";
import { FormsModule } from "@angular/forms";
import { NzIconModule } from "ng-zorro-antd/icon";
import { ConfigPage, HomePage, UnknownRoutePage } from "./";

const PAGES = [HomePage, ConfigPage, UnknownRoutePage];

@NgModule({
    declarations: PAGES,
    imports: [RouterModule, FormsModule, BrowserModule, NzIconModule],
    exports: PAGES,
})
export class PagesModule {}
