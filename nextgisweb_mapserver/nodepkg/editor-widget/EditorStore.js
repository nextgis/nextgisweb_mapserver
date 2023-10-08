import { makeAutoObservable, toJS } from "mobx";

export class EditorStore {
    identity = "mapserver_style";
    xml = { in: null, out: null };

    constructor({ initialXml }) {
        this.xml.in = this.xml.out = initialXml;
        makeAutoObservable(this, { identity: false });
    }

    load(value) {
        this.xml.in = value.xml;
    }

    dump() {
        return toJS({ xml: this.xml.out });
    }

    get isValid() {
        return true;
    }
}
