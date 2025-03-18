import { observer } from "mobx-react-lite";

import { Code } from "@nextgisweb/gui/component/code";
import { gettext } from "@nextgisweb/pyramid/i18n";
import type { EditorWidget as IEditorWidget } from "@nextgisweb/resource/type";

import type { EditorStore } from "./EditorStore";

export const EditorWidget: IEditorWidget<EditorStore> = observer(
    ({ store }) => {
        return (
            <Code
                value={store.xml.initial}
                onChange={store.xml.setter}
                lang="xml"
                lineNumbers
            />
        );
    }
);

EditorWidget.displayName = "EditorWidget";
EditorWidget.title = gettext("MapServer style");
EditorWidget.activateOn = { create: true };
