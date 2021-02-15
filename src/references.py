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

        review_gallery = {
            "content": {
                "projectMeta": ag.gallery_meta.to_json(),
                "annotations": {},
                "layout": [[] for i in range(2)]
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
            review_gallery["content"]["layout"][idx % 2].append(figure_id)

        reference_gallery[reference_key] = review_gallery


    sly.logger.info(f"Number of items in catalog: {len(catalog.index)}")
    sly.logger.info(f"Number of references: {len(reference_gallery)}")

    data["userRef"] = {}  # {1: "7861026000305"} #@TODO: for debug
    data["refGrid"] = reference_gallery
    state["selected"] = {}


def refresh_grid(user_id, reference_key):
    fields = [
        {"field": "data.userRef", "payload": {user_id: reference_key}, "append": True}
    ]
    ag.api.task.set_fields(ag.task_id, fields)