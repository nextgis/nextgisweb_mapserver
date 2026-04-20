import type * as apitype from "@nextgisweb/mapserver/type/api";
import { createPostprocessAdapter } from "@nextgisweb/render/postprocess-section";
import type { SharedPostprocessValue } from "@nextgisweb/render/postprocess-section";
import type { RenderPostprocess } from "@nextgisweb/render/type/api";

export type PostprocessValue = SharedPostprocessValue;
type SparseRenderPostprocess = Partial<RenderPostprocess>;
type ApiPostprocess = SparseRenderPostprocess | null;
type ResourcePostprocessUpdate = Exclude<
  apitype.MapserverStyleUpdate["postprocess"],
  undefined
>;

const postprocessAdapter = createPostprocessAdapter<
  ApiPostprocess,
  SparseRenderPostprocess | null
>();

export const normalizePostprocess = postprocessAdapter.normalize;

export function serializePostprocess(
  value: PostprocessValue | Partial<PostprocessValue> | null | undefined
): ResourcePostprocessUpdate {
  return postprocessAdapter.serialize(value) as ResourcePostprocessUpdate;
}
