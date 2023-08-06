import { Component, OnInit } from "@angular/core";
import {
    extend,
    NgLifeCycleEvents,
    Tuple,
    TupleLoader,
    VortexService,
} from "@synerty/vortexjs";
import { coreEmailFilt } from "../PluginNames";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";

class SettingProperty extends Tuple {
    id: number;
    settingId: number;
    key: string;
    type: string;

    int_value: number;
    char_value: string;
    boolean_value: boolean;

    constructor() {
        super("c.s.p.setting.property");
    }
}

@Component({
    selector: "core-email-setting-list",
    templateUrl: "./admin-setting-list.component.html",
})
export class AdminSettingListComponent
    extends NgLifeCycleEvents
    implements OnInit
{
    items: SettingProperty[] = [];
    loader: TupleLoader;
    private readonly filt = extend(
        {
            key: "server.setting.data",
        },
        coreEmailFilt
    );

    constructor(
        private balloonMsg: BalloonMsgService,
        vortexService: VortexService
    ) {
        super();

        this.loader = vortexService.createTupleLoader(this, this.filt);

        this.loader.observable.subscribe(
            (tuples) => (this.items = <SettingProperty[]>tuples)
        );
    }

    ngOnInit() {}

    saveClicked() {
        this.loader
            .save()
            .then(() => this.balloonMsg.showSuccess("Save Successful"))
            .catch((e) => this.balloonMsg.showError(e));
    }

    resetClicked() {
        this.loader
            .load()
            .then(() => this.balloonMsg.showSuccess("Reset Successful"))
            .catch((e) => this.balloonMsg.showError(e));
    }
}
