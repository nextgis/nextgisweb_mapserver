import { makeAutoObservable, toJS } from "mobx";

interface Value {
    xml: string | null;
}

export class EditorStore {
    identity = "mapserver_style";
    xml: { in: string | null; out: string | null } = { in: null, out: null };

    constructor({ initialXml }: { initialXml: string }) {
        this.xml.in = this.xml.out = initialXml;
        makeAutoObservable(this, { identity: false });
    }

    load(value: Value) {
        this.xml.in = value.xml;
    }

    dump() {
        return toJS({ xml: this.xml.out });
    }

    get isValid() {
        return true;
    }
}
