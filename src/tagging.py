import supervisely_lib as sly
import globals as ag
import requests
import cache
import references


def assign(api, figure_id, tag_meta, tag_value, remove_duplicates=True):
    if tag_value is not None and tag_value != "":
        if remove_duplicates is True:
            delete(api, figure_id, tag_meta, tag_value)
        api.advanced.add_tag_to_object(tag_meta.sly_id, figure_id, tag_value)


def delete(api, figure_id, tag_meta, tag_value):
    try:
        tags_json = api.advanced.get_object_tags(figure_id)
        tags = sly.TagCollection.from_json(tags_json, ag.meta.tag_metas)
        for tag in tags:
            if tag.meta.sly_id == tag_meta.sly_id:
                api.advanced.remove_tag_from_object(tag_meta.sly_id, figure_id, tag.sly_id)
    except requests.exceptions.HTTPError as error:
        if error.response.status_code == 404:
            return None
        else:
            raise error


def change_tag(api: sly.Api, task_id, context, state, app_logger, action_figure):
    tag_meta = ag.meta.get_tag_meta(ag.tag_name)
    user_id = context["userId"]
    tag_value = None
    if state["catalogSelection"] is not None and state["catalogSelection"]["selectedRowData"] is not None:
        tag_value = str(state["catalogSelection"]["selectedRowData"][ag.column_name])

    figure_id = context["figureId"]
    image_id = context["imageId"]
    ann = cache.get_annotation(image_id)
    selected_label = ann.get_label_by_id(figure_id)

    if selected_label is None:
        sly.logger.warn(f"Figure with id {figure_id} is not found in annotation")
        return
    if selected_label.obj_class.name == ag.target_class_name:
        action_figure(api, figure_id, tag_meta, tag_value)
    elif selected_label.obj_class.name == ag.multiselect_class_name:
        for idx, label in enumerate(ann.labels):
            if label.geometry.sly_id == figure_id:
                continue
            if label.geometry.to_bbox().intersects_with(selected_label.geometry.to_bbox()):
                action_figure(api, label.geometry.sly_id, tag_meta, tag_value)
    if action_figure == assign:
        references.refresh_grid(user_id, tag_value)
    elif action_figure == delete:
        references.refresh_grid(user_id, None)


@ag.app.callback("assign_tag")
@sly.timeit
def assign_tag(api: sly.Api, task_id, context, state, app_logger):
    change_tag(api, task_id, context, state, app_logger, assign)


@ag.app.callback("delete_tag")
@sly.timeit
def delete_tag(api: sly.Api, task_id, context, state, app_logger):
    change_tag(api, task_id, context, state, app_logger, delete)