import { Component, OnInit } from "@angular/core";

let exampleDocMod = `
    {
        key: "ABC123",
        document: {
        {
            alias:"A12345678COMP",
            name: "This is a circuit breaker ABC123",
            rating: "11kV"
        }
    }
`;

@Component({
    selector: "docDb-admin",
    templateUrl: "docDb.component.html",
})
export class DocDbComponent implements OnInit {
    exampleDoc = exampleDocMod;

    ngOnInit() {}
}
