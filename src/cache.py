import globals as ag
import supervisely_lib as sly
import threading

annotations = {}
anns_lock = threading.Lock()


def _download(image_id):
    ann_json = ag.api.annotation.download(image_id).annotation
    ann = sly.Annotation.from_json(ann_json, ag.meta)

    global anns_lock
    anns_lock.acquire()
    annotations[image_id] = ann
    anns_lock.release()


def get_annotation(image_id):
    _download(image_id)
    return annotations[image_id]