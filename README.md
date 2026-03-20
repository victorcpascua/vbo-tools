vbo-tools
=========

Simple utilities for RaceLogic VBO files.


Usage
-----

Install the tools system-wide in editable mode (or normally):

```bash
pip install -e .
```

This exposes the `vbo-tools` CLI command with two main subcommands: `csv2vbo` and `add-video`.

### csv2vbo

Converts .csv files produced by various datalogging software to
.vbo files produced by RaceLogic's dataloggers and understood
by the CircuitTools software. The script requires Python 3 and
currently supports the following .csv variants:

  - RaceChrono
  - G-Tech Fanatic
  - TrackMaster
  - QStarz LT6000
  - RaceStudio 2

    TrackMaster .csv can be obtained by manual export
    from a .xls file (only the overview and lap sheets).

`vbo-tools csv2vbo` expects the path to an input .csv file and an optional output .vbo file.
It will either detect the variant of the input .csv file automatically or, failing that, exit with an error. For example, to convert "log.csv" into "log.vbo", run:

```bash
vbo-tools csv2vbo log.csv -o log.vbo
```

You can optionally bundle a video immediately during conversion using `-v`:

```bash
vbo-tools csv2vbo log.csv -v log.mp4
```
*(The `-o` / `--output` flag is optional. If omitted, it will generate a file with the same name and the `.vbo` extension).*


The script does not have overly strict requirements on the input .csv
file. It has to contain a header row with column names, and from that
point onward, only data rows with the same number of columns as the
header row may follow. The data rows may contain duplicate header
rows -- this may result from concatenating multiple .csv files exported
from a spreadsheet. The duplicate header rows are filtered out, as well
as duplicate consecutive data rows.

All rows prior to the header row are output into the resulting VBO file
as comments. The script considers the first row with the maximal number of
columns to be the header row. This usually works even in presence of
non-data rows prior to the header row, as long as the number of columns
in the data is greater than the number of columns in the non-date rows
prior to the header.

If the timestamp of two consecutive data rows exceeds 0.1 s, the script
automatically creates intermediate data rows by interpolating between 
the two data rows, with 0.1 second increments to simulate a 10 Hz GPS.
This makes working with the data in CircuitTools more reasonable (the
software itself does not do interpolation), but it cannot supplement
the vastly more accurate output of a 10 Hz GPS.


### add-video

### add-video

Bundles an existing .vbo file with a corresponding video file (e.g., .mp4, .avi)
so it can be correctly loaded and synchronized in RaceLogic Circuit Tools.

It will rename the video file to match the required prefix alongside the VBO file. If the original video file is located in a different directory, it will be copied instead.

Usage:

```bash
vbo-tools add-video log.vbo video.mp4
```
