import { ChangeDetectionStrategy, Component } from "@angular/core";
import { HeaderService } from "@synerty/peek-plugin-base-js";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { homeLinks } from "@_peek/plugin-home-links";

@Component({
    selector: "home-page",
    templateUrl: "home.page.html",
    styleUrls: ["home.page.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HomePage extends NgLifeCycleEvents {
    homeLinks = homeLinks;

    constructor(headerService: HeaderService) {
        super();
        headerService.setTitle("Peek Home");
    }
}
