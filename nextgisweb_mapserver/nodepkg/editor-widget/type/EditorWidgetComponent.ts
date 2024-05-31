import type { ForwardRefRenderFunction, FunctionComponent } from "react";

import type { EditorStore } from "../EditorStore";

export interface EditorWidgetProps<S extends EditorStore = EditorStore> {
    store: S;
}

interface EditorWidgetOptions {
    title?: string;
    activateOn?: { create: boolean };
}

export type EditorWidgetComponent<P = unknown> = (
    | FunctionComponent<P>
    | ForwardRefRenderFunction<unknown, P>
) &
    EditorWidgetOptions;
