<div align="center" markdown>
<img src="https://github.com/supervisely-ecosystem/episode-frame-reorder/releases/download/v1.0.0/EFR.POSTER.png"/>

# Episode Frame Reorder

</div>

## Overview

Episode Frame Reorder is a Supervisely app for changing frame order in point cloud episodes.

The app loads frames from a selected point cloud dataset, shows them in a reorderable table, and saves the new sequence to the dataset by button click.

## What it does

- Displays episode frames in a table with metadata
- Lets you rearrange rows in the desired sequence
- Saves the new order with the **Update order** button

## How to use

1. Run **Episode frame reorder** for a point cloud dataset.
2. Use the search bar to quickly find frames (for example by **Name** or **ID**).
3. If needed, change **Rows per page** in the table footer to control how many rows are shown.
4. In the table, find the frames you want to move.
5. Select one or multiple frames with checkboxes in the first column.
6. After selection, an action panel appears on the right side.
7. Choose the required action in the right panel:
   - **Top** — move selected frames to the beginning of the episode.
   - **Up** — move selected frames one position up.
   - **Set to #** — move selected frames to a specific position number.
   - **Down** — move selected frames one position down.
   - **Bottom** — move selected frames to the end of the episode.
   - **Deselect** — clear current selection.
8. You can also drag rows by the drag handle to reorder manually.
9. Click **Update order** to save the new frame sequence in the dataset.
