import { takeUntil } from "rxjs/operators";
import { Component } from "@angular/core";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { DocDbTupleService } from "@peek/peek_core_docdb/_private";
import {
    PrivateDocumentLoaderService,
    PrivateDocumentLoaderStatusTuple,
} from "@peek/peek_core_docdb/_private/document-loader";

@Component({
    selector: "peek-core-docdb-cfg",
    templateUrl: "docdb-cfg.component.web.html",
})
export class DocdbCfgComponent extends NgLifeCycleEvents {
    lastStatus: PrivateDocumentLoaderStatusTuple =
        new PrivateDocumentLoaderStatusTuple();

    constructor(
        private documentLoader: PrivateDocumentLoaderService,
        private tupleService: DocDbTupleService
    ) {
        super();

        this.lastStatus = this.documentLoader.status();
        this.documentLoader
            .statusObservable()
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((value) => (this.lastStatus = value));
    }
}
