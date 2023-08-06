import { ChangeDetectionStrategy, Component } from "@angular/core";
import { HeaderService, NavBackService } from "@synerty/peek-plugin-base-js";
import { LoggedInGuard } from "@peek/peek_core_user";
import { BehaviorSubject } from "rxjs";

@Component({
    selector: "header-component",
    templateUrl: "header.component.html",
    styleUrls: ["header.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HeaderComponent {
    showSearch$: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);

    constructor(
        public headerService: HeaderService,
        private loggedInGuard: LoggedInGuard,
        public navBackService: NavBackService
    ) {}

    get showSearch() {
        return this.showSearch$.getValue();
    }

    set showSearch(value) {
        this.showSearch$.next(value);
    }

    showSearchClicked(): void {
        if (this.showSearch) {
            this.showSearch = false;
        } else {
            const canActivate: any = this.loggedInGuard.canActivate();
            if (canActivate) {
                this.showSearch = true;
            } else if (canActivate.then) {
                canActivate.then((val: boolean) => (this.showSearch = val));
            }
        }
    }
}
