# mouseReMoCo - Wacom Tablet Test

Prototype of a research application for testing circular target tracing with pen tablets.

This is a Python/PyQt6 (incomplete) version of the original Java application with support for pressure-sensitive tablets.

**Version:** 2.0.0 (Python/PyQt6)

---

## Quick Start

### 1. Clone Repository

- Manually create a directory named `mouseReMoCo-app` 
- Open a terminal and move in `mouseReMoCo-app` 
- Run 
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

### 2. Setup Environment (Conda)

Create and activate a conda environment:

```bash
    conda env create -f environment.yml
    conda activate mouseremoco
```


### 3. Run Application

- Open a terminal and move in `mouseReMoCo-app` 
- Run the application: 
```bash
    python mouseReMoCo/main.py
```

The `data.csv` and `marker.csv` files will be created in the `mouseReMoCo-app` directory after running the application, rendering the following structure:

```
mouseReMoCo-app/
├── data.csv                      ← Generated data (runtime)
├── marker.csv                    ← Generated markers (runtime)
└── mouseremoco/
    └── python/                   ← Python package
        └── main.py               ← Entry point
```

---

## Controls

| Key | Action |
|-----|--------|
| **SPACE** | Toggle record/pause |
| **C** | Print configuration to console |
| **Q** | Quit application |

---

## Output Files

After running the application, two CSV files are generated in the `python/` directory:

### `data.csv`
Contains tablet/mouse position and pressure data:
- `event_timestamp` - Hardware event timestamp (ms, with epoch 0 at Jan 1, 1970).
- `call_time` - System time when handler was called (ms, with epoch 0 at system start)
- `mouseX`, `mouseY` - Cursor position (sub-pixel precision)
- `mouseInTarget` - 1 if inside tolerance band, 0 otherwise
- `pressure` - Stylus pressure (0.0-1.0)
- `tiltX`, `tiltY` - Stylus tilt angles (-60° to +60°)

IMPORTANT NOTES: 
- `pressure`, `tiltX`, and `tiltY` are 0 when using mouse input.
- `event_timestamp` is standard UNIX time; use it for synchronization across devices.
- `call_time` it the exact time stamp of mouse-tablet interaction: use it for all analyses. 
- Sampling rate varies based on hardware and system load: it is NOT constant.

### `marker.csv`
Contains event markers for experiment synchronization:
- `timestamp` - Human-readable timestamp
- `milliseconds` - Epoch milliseconds (for automated sync)
- `marker` - Event description (e.g., "RecordingStarted", "TabletDetected")

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

Edit `main.py` before `create_and_display()` to customize:

```python
# Customize before window setup
window_setup.update_configuration(
#    cursor_radius=20,              # Change cursor size
#    external_radius=200,           # Change target size
#    trail_length=500,              # Trail length (pixels)
)
```

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
- **numpy** - Numerical operations 


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

**Last updated:** January 28, 2026
