import { action, computed, observable } from "mobx";

import { mapper } from "@nextgisweb/gui/arm";
import type * as apitype from "@nextgisweb/mapserver/type/api";
import type { CompositeStore } from "@nextgisweb/resource/composite";
import type { EditorStore as IEditorStore } from "@nextgisweb/resource/type";

const { xml, $load, $error, $dump, $dirty } = mapper<
    EditorStore,
    apitype.MapserverStyleRead
>({
    validateIf: (o) => o.validate,
    properties: {
        xml: { required: true },
    },
});

export class EditorStore
    implements
        IEditorStore<
            apitype.MapserverStyleRead,
            apitype.MapserverStyleCreate,
            apitype.MapserverStyleUpdate
        >
{
    readonly identity = "mapserver_style";
    readonly composite: CompositeStore;

    readonly xml = xml.init("", this);

    @observable.ref accessor validate = false;

    constructor({
        composite,
        initialXml,
    }: {
        composite: CompositeStore;
        initialXml: string;
    }) {
        this.composite = composite;
        this.xml.load(initialXml);
    }

    @action
    load(value: apitype.MapserverStyleRead) {
        $load(this, value);
    }

    dump(): apitype.MapserverStyleUpdate | undefined {
        if (!this.dirty && this.composite.operation !== "create") {
            return undefined;
        }
        return $dump(this);
    }

    @computed
    get dirty() {
        return $dirty(this);
    }

    @computed
    get isValid(): boolean {
        return $error(this) === false;
    }
}
