import json
import pandas as pd
import os
import globals as ag
import supervisely_lib as sly
from references import refresh_grid

df = None
index = None


def _build_catalog_index():
    global index
    if ag.column_name not in df.columns:
        raise KeyError(f"Column {ag.column_name} not found in CSV columns: {df.columns}")
    records = json.loads(df.to_json(orient="records"))
    index = {str(row[ag.column_name]): row for row in records}


def init(data):
    global df
    local_path = os.path.join(ag.app.data_dir, ag.catalog_path.lstrip("/"))
    ag.api.file.download(ag.team_id, ag.catalog_path, local_path)
    df = pd.read_csv(local_path)
    _build_catalog_index()
    data["userCatalog"] = {}


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