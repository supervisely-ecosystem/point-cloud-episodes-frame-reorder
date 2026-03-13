<div align="center" markdown>
<img src="https://github.com/supervisely-ecosystem/episode-frame-reorder/releases/download/v1.0.0/EFR.POSTER.png"/>

# Point Cloud Episodes Frame Reorder

</div>

## Overview

Point Cloud Episodes Frame Reorder is a Supervisely app for changing frame order in point cloud episodes.

The app loads frames from a selected point cloud dataset, shows them in a reorderable table, and saves the new sequence to the dataset by button click.

![Point Cloud Episodes Frame Reorder](https://github.com/supervisely-ecosystem/point-cloud-episodes-frame-reorder/releases/download/v1.0.0/screenshot-localhost-8000-1773404363772.png)

## What it does

- Displays point cloud episode frames in a table with metadata
- Lets you rearrange rows in the desired sequence
- Saves the new order with the **Apply changes** button
- Returns frames to the original dataset order with the **Refresh** button

## When to use this app

Point Cloud Episodes Frame Reorder is useful when point cloud episode frame sequence is important for annotation, QA, and model training, but the dataset order is not correct.

Typical cases:

- **Incremental uploads to an existing project**: new frames are added later, and they appear in the wrong position inside the point cloud episode.
- **Merged data from multiple sources**: frames are collected from different folders, devices, or pipelines, so final order in the dataset does not match the real timeline.
- **Import/export side effects**: after migration between tools or formats, frame IDs/names remain valid but sequence becomes inconsistent.

![Table](https://github.com/supervisely-ecosystem/point-cloud-episodes-frame-reorder/releases/download/v1.0.0/screenshot-localhost-8000-1773404394938.png)

## How to use

1. Run **Point Cloud Episodes frame reorder** for a point cloud episodes dataset.
2. Use the search bar to quickly find frames (for example by **Name** or **ID**).
3. If needed, change **Rows per page** in the table footer to control how many rows are shown.
4. In the table, find the frames you want to move.
5. Select one or multiple frames with checkboxes in the first column.
6. After selection, an action panel appears on the right side.
7. Choose the required action in the right panel:
   - **Top** — move selected frames to the beginning of the point cloud episode.
   - **Up** — move selected frames one position up.
   - **Set to #** — move selected frames to a specific position number.
     ![Set to #](https://github.com/supervisely-ecosystem/point-cloud-episodes-frame-reorder/releases/download/v1.0.0/screenshot-localhost-8000-1773405490118.png)
   - **Down** — move selected frames one position down.
   - **Bottom** — move selected frames to the end of the point cloud episode.
   - **Deselect** — clear current selection.
8. You can also drag rows by the drag handle to reorder manually.
9. Click **Apply changes** to save the new frame sequence in the dataset.

## Refresh button

Use **Refresh** to return frames to their original order (the last order saved in the dataset) and discard unsaved local reordering.
