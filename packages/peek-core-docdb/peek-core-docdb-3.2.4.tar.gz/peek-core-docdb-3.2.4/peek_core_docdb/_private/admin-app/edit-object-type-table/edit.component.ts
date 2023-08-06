import { Component } from "@angular/core";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { docDbFilt } from "@peek/peek_core_docdb/_private";
import {
    DocDbDocumentTypeTuple,
    DocDbModelSetTuple,
} from "@peek/peek_core_docdb";
import {
    extend,
    NgLifeCycleEvents,
    TupleDataObserverService,
    TupleLoader,
    VortexService,
} from "@synerty/vortexjs";

@Component({
    selector: "pl-docdb-edit-object-type",
    templateUrl: "./edit.component.html",
})
export class EditDocumentTypeComponent extends NgLifeCycleEvents {
    items: DocDbDocumentTypeTuple[] = [];
    loader: TupleLoader;
    modelSetById: { [id: number]: DocDbModelSetTuple } = {};
    documentTypeById: { [id: number]: DocDbDocumentTypeTuple } = {};

    // This must match the dict defined in the admin_backend handler
    private readonly filt = {
        key: "admin.Edit.DocDbDocumentTypeTuple",
    };

    constructor(
        private balloonMsg: BalloonMsgService,
        vortexService: VortexService,
        private tupleObserver: TupleDataObserverService
    ) {
        super();

        this.loader = vortexService.createTupleLoader(this, () =>
            extend({}, this.filt, docDbFilt)
        );

        this.loader.observable.subscribe(
            (tuples: DocDbDocumentTypeTuple[]) => (this.items = tuples)
        );

        // let modelSetTs = new TupleSelector(ModelSetTuple.tupleName, {});
        // this.tupleObserver.subscribeToTupleSelector(modelSetTs)
        //     .pipe(takeUntil(this.onDestroyEvent))
        //     .subscribe((tuples: ModelSetTuple[]) => {
        //         this.modelSetById = {};
        //         for (let tuple of tuples) {
        //             this.modelSetById[tuple.id] = tuple;
        //         }
        //     });
        //
        // let documentTypeTs = new TupleSelector(DocDbDocumentTypeTuple.tupleName, {});
        // this.tupleObserver.subscribeToTupleSelector(documentTypeTs)
        //     .pipe(takeUntil(this.onDestroyEvent))
        //     .subscribe((tuples: DocDbDocumentTypeTuple[]) => {
        //         this.documentTypeById = {};
        //         for (let tuple of tuples) {
        //             this.documentTypeById[tuple.id] = tuple;
        //         }
        //     });
    }

    modelSetTitle(tuple: DocDbDocumentTypeTuple): string {
        // let modelSet = this.modelSetById[tuple.modelSetId];
        // return modelSet == null ? "" : modelSet.name;
        return "TODO";
    }

    documentTypeTitle(tuple: DocDbDocumentTypeTuple): string {
        // let documentType = this.documentTypeById[tuple.doc];
        // return documentType == null ? "" : documentType.name;
        return "TODO";
    }

    save() {
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
