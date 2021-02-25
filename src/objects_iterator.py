import supervisely_lib as sly
import globals as ag
import cache
import references


def get_by_id(ann: sly.Annotation, figure_id):
    for idx, label in enumerate(ann.labels):
        if label.geometry.sly_id == figure_id:
            return label
    return None


def get_first_id(ann: sly.Annotation):
    for idx, label in enumerate(ann.labels):
        if label.obj_class.name == ag.target_class_name:
            return label
    return None


def get_prev_id(ann: sly.Annotation, active_figure_id):
    prev_idx = None
    for idx, label in enumerate(ann.labels):
        if label.geometry.sly_id == active_figure_id:
            if prev_idx is None:
                return None
            return ann.labels[prev_idx]
        if label.obj_class.name == ag.target_class_name:
            prev_idx = idx


def get_next_id(ann: sly.Annotation, active_figure_id):
    need_search = False
    for idx, label in enumerate(ann.labels):
        if label.geometry.sly_id == active_figure_id:
            need_search = True
            continue
        if need_search:
            if label.obj_class.name == ag.target_class_name:
                return label
    return None


def select_object(api: sly.Api, task_id, context, find_func, show_msg=False) -> sly.Label:
    user_id = context["userId"]
    image_id = context["imageId"]
    project_id = context["projectId"]
    ann_tool_session = context["sessionId"]

    if image_id is None:
        return None
    ann = cache.get_annotation(image_id)

    active_figure_id = context["figureId"]
    if active_figure_id is None:
        active_label = get_first_id(ann)
    else:
        active_label = find_func(ann, active_figure_id)

    if active_label is not None:
        active_figure_id = active_label.geometry.sly_id
        api.img_ann_tool.set_figure(ann_tool_session, active_figure_id)
        api.img_ann_tool.zoom_to_figure(ann_tool_session, active_figure_id, 2)

    return active_label


@ag.app.callback("select_prev_object")
@sly.timeit
def prev_object(api: sly.Api, task_id, context, state, app_logger):
    active_label = select_object(api, task_id, context, get_prev_id)
    if active_label is not None:
        references.refresh_grid(context["userId"], get_label_tag(active_label))


@ag.app.callback("select_next_object")
@sly.timeit
def next_object(api: sly.Api, task_id, context, state, app_logger):
    active_label = select_object(api, task_id, context, get_next_id, show_msg=True)
    if active_label is not None:
        references.refresh_grid(context["userId"], get_label_tag(active_label))


@ag.app.callback("manual_selected_figure_changed")
@sly.timeit
def obj_changed(api: sly.Api, task_id, context, state, app_logger):
    active_figure_id = context["figureId"]
    image_id = context["imageId"]
    ann: sly.Annotation = cache.get_annotation(image_id)

    active_label = None
    if active_figure_id is not None:
        active_label = get_by_id(ann, active_figure_id)
    references.refresh_grid(context["userId"], get_label_tag(active_label))


def get_label_tag(label: sly.Label):
    if label is None:
        return None
    for tag in label.tags:
        if tag.meta.name == ag.tag_name:
            return tag.value
    return None
