import os
from collections import defaultdict
import supervisely_lib as sly

import globals as ag
import catalog

reference_gallery = {}

empty_gallery = {
    "content": {
        "projectMeta": {},
        "annotations": {},
        "layout": []
    },
    "previewOptions": ag.image_preview_options,
    "options": ag.image_grid_options,
}


def init(data, state):
    global reference_gallery

    local_path = os.path.join(ag.app.data_dir, ag.reference_path.lstrip("/"))
    ag.api.file.download(ag.team_id, ag.reference_path, local_path)

    ref_json = sly.json.load_json_file(local_path)
    for reference_key, ref_examples in ref_json["references"].items():
        if len(ref_examples) >= 2:
            cnt_grid_columns = 2
        else:
            cnt_grid_columns = 1

        review_gallery = {
            "content": {
                "projectMeta": ag.gallery_meta.to_json(),
                "annotations": {},
                "layout": [[] for i in range(cnt_grid_columns)]
            },
            "previewOptions": ag.image_preview_options,
            "options": ag.image_grid_options,
        }

        for idx, reference_info in enumerate(ref_examples):
            image_url = reference_info["image_url"]
            [top, left, bottom, right] = reference_info["bbox"]
            figure_id = reference_info["geometry"]["id"]
            label = sly.Label(sly.Rectangle(top, left, bottom, right, sly_id=figure_id),
                              ag.gallery_meta.get_obj_class("product"))
            catalog_info = catalog.index[reference_key]

            review_gallery["content"]["annotations"][figure_id] = {
                "url": image_url,
                "labelId": figure_id,  # duplicate for simplicity
                "figures": [label.to_json()],
                "zoomToFigure": {
                    "figureId": figure_id,
                    "factor": 1.2
                },
                "catalogInfo": catalog_info
            }
            review_gallery["content"]["layout"][idx % cnt_grid_columns].append(figure_id)

        reference_gallery[reference_key] = review_gallery

    sly.logger.info(f"Number of items in catalog: {len(catalog.index)}")
    sly.logger.info(f"Number of references: {len(reference_gallery)}")

    data["userRef"] = {}  # {1: "7861026000305"} #@TODO: for debug
    data["refGrid"] = reference_gallery
    state["selected"] = {}


def refresh_grid(user_id, reference_key, field="data.userRef"):
    fields = [
        {"field": field, "payload": {user_id: reference_key}, "append": True}
    ]
    ag.api.task.set_fields(ag.task_id, fields)


@ag.app.callback("show_catalog_selection")
@sly.timeit
def obj_changed(api: sly.Api, task_id, context, state, app_logger):
    user_id = context["userId"]
    selected_catalog_row = state["catalogSelection"]
    if selected_catalog_row is None:
        refresh_grid(user_id, None, "data.userCatalog")
    else:
        catalog_key = str(selected_catalog_row["selectedRowData"][ag.column_name])
        refresh_grid(user_id, catalog_key, "data.userCatalog")
