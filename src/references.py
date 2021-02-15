import os
from collections import defaultdict
import supervisely_lib as sly

import globals as ag
import catalog

references = defaultdict(list)


def init():
    local_path = os.path.join(ag.app.data_dir, ag.reference_path.lstrip("/"))
    ag.api.file.download(ag.team_id, ag.reference_path, local_path)

    ref_json = sly.json.load_json_file(local_path)
    for reference_key, ref_examples in ref_json["references"].items():
        for reference_info in ref_examples:
            image_url = reference_info["image_url"]
            [top, left, bottom, right] = reference_info["bbox"]
            figure_id = reference_info["geometry"]["id"]
            label = sly.Label(sly.Rectangle(top, left, bottom, right, sly_id=figure_id),
                              ag.gallery_meta.get_obj_class("product"))
            catalog_info = catalog.index[reference_key]

            references[reference_key].append({
                "url": image_url,
                "labelId": figure_id,  # duplicate for simplicity
                "figures": [label.to_json()],
                "zoomToFigure": {
                    "figureId": figure_id,
                    "factor": 1.2
                },
                "catalogInfo": catalog_info
            })

    sly.logger.info(f"Number of items in catalog: {len(catalog.index)}")
    sly.logger.info(f"Number of references: {len(references)}")