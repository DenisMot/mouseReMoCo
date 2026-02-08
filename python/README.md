# mouseReMoCo

`mouseRemMoCo` started as a PyQt6 port of the `mouseRemMoCo` Java application. 

As PyQt6 allows for pressure-sensitive tablets to be used, `mouseRemMoCo` evolved to support pressure-sensitive input from e.g., a Wacom pen on a tablet.

As of February 2026, it is a prototype application useable for scientific research on circular steering combined with pressure steering.



---

## Quick Start

You will need to have [Miniconda](https://docs.conda.io/en/latest/miniconda.html) installed on your computer. 

You also need to get familiar with using shell commands (i.e., with `Terminal` on macOS/Linux or `PowerShell` on Windows).

### 1. Clone GitHub repository and setup conda environment for `mouseReMoCo`

1. Manually create a directory named `mouseReMoCo-folder` (e.g., `Desktop/mouseReMoCo-folder/`)
    - do this with mouse and clicks 
2. Open a terminal and move in `mouseReMoCo-folder` 
3. Run the following commands:
```bash
    git clone --branch python-app --single-branch --depth 1 https://github.com/DenisMot/mouseReMoCo.git 
```

You now have a copy of the `mouseReMoCo`GitHub repository in `mouseReMoCo-folder`.

```
mouseReMoCo-folder/
└── mouseReMoCo/
    └── python/                   ← Python package
        └── main.py               ← Entry point
```

4. Move the terminal in `mouseReMoCo/python/` where the `environment.yml` file is located
5. Run the following commands:

```bash
    conda env create -f environment.yml
    conda activate mouseremoco
```

You now have the `mouseremoco` conda environment needed for the `mouseReMoCo` application.

### 3. Run Application

1. Open a terminal and move in `mouseReMoCo-folder`
2. Run the application with the following command line:
- For macOS/Linux (path is with forward slashes): 
```bash
    python mouseReMoCo/python/main.py
```
- For Windows (path is with backslashes):
```bash
    python mouseReMoCo\python\main.py
```


The `data.csv` and `marker.csv` files will be created in the `mouseReMoCo-folder` directory after running the application, rendering the following structure:

```
mouseReMoCo-folder/
├── data.csv                      ← Generated data (runtime)
├── marker.csv                    ← Generated markers (runtime) 
└── mouseReMoCo/
    └── python/                   ← Python package
        └── main.py               ← Entry point
```

---

## Advanced: Run from a Different Data Directory

The `launcher` directory contains platform-specific shell scripts that allow you to run `mouseReMoCo` in a safe ways e.g., for a research experiment. 

You can place the launcher in any directory (e.g., your current experiment folder), and all output files will save there automatically, without overwriting any existing file (i.e., the launcher will archive old data with timestamps).

### Launcher initialization 
The launcher scripts need to know the path to the `main.py` file on YOUR computer. To set this up: 
- make a copy of the launcher script you want to your `mouseReMoCo-folder` 
- open the copy with VSCode (or a text editor of your choice) 
- replace `REPO_DIR="/path/to/your/mouseReMoCo"`  with the actual path of `mouseReMoCo-folder` on YOUR computer (e.g., `REPO_DIR="/Users/denis/Desktop/mouseReMoCo-folder/"` or `REPO_DIR="C:\Users\Denis\Desktop\mouseReMoCo-folder\"`)
- save the file

You now have a launcher script set for YOUR computer in your `mouseReMoCo-folder`: **keep it here as a reference**, but make copies of it to run experiments in different directories.


### Step by step usage:

1. Make a copy of YOUR `mouseremoco.command` (macOS) or `mouseremoco.bat` (Windows) to your desired data directory (e.g., `Desktop/Experiment_1/`)
2. Double click the launcher to run the application
3. Data files (`data.csv` and `marker.csv`) will be generated in the same directory as the launcher


### Example: Setting up Multiple Experiments

```
Desktop/
├── Experiment_1/
│   ├── mouseremoco.command    ← Copy with REPO_DIR edited
│   ├── data.csv               ← Generated here
│   └── marker.csv             ← Generated here
├── Experiment_2/
│   ├── mouseremoco.command    ← Separate copy
│   ├── data.csv
│   └── marker.csv
```

Each folder keeps its own data organized and independent.

### Automatic Data Archiving

When using the launcher, the launcher **automatically archives your data files** with a timestamp when it closes:

- Original files: `data.csv`, `marker.csv` (overwritten on next run)
- Archived files: `data_2025-02-06_14-30-45.csv`, `marker_2025-02-06_14-30-45.csv` (preserved with timestamp)

**Example directory after 2 experiments:**
```
Experiment_1/
├── mouseremoco.command
├── data.csv                          ← Current session (will be overwritten)
├── marker.csv                        ← Current session (will be overwritten)
├── data_2025-02-06_14-30-45.csv     ← Archived from first run
├── marker_2025-02-06_14-30-45.csv   ← Archived from first run
├── data_2025-02-06_15-15-20.csv     ← Archived from second run
└── marker_2025-02-06_15-15-20.csv   ← Archived from second run
```

This ensures you never lose data between sessions—all your experiments are automatically preserved with unique timestamps.

---

## Controls

| Key | Action |
|-----|--------|
| **SPACE** | Toggle record/pause |
| **C** | Print configuration to console |
| **Q** | Quit application (shows goodbye message if LSL recording is active) |
| **← / →** | Decrease / Increase pressure band width |
| **↓ / ↑** | Decrease / Increase pressure band center |
| **S** | Toggle trail smoothing on/off |
| **G** | Toggle pressure band gauge visibility on/off |

---

## Output Files

After running the application, two CSV files are generated in the `python/` directory:

### `data.csv`
Contains tablet/mouse timestamps with position and pressure data:
- `event_timestamp` - Hardware event timestamp (ms, with epoch 0 unknown, maybe system start)
- `unix_timestamp` - System time when event handler was called (ms, with epoch 0 at Jan 1, 1970)
- `mouseX`, `mouseY` - Cursor position (sub-pixel precision, pixels)
- `mouseInTarget` - 1 if inside tolerance band, 0 otherwise
- `pressure` - Stylus pressure (0.0-1.0 normalized)
- `tiltX`, `tiltY` - Stylus tilt angles (degrees, -60° to +60°)

IMPORTANT NOTES: 
- `pressure`, `tiltX`, and `tiltY` are 0 when using mouse input.
- `event_timestamp` - Hardware timestamp from tablet/mouse event (most accurate for analysis)
- `unix_timestamp` - System time when handler was called (use for synchronization with external devices)
- Sampling rate varies based on hardware and system load: **sampling is NOT constant**.

### `marker.csv`
Contains event markers for experiment synchronization:
- `timestamp` - Human-readable ISO8601 timestamp with millisecond precision
- `unix_timestamp` - UNIX epoch time in milliseconds (since Jan 1, 1970, 00:00:00 UTC)
- `marker` - Event description (e.g., "RecordingStarted", "TabletDetected")

### Shared Metadata
Both `data.csv` and `marker.csv` include the same metadata in their first two lines:
1. **Configuration String** - A JSON string of the current configuration settings (e.g., cursor radius, target size)
2. **Session Start Timestamp** - ISO8601 timestamp of when the session started (same for both files)

This metadata allows you to **link the data and marker files together** and understand the experimental conditions under which the data was collected.

---

## Lab Streaming Layer (LSL) Output

Lab Streaming Layer (LSL) enables **real-time streaming** of mouse/tablet data to external applications like LabRecorder, enabling synchronized multi-device recording.

### Prerequisites

LSL is **optional**. To use it, you have to download and install **LabRecorder** from [LSL documentation](https://labstreaminglayer.readthedocs.io/). 

### Enable LSL

Edit `mouseremoco/app_config.py`to change the `ENABLE_LSL` flag to `True`:
```python
ENABLE_LSL = True
```

### How LSL Works

When enabled, mouseReMoCo broadcasts three LSL streams:

| Stream | Type | Purpose |
|--------|------|---------|
| **MouseData** | double64 | timestamps, position, pressure and tilt |
| **MouseMarkers** | String | Event markers |
| **MouseMarkersNumeric** | Integer | Numeric markers for sync (for future use) |

**Data precision:** Uses double64 format for exact timestamp accuracy (avoids float32 rounding errors for large numbers like UNIX timestamps).

### Recording with LabRecorder

1. Run mouseReMoCo (so that it starts broadcasting LSL streams)
2. Start LabRecorder (make sure it's on the same network if using a different machine)
3. in LabRecorder, Click "update" to refresh the list of available streams
4. in LabRecorder, Select the streams for recording
5. in LabRecorder, Click "Start Recording"
6. Run mouseReMoCo and perform your task
6. in LabRecorder, Click "Stop Recording" to generate the `.xdf` file with synchronized data
7. Close mouseReMoCo 

### LSL Metadata

All streams include the same metadata found in *.csv file header:

- **configuration_str** - Configuration settings (same as first line of `data.csv`)
- **timestamp_str** - ISO8601 session start time (same as second line of `data.csv`)


---

## Project Structure

```
python/
├── main.py                           ← Entry point
├── environment.yml                   ← Conda environment definition
├── README.md                         ← This file
│
├── mouseremoco/                      ← Python package
│   ├── __init__.py
│   ├── app_config.py                 ← Centralized configuration (edit this!)
│   ├── config.py                     ← Configuration classes
│   ├── geometry.py                   ← Geometry utilities
│   ├── screen.py                     ← Screen & tablet detection
│   ├── types.py                      ← Lightweight shared types (`AppStatus`)
│   ├── state.py                      ← WindowSetup and orchestration
│   │
│   ├── ui/                           ← UI Components
│   │   ├── window.py                 ← MainWindow (PyQt6 widget)
│   │   ├── cursor.py                 ← Custom cursor factory
│   │   ├── target.py                 ← Circular target drawing
│   │   └── trail.py                  ← Comet trail rendering
│   │
│   ├── input/                        ← Input Processing
│   │   └── capture.py                ← Event data extraction
│   │
│   └── output/                       ← Data Output
│       ├── backends.py               ← CSV & LSL backends
│       ├── manager.py                ← Output manager
│       └── tests/                    ← Output tests
│           └── test_lsl_backend.py
│
├── images/                           ← Docs images
│   ├── SampleRate-Mouse.png
│   └── SampleRate-Tablet.png
│
├── launchers/                        ← Platform specific launch scripts
│   ├── mouseremoco.bat
│   ├── mouseremoco.command
│   └── mouseremoco.sh
│
└──  notebooks/                        ← Analysis notebooks go here

```

---

## Configuration

All startup parameters are centralized in **`mouseremoco/app_config.py`** for easy modification without digging through code. This includes:

- **Window & Display**: Screen dimensions, refresh rate, background color
- **Circular Task**: Target radius, center position, tolerance band
- **Visual Styling**: Colors, fonts, cursor sizes, trail modes
- **Recording**: CSV and LSL backend activation
- **Tablet Input**: Pressure band settings, tilt limits

### Quick Start - Modify Parameters

Edit `mouseremoco/app_config.py` before running:

```python
# Example: enable CSV only
ENABLE_CSV = True          # Record to CSV files
ENABLE_LSL = False         # Stream to LabRecorder or other LSL receivers
```

### Common Customizations

| Parameter | Purpose | Example |
|-----------|---------|---------|
| `ENABLE_CSV` | Write data.csv, marker.csv | `True` |
| `ENABLE_LSL` | Stream via Lab Streaming Layer | `True` |
| `PRESSURE_BAND_CENTER` | Tablet pressure threshold | `0.5` |
| `PRESSURE_BAND_WIDTH` | Pressure band range | `0.4` |
| `INDEX_OF_DIFFICULTY` | Steering difficulty index | `40` |

All parameters have sensible defaults. Changes take effect immediately on restart—no build required.

---

## Tablet Detection

The application automatically detects pressure-sensitive devices (e.g., Wacom tablets) when in proximity.
- Trail color changes: **Blue (mouse) → Red/Green (tablet)**
- Pressure-sensitive trail thickness and color when using tablet

---

## Troubleshooting

### No tablet detected when using a Wacom pen/tablet

**Solution:** Check Wacom driver installation and tablet connectivity.

### Poor performance / high latency

**Solution:**
- Close other applications
- Check CPU usage
- Verify hardware tablet drivers are up-to-date

---



## Dependencies

See `environment.yml` for exact versions. Key dependencies include:
- `PyQt6` for GUI
- `pylsl` for Lab Streaming Layer integration

---

## License

See LICENSE file in repository root.

---

## Citation

If you use mouseReMoCo in research, please cite:

```
Denis Mottet et al. mouseReMoCo: Wacom Tablet Test for Motor Control Studies
```

---

## Support

For issues, questions, or suggestions:
1. Check existing GitHub issues
2. Create new issue with description and console output
3. Include Python version: `python --version`
4. Include PyQt6 version: `conda list qt`

---

## See Also

- **Original Java version:** See `src/` directory
- **Analysis notebooks:** See `python/` directory for Jupyter notebooks

---

# Acknowledgements
- Thanks to my research colleagues for inspiring this project, with special thanks to Malo for refuelling my motivation
- Thanks to the open-source community for libraries and tools used in this project
- Thanks to Copilot for code suggestions and documentation help
