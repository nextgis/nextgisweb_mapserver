import { observer } from "mobx-react-lite";

import { Code } from "@nextgisweb/gui/component/code";
import { gettext } from "@nextgisweb/pyramid/i18n";

import type { EditorStore } from "./EditorStore";
import type { EditorWidgetComponent, EditorWidgetProps } from "./type";

export const EditorWidget: EditorWidgetComponent<
    EditorWidgetProps<EditorStore>
> = observer(({ store }) => {
    return (
        <Code
            value={store.xml.in || undefined}
            onChange={(v) => (store.xml.out = v)}
            lang="xml"
            lineNumbers
        ></Code>
    );
});

EditorWidget.title = gettext("MapServer style");
EditorWidget.activateOn = { create: true };
