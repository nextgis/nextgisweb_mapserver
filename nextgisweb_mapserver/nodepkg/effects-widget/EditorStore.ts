import { isEqual } from "lodash-es";
import { action, computed, observable } from "mobx";

import type * as apitype from "@nextgisweb/mapserver/type/api";
import type { CompositeStore } from "@nextgisweb/resource/composite";
import type { EditorStore as IEditorStore } from "@nextgisweb/resource/type";

import { normalizePostprocess, serializePostprocess } from "../postprocess";
import type { PostprocessValue } from "../postprocess";

export class EditorStore implements IEditorStore<
  apitype.MapserverStyleRead,
  apitype.MapserverStyleCreate,
  apitype.MapserverStyleUpdate
> {
  readonly identity = "mapserver_style";
  readonly composite: CompositeStore;

  @observable.ref accessor postprocess: PostprocessValue | null = null;

  #loaded: PostprocessValue | null = null;

  constructor({ composite }: { composite: CompositeStore }) {
    this.composite = composite;
  }

  @action
  load(value: apitype.MapserverStyleRead) {
    const normalized = normalizePostprocess(value.postprocess);
    this.postprocess = normalized;
    this.#loaded = normalized;
  }

  dump(): apitype.MapserverStyleUpdate | undefined {
    if (!this.dirty) {
      return undefined;
    }

    return { postprocess: serializePostprocess(this.postprocess) };
  }

  @computed
  get dirty() {
    return !isEqual(this.postprocess, this.#loaded);
  }

  @computed
  get isValid(): boolean {
    return true;
  }

  @action.bound
  setPostprocess<K extends keyof PostprocessValue>(
    key: K,
    value: PostprocessValue[K]
  ) {
    const current: Partial<PostprocessValue> = this.postprocess ?? {};
    if (current[key] === value) return;
    this.postprocess = normalizePostprocess({ ...current, [key]: value });
  }
}
