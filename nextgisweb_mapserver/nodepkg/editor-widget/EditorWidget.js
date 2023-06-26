import { observer } from "mobx-react-lite";
import { Code } from "@nextgisweb/gui/component/code";
import i18n from "@nextgisweb/pyramid/i18n!mapserver";

export const EditorWidget = observer(({ store }) => {
    return (
        <Code
            value={store.xml.in}
            onChange={(v) => (store.xml.out = v)}
            lang="xml"
            lineNumbers
        ></Code>
    );
});

EditorWidget.title = i18n.gettext("MapServer style");
EditorWidget.activateOn = { create: true };
