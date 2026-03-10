import supervisely as sly
import src.globals as g
from supervisely.app.widgets import (
    Container,
    Widget,
    Card,
    Button,
    Text,
    SelectProject,
    SelectDataset,
    Field,
    ReorderFrames,
    Pagination,
)

from typing import Optional, Dict, Any, List, Tuple, Union
from supervisely.app.singleton import Singleton
from time import sleep
import threading


class PagedReorderFrames(ReorderFrames):
    def __init__(self, *args, **kwargs):
        self._page_offset = 0
        super().__init__(*args, **kwargs)

    def set_page_offset(self, page_offset: int) -> None:
        self._page_offset = max(int(page_offset), 0)

    def _build_rows(self) -> List[List[str]]:
        return [
            [str(self._page_offset + index + 1), episode.label]
            for index, episode in enumerate(self._episodes)
        ]


select_project = SelectProject(
    default_id=g.PROJECT_ID, workspace_id=g.WORKSPACE_ID, compact=True
)
select_dataset = SelectDataset(
    default_id=g.DATASET_ID, project_id=g.PROJECT_ID, compact=True
)

reorder_frames = PagedReorderFrames()
save_order_button = Button(
    text="Save dataset order",
    button_type="success",
    icon="zmdi zmdi-save",
)
save_order_status = Text(
    text="Reorder episodes and click Save dataset order.",
    status="info",
)

DEFAULT_PAGE_SIZE = 20
_all_episodes: List[ReorderFrames.Episode] = []
_current_page = 1
_page_size = DEFAULT_PAGE_SIZE
_is_rendering_page = False


def _get_reorder_episodes(
    dataset_id: Optional[int],
) -> List[ReorderFrames.Episode]:
    if dataset_id is None:
        return []

    try:
        pointcloud_infos = g.api.pointcloud_episode.get_list(dataset_id=dataset_id)
    except Exception as exc:
        sly.logger.warning(
            f"Failed to load episodes for dataset ID {dataset_id}: {exc}"
        )
        return []

    pointcloud_infos = sorted(
        pointcloud_infos,
        key=lambda info: (info.frame if info.frame is not None else -1, info.id),
    )

    episodes: List[ReorderFrames.Episode] = []
    for pointcloud_info in pointcloud_infos:
        label = pointcloud_info.name or str(pointcloud_info.id)
        if pointcloud_info.frame is not None:
            label = f"{pointcloud_info.frame}: {label}"
        episodes.append(ReorderFrames.Episode(key=pointcloud_info.id, label=label))

    return episodes


def _normalize_dataset_id(
    dataset_id: Optional[Union[int, str, List[Any], Tuple[Any, ...]]],
) -> Optional[int]:
    value: Any = dataset_id

    if value is None:
        return None

    if isinstance(value, (list, tuple)):
        if len(value) == 0:
            return None
        value = value[0]

    try:
        return int(value)
    except (TypeError, ValueError):
        sly.logger.warning(f"Invalid dataset ID received: {value}")
        return None


def _get_total_pages(total_items: int, page_size: int) -> int:
    if page_size <= 0:
        return 1
    return max((total_items + page_size - 1) // page_size, 1)


def _clamp_page(page: int, total_items: int, page_size: int) -> int:
    return min(max(page, 1), _get_total_pages(total_items, page_size))


def _get_page_bounds(total_items: int, page: int, page_size: int) -> Tuple[int, int]:
    if total_items == 0:
        return 0, 0

    safe_page_size = max(page_size, 1)
    safe_page = _clamp_page(page, total_items, safe_page_size)
    start_idx = (safe_page - 1) * safe_page_size
    end_idx = min(start_idx + safe_page_size, total_items)
    return start_idx, end_idx


def _render_current_page() -> None:
    global _current_page, _is_rendering_page

    total_items = len(_all_episodes)
    _current_page = _clamp_page(_current_page, total_items, _page_size)
    start_idx, end_idx = _get_page_bounds(total_items, _current_page, _page_size)
    page_episodes = _all_episodes[start_idx:end_idx]

    _is_rendering_page = True
    try:
        reorder_frames.set_page_offset(start_idx)
        reorder_frames.set_episodes(page_episodes)
    finally:
        _is_rendering_page = False

    pages.set_total(total_items)
    pages.set_current_page(_current_page)

    sly.logger.info(
        f"Rendered page {_current_page} with {len(page_episodes)} episodes "
        f"(items {start_idx + 1 if total_items > 0 else 0}-{end_idx} of {total_items})"
    )


def _sync_reorder_frames(dataset_id: Optional[int]) -> None:
    global _all_episodes, _current_page

    dataset_id = _normalize_dataset_id(dataset_id)
    _all_episodes = _get_reorder_episodes(dataset_id)
    _current_page = 1
    _render_current_page()

    sly.logger.info(
        f"Loaded {len(_all_episodes)} episodes into reorder widget for dataset ID: {dataset_id}"
    )


def _save_dataset_order(dataset_id: int, ordered_pointcloud_ids: List[int]) -> int:
    pointcloud_infos = g.api.pointcloud_episode.get_list(dataset_id=dataset_id)
    info_by_id = {
        pointcloud_info.id: pointcloud_info for pointcloud_info in pointcloud_infos
    }

    if len(pointcloud_infos) != len(ordered_pointcloud_ids):
        raise RuntimeError("Pointcloud list is outdated. Reload dataset and try again.")

    missing_ids = [
        pointcloud_id
        for pointcloud_id in ordered_pointcloud_ids
        if pointcloud_id not in info_by_id
    ]
    if len(missing_ids) > 0:
        raise RuntimeError(
            f"Some pointcloud IDs are missing in dataset: {missing_ids[:5]}"
        )

    max_existing_frame = max(
        [
            pointcloud_info.frame
            for pointcloud_info in pointcloud_infos
            if pointcloud_info.frame is not None
        ],
        default=-1,
    )
    temp_frame_start = max_existing_frame + len(ordered_pointcloud_ids) + 1

    for offset, pointcloud_id in enumerate(ordered_pointcloud_ids):
        pointcloud_info = info_by_id[pointcloud_id]
        pointcloud_meta = dict(pointcloud_info.meta or {})
        pointcloud_meta["frame"] = temp_frame_start + offset
        g.api.post(
            "images.editInfo",
            {
                "id": pointcloud_id,
                "meta": pointcloud_meta,
            },
        )

    updated_count = 0
    for frame_index, pointcloud_id in enumerate(ordered_pointcloud_ids):
        pointcloud_info = info_by_id[pointcloud_id]
        if pointcloud_info.frame == frame_index:
            continue

        pointcloud_meta = dict(pointcloud_info.meta or {})
        pointcloud_meta["frame"] = frame_index
        g.api.post(
            "images.editInfo",
            {
                "id": pointcloud_id,
                "meta": pointcloud_meta,
            },
        )
        updated_count += 1

    return updated_count


pages = Pagination(total=0, page_size=DEFAULT_PAGE_SIZE)

settings_card = Card(
    title="Settings",
    description="Select the project and dataset.",
    content=Container(
        widgets=[
            select_project,
            select_dataset,
            reorder_frames,
            save_order_button,
            save_order_status,
            pages,
        ]
    ),
)

layout = Container(widgets=[settings_card])

app = sly.Application(layout=layout)


@reorder_frames.order_changed
def _on_page_order_changed(page_episodes: List[ReorderFrames.Episode]):
    global _all_episodes

    if _is_rendering_page:
        return

    start_idx, end_idx = _get_page_bounds(
        total_items=len(_all_episodes),
        page=_current_page,
        page_size=_page_size,
    )

    if end_idx - start_idx != len(page_episodes):
        sly.logger.warning(
            "Skipping order sync because page bounds and widget data length do not match."
        )
        return

    _all_episodes[start_idx:end_idx] = list(page_episodes)


@pages.page_changed
def _on_page_changed(page: int):
    global _current_page

    _current_page = int(page)
    _render_current_page()


@pages.page_size_changed
def _on_page_size_changed(page_size: int):
    global _page_size, _current_page

    _page_size = max(int(page_size), 1)
    _current_page = 1
    _render_current_page()


@select_project.value_changed
def _on_project_changed(project_id: int):
    select_dataset.set_project_id(project_id)
    _sync_reorder_frames(_normalize_dataset_id(select_dataset.get_selected_id()))


@select_dataset.value_changed
def _on_dataset_changed(dataset_id: int):
    _sync_reorder_frames(_normalize_dataset_id(dataset_id))


@save_order_button.click
def _on_save_order():
    dataset_id = _normalize_dataset_id(select_dataset.get_selected_id())
    if dataset_id is None:
        save_order_status.set("Dataset is not selected.", status="warning")
        return

    ordered_pointcloud_ids = [int(episode.key) for episode in _all_episodes]
    if len(ordered_pointcloud_ids) == 0:
        save_order_status.set("Dataset has no episodes.", status="warning")
        return

    try:
        updated_count = _save_dataset_order(
            dataset_id=dataset_id,
            ordered_pointcloud_ids=ordered_pointcloud_ids,
        )
    except Exception as exc:
        sly.logger.warning(
            f"Failed to save episode order for dataset ID {dataset_id}: {exc}"
        )
        save_order_status.set(f"Failed to save order: {exc}", status="error")
        return

    _sync_reorder_frames(dataset_id)
    save_order_status.set(
        f"Dataset order saved. Updated episodes: {updated_count}",
        status="success",
    )


_sync_reorder_frames(_normalize_dataset_id(select_dataset.get_selected_id()))
