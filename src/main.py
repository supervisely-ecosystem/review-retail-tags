import json
import supervisely_lib as sly

import globals as ag  # application globals
import catalog
import references
import objects_iterator
import tagging


def main():
    ag.init()

    data = {}
    data["user"] = {}

    data["catalog"] = {"columns": [], "data": []}
    data["targetProject"] = {"id": ag.project.id, "name": ag.project.name}
    data["currentMeta"] = {}

    state = {}
    state["selectedTab"] = "review"
    state["targetClass"] = ag.target_class_name
    state["multiselectClass"] = ag.multiselect_class_name
    state["user"] = {}
    state["selected"] = {}

    sly.logger.info("Initialize catalog ...")
    catalog.init()
    data["catalog"] = json.loads(catalog.df.to_json(orient="split"))
    data["emptyGallery"] = references.empty_gallery

    sly.logger.info("Initialize references ...")
    references.init(data, state)

    # sly.logger.info("Initialize batches ...")
    # batches.init(data, state)

    ag.app.run(data=data, state=state)


if __name__ == "__main__":
    sly.main_wrapper("main", main)
