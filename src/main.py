import supervisely as sly
import src.globals as g
from supervisely.app.widgets import Container

from supervisely.app.widgets import ReorderTable, Button

columns = [
    "ID",
    "Name",
    "Figures count",
    "Objects count",
    "Created At",
    "Updated At",
]

reorder_table = ReorderTable(columns=columns)
update_button = Button(text="Update order", button_type="primary")

pointcloud_infos = g.api.pointcloud.get_list(g.DATASET_ID)

data = [
    [
        pointcloud_info.id,
        pointcloud_info.name,
        pointcloud_info.figures_count,
        pointcloud_info.objects_count,
        pointcloud_info.created_at,
        pointcloud_info.updated_at,
    ]
    for pointcloud_info in pointcloud_infos
]
reorder_table.set_data(columns, data)


@update_button.click
def update_order() -> None:
    ids = reorder_table.get_column_data("ID")
    g.api.pointcloud_episode.update_frames_order(g.DATASET_ID, ids)
    sly.logger.info(f"Saved new frame order for dataset {g.DATASET_ID}")


layout = Container(widgets=[reorder_table, update_button])

app = sly.Application(layout=layout)
