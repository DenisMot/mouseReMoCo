# mouseReMoCo - Wacom Tablet Test

Prototype of a research application for testing circular target tracing with pen tablets.

This is a Python/PyQt6 (incomplete) version of the original Java application with support for pressure-sensitive tablets.

**Version:** 2.0.0 (Python/PyQt6)

---

## Quick Start

### 1. Clone repository and setup conda environment

- Manually create a directory named `mouseReMoCo-app` 
- Open a terminal and move in `mouseReMoCo-app` 
- Run the following commands:
```bash
    git clone --branch python-app --single-branch --depth 1 https://github.com/DenisMot/mouseReMoCo.git 
```
- You now have a copy of the `mouseReMoCo`repository in `mouseReMoCo-app`.

```
mouseReMoCo-app/
└── mouseReMoCo/
    └── python/                   ← Python package
        └── main.py               ← Entry point
```

- Move the terminal in `mouseReMoCo-app/python/` where the `environment.yml` file is located
- Run the following commands:

```bash
    conda env create -f environment.yml
    conda activate mouseremoco
```

- Move the terminal back to `mouseReMoCo-app` where you want the output files to be generated. 


### 3. Run Application

- Open a terminal and move in `mouseReMoCo-app` 
- Run the application: 
```bash
    python mouseReMoCo/python/main.py
```
NB: for windows, path is with backslashes:
```bash
    python mouseReMoCo\python\main.py
```

The `data.csv` and `marker.csv` files will be created in the `mouseReMoCo-app` directory after running the application, rendering the following structure:

```
mouseReMoCo-app/
├── data.csv                      ← Generated data (runtime)
├── marker.csv                    ← Generated markers (runtime)
└── mouseReMoCo/
    └── python/                   ← Python package
        └── main.py               ← Entry point
```

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

**Note:** Pressure band adjustment requires a tablet to be detected (first stylus press activates).

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

## Lab Streaming Layer (LSL) Output (Optional)

Lab Streaming Layer (LSL) enables **real-time streaming** of mouse/tablet data to external applications like LabRecorder, enabling synchronized multi-device recording.

### Prerequisites

LSL is **optional**. To use it:

1. Install pylsl:
   ```bash
   pip install pylsl
   ```

2. Download and install **LabRecorder** from [LSL documentation](https://labstreaminglayer.readthedocs.io/)

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

**Data precision:** Uses double64 format for exact timestamp accuracy (avoids float32 rounding errors).

### Recording with LabRecorder

1. Start LabRecorder (available before or after mouseReMoCo)
2. LabRecorder automatically discovers the three streams
3. Select them for recording
4. Click "Start Recording"
5. Run mouseReMoCo normally
6. Close mouseReMoCo (shows reminder if LabRecorder is recording)
7. Stop LabRecorder → generates `.xdf` file with synchronized data

### LSL Metadata

All streams include the same metadata found in *.csv file header:

- **configuration_str** - Configuration settings (same as first line of `data.csv`)
- **timestamp_str** - ISO8601 session start time (same as second line of `data.csv`)


---

## Project Structure

```
python/
├── main.py                           ← Entry point
├── environment.yml                   ← Conda environment (preferred)
├── requirements.txt                  ← Pip requirements (optional)
├── README.md                         ← This file
│
├── mouseremoco/                      ← Python package
│   ├── __init__.py
│   ├── app_config.py                 ← Centralized configuration (edit this!)
│   ├── config.py                     ← Configuration classes
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
│       └── manager.py                ← Output manager
│
├── data.csv                          ← Generated data (runtime)
├── marker.csv                        ← Generated markers (runtime)
└── test-tablet.ipynb                 ← Original notebook (archive)
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

All parameters have sensible defaults. Changes take effect immediately on restart—no build required.

---

## Tablet Detection

The application automatically detects pressure-sensitive devices (e.g., Wacom tablets):
- **First stylus press** triggers tablet detection
- Trail color changes: **Blue (mouse) → Red (tablet)**
- Pressure-sensitive trail thickness when using tablet

Check console output for tablet detection status.

---

## Troubleshooting

### "No tablet detected - will use mouse input only"

**Solution:** Check Wacom driver installation and tablet connectivity.

### Cannot write CSV files

**Solution:** Ensure write permissions in the directory where the application is running.

### Poor performance / high latency

**Solution:**
- Close other applications
- Check CPU usage
- Verify hardware tablet drivers are up-to-date

---




## Dependencies

- **PyQt6** - Cross-platform GUI framework 
- **pylsl** - Lab Streaming Layer for real-time data streaming
- **psutil** - System monitoring

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
- Thanks to the open-source community for libraries and tools used in this project
- Thanks to Copilot for code suggestions and documentation help!