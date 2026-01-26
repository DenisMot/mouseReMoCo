# Python Notebook Architecture - test-tablet.ipynb

## Overview
A PyQt6-based application for testing Wacom tablet input, with support for circular and linear tasks, performance tracking, and data output to CSV and LSL (Lab Streaming Layer).

---

## Class Hierarchy & Relationships

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         APPLICATION ARCHITECTURE                         │
└──────────────────────────────────────────────────────────────────────────┘

┌─ INITIALIZATION ─────────────────────────────────────────────────────────┐
│  main()  →  QApplication (PyQt6)  →  WindowSetup (Orchestrator)         │
│                                         ├─→ Configuration                │
│                                         ├─→ AppStatus                    │
│                                         ├─→ ScreenManager                │
│                                         └─→ MainWindow                   │
└──────────────────────────────────────────────────────────────────────────┘

┌─ RUNTIME - EVENT LOOP ───────────────────────────────────────────────────┐
│                                                                          │
│  Qt Events → MainWindow → DataCapture → {Processing Phase}              │
│                            ├─ extract x, y, pressure, timestamps         │
│                            └─ circle detection (single computation)       │
│                                  ↓                                        │
│                    ┌─────────────┴─────────────┐                         │
│                    │                           │                         │
│                IF recording:              ALWAYS:                        │
│                OutputTablet               Trail.add_point()              │
│                ├─ CSVBackend              CircularTargetWidget           │
│                └─ LSLBackend              CursorFactory                  │
│                                                                          │
│  Display: MainWindow.paintEvent()                                        │
│  ├─ CircularTargetWidget.draw()                                          │
│  ├─ Trail.draw()                                                         │
│  ├─ Mode indicator                                                       │
│  └─ Debug rectangles                                                     │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Cell-by-Cell Breakdown (14 Cells)

### **Cell 1: Configuration Class**
Central configuration management mirroring Java's `Configuration.java`. Handles screen setup, circular/linear task parameters, visual styling, and all application settings.

### **Cell 2: ScreenManager & ScreenInfo**
Screen detection and management utilities. `ScreenInfo` data class holds metadata (DPI, resolution, physical size). `ScreenManager` provides static methods for querying screen information.

### **Cell 3: CursorFactory**
Factory for creating custom cursor images with filled circles and crosshairs. Methods: `create_cursor()`, `create_record_cursor()` (red), `create_wait_cursor()` (yellow), `create_out_cursor()` (darkened).

### **Cell 4: CircularTaskConfig & CircularTargetWidget**
Configuration and rendering for circular target. `CircularTaskConfig` defines render parameters. `CircularTargetWidget` draws the target circle with inner/outer radius, border styling, and path visualization.

### **Cell 5: AppStatus**
Centralized application state management. Tracks recording state (on/paused/duration), input device type (mouse vs tablet), display state (fullscreen), trail mode, and task execution state.

### **Cell 6: WindowSetup (Orchestrator)**
Complete window initialization pipeline:
1. `initialize_screens()` - Detect and select target screen
2. `calculate_initial_radii()` - Compute circle dimensions
3. `create_widget()` - Create MainWindow widget
4. `measure_and_correct_dimensions()` - Account for window frame insets
5. `finalize_display()` - Set up output and display window

### **Cell 7: Trail Class**
Comet trail rendering and path management. `add_point()` records cursor positions with timestamps. Implements path-length based fading, pressure/tilt tracking, and output integration.

### **Cell 8: OutputTablet & Output Backends**
Unified output management with pluggable backends.
- **OutputBackend** (abstract base) with two implementations:
  - `CSVBackend` - Write to `data.csv` and `marker.csv` with subpixel precision (2 decimal places)
  - `LSLBackend` - Stream via Lab Streaming Layer (optional)
- `OutputTablet` manages multiple backends simultaneously

### **Cell 9: DataCapture Class**
Centralized event data extraction and normalization. `capture_tablet_event()` and `capture_mouse_event()` extract all relevant data once per event. `_is_point_inside_circle()` is the single computation point for expensive circle detection. Returns normalized dict with x, y, pressure, timestamps, is_inside flag.

### **Cell 10: MainWindow (Core Widget)**
Main application window managing all event handling and rendering.
- **Event Handlers**: `paintEvent()`, `tabletEvent()`, `mouseMoveEvent()`, `keyPressEvent()`
- **Control Methods**: `_toggle_recording()`, `_toggle_fullscreen()`, `_quit_application()`, `closeEvent()`
- **Key Attributes**: `data_capture`, `trail`, `circular_target`, `output_data`, `status`

### **Cell 11: Application Execution**
Initializes QApplication, creates WindowSetup, executes initialization pipeline:
1. Create or retrieve Qt application singleton
2. Create WindowSetup (owns Configuration internally)
3. Call `window_setup.create_and_display()` 
4. Update configuration after drawable area is known
5. Execute Qt event loop via `app.exec()`

### **Cell 12: Data Analysis - Load & Clean**
Post-recording data analysis. Loads CSV with proper header skipping, converts timestamps to datetime, calculates latency (call_time - event_timestamp), detects/handles NaN values, calculates sampling frequency.

### **Cell 13: Performance Statistics**
Calculates performance metrics: mean/median latency, sampling frequency statistics, NaN counts, recording duration, data quality assessment.

### **Cell 14: Visualization & Plotting**
Visual analysis of recorded data. Generates latency histograms, time series plots, sampling frequency analysis, 2D trajectory plots, and summary statistics.

---

## Detailed Data Flow

```
┌─ INPUT PHASE ───────────────────────────────────────────────────────────┐
│  Qt Event Loop  →  TabletEvent / MouseMoveEvent / KeyPressEvent         │
│                 →  MainWindow event handler                              │
└──────────────────────────────────────────────────────────────────────────┘

┌─ PROCESSING PHASE ──────────────────────────────────────────────────────┐
│  DataCapture.capture_*_event()                                           │
│  ├─ Extract coordinates (x, y)                                           │
│  ├─ Get event timestamp (ms)                                             │
│  ├─ Compute call time (system time)                                      │
│  ├─ Circle detection: _is_point_inside_circle()  [expensive - once only]│
│  └─ Get pressure (tablet) or 0.0 (mouse)                                 │
│     Returns: {x, y, pressure, event_timestamp_ms, computed_timestamp_ms, │
│              is_inside, input_type}                                       │
└──────────────────────────────────────────────────────────────────────────┘

┌─ DECISION GATE ─────────────────────────────────────────────────────────┐
│                                                                          │
│  IF is_recording == True:                                                │
│    └─→ OutputTablet.write_data()                                         │
│        ├─→ CSVBackend.write_data()    [data.csv with subpixel precision]│
│        └─→ LSLBackend.write_data()    [if enabled]                       │
│                                                                          │
│  ALWAYS [regardless of recording]:                                       │
│    └─→ Trail.add_point()              [for display rendering]            │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌─ DISPLAY PHASE ─────────────────────────────────────────────────────────┐
│  Cursor Update: _update_cursor_for_position(x, y)                        │
│  └─ Color based on distance from circle center                           │
│                                                                          │
│  Repaint Request: MainWindow.update()                                    │
│  └─ Triggers paintEvent()                                                │
│     ├─ CircularTargetWidget.draw()   [target circle]                     │
│     ├─ Trail.draw()                  [comet trail]                       │
│     ├─ _draw_mode_indicator()        [mode + recording status]           │
│     └─ _draw_limits_rectangles()     [debug overlay]                     │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Recording Workflow (Event-Driven)

### Phase 1: Toggle Recording State
```
User presses SPACE
    ↓
MainWindow.keyPressEvent() detects SPACE
    ↓
MainWindow._toggle_recording()
    ↓
AppStatus.toggle_recording()
    ├─ IF is_recording was False:
    │   ├─ is_recording = True
    │   └─ recording_start_time = time.time()
    │
    └─ IF is_recording was True:
        ├─ is_recording = False
        ├─ elapsed = time.time() - recording_start_time
        ├─ total_recording_duration += elapsed
        └─ pause_count += 1
    ↓
OutputTablet.write_marker("RecordingStarted" or "RecordingPaused")
    ↓
MainWindow.update() [request repaint]
    └─ _draw_mode_indicator() shows updated status (● RECORDING or ○ PAUSED)
```

### Phase 2: Continuous Event Capture Loop
```
WHILE Application.exec() running:
    │
    ├─ User moves mouse or tablet [OS event]
    │
    ├─→ Qt Event Loop dispatches event
    │
    ├─→ MainWindow.mouseMoveEvent() OR tabletEvent()
    │   │
    │   ├─→ DataCapture.capture_*_event()
    │   │   └─ Extract: x, y, pressure, timestamps, is_inside
    │   │
    │   ├─→ Decision Gate:
    │   │   │
    │   │   IF is_recording == True:
    │   │   │   └─→ OutputTablet.write_data()
    │   │   │       ├─→ CSVBackend.write_data() [data.csv]
    │   │   │       └─→ LSLBackend.write_data() [if enabled]
    │   │   │
    │   │   ELSE:
    │   │       └─→ Skip CSV/LSL write
    │   │
    │   ├─→ ALWAYS:
    │   │   └─→ Trail.add_point()
    │   │       [Update comet trail for display, regardless of recording]
    │   │
    │   ├─→ Cursor Update:
    │   │   └─→ _update_cursor_for_position(x, y)
    │   │       [Change color based on target distance]
    │   │
    │   └─→ MainWindow.update() [request repaint]
    │       └─→ Qt schedules paintEvent()
    │           └─→ Render circular target, trail, indicators
    │
    └─ [Loop continues until user presses Q]
```

### Phase 3: Application Exit
```
User presses Q
    ↓
MainWindow.keyPressEvent() detects 'q'
    ↓
MainWindow._quit_application()
    │
    ├─ Disable all input: setEnabled(False)
    │
    └─→ IF fullscreen_mode == 1:
        ├─ _toggle_fullscreen() [return to windowed]
        └─ QTimer.singleShot(1000ms, self.close)
            [1 second delay for macOS window state to settle]
    ↓
MainWindow.closeEvent() triggered (or after timer)
    │
    ├─ IF still recording:
    │   ├─ AppStatus.pause_recording()
    │   └─ OutputTablet.write_marker("RecordingEnded")
    │
    ├─ OutputTablet.close()
    │   ├─ CSVBackend.close() [flush and close data.csv, marker.csv]
    │   └─ LSLBackend.close() [close LSL outlets]
    │
    └─ event.accept()
        ↓
    Application.exec() returns
        ↓
    Post-Recording Analysis [Cells 12-14]
```

---

## Recording State Management

### AppStatus Tracks Recording Duration
```python
class AppStatus:
    is_recording: bool                  # Toggle flag (True/False)
    recording_start_time: float         # time.time() when started
    total_recording_duration: float     # Accumulated seconds across pause/resume
    pause_count: int                    # Number of pause events
    
    def start_recording():              # Sets is_recording=True, records start_time
    def pause_recording():              # Adds elapsed to total, increments pause_count
    def toggle_recording():             # Calls pause() if running, start() if paused
```

### Recording Decision Gate
```python
IF output_data and is_recording == True:
    output_data.write_data(...)         # Write to CSV
ELSE:
    # Skip writing - event is still captured in Trail for display
```

**Critical Point**: Trail always updates (for comet trail visualization), but CSV output only writes when `is_recording == True`. This allows visual feedback without recording.

### CSV Output Structure
```
data.csv:
  Header 1: Configuration string (screen, circle params)
  Header 2: ISO8601 timestamp
  Header 3: Column names (event_timestamp, call_time, mouseX, mouseY, ...)
  Rows:     Data rows with subpixel precision (2 decimal places)

marker.csv:
  Header 1: Configuration string
  Header 2: ISO8601 timestamp
  Header 3: Column names (timestamp, milliseconds, marker)
  Rows:     "RecordingStarted", "RecordingPaused", "RecordingEnded", etc.
```

---

## Timer Usage

**Only Timer in Application**: `QTimer.singleShot(1000, self.close)` in `_quit_application()`
- **Purpose**: macOS fullscreen close workaround
- **Duration**: 1000 milliseconds (1 second)
- **Trigger**: When user presses Q while in fullscreen mode
- **Reason**: Allows window state to settle before closing

**Recording Duration Tracking**: NOT timer-based. Duration is calculated by subtracting timestamps:
- `elapsed = time.time() - recording_start_time`
- No periodic `QTimer` for recording

---

## Key Design Patterns

| Pattern | Usage | Example |
|---------|-------|---------|
| **Singleton-like** | AppStatus, Configuration | Single instance manages all state |
| **Factory** | CursorFactory | Create variants of cursors |
| **Strategy** | OutputBackend (CSV/LSL) | Pluggable output backends |
| **Observer** | Qt event handlers | React to mouse/tablet/keyboard |
| **Orchestrator** | WindowSetup | Coordinate complex initialization |
| **Builder** | CircularTaskConfig | Configure complex objects |

---

## Keyboard Controls

| Key | Action | Effect |
|-----|--------|--------|
| **SPACE** | Toggle Recording | Start/pause data logging to CSV |
| **Q** | Quit Application | Graceful shutdown with cleanup |
| **C** | Print Configuration | Output current config to console |
| **F** | Toggle Fullscreen | Switch windowed ↔ borderless fullscreen |

---

## File Output

When recording is enabled, the notebook creates:
- **data.csv** - Position data with subpixel precision, timestamps, pressure
- **marker.csv** - Event markers (RecordingStarted, RecordingPaused, TabletDetected, etc.)

---

## Dependencies

| Package | Purpose | Required |
|---------|---------|----------|
| **PyQt6** | GUI framework (events, widgets, painting) | ✅ Yes |
| **numpy** | Numeric operations (distance calculations) | ✅ Yes |
| **pandas** | Data analysis (post-recording CSV analysis) | ✅ Yes |
| **matplotlib** | Visualization (latency plots, trajectories) | ✅ Yes |
| **pylsl** | Lab Streaming Layer (optional real-time streaming) | ⚠️ Optional |

---

## Architecture Summary

The notebook implements a **modular, event-driven testing framework** organized into three distinct phases:

### Initialization Phase (Cells 1-7)
- **Configuration** defines all parameters
- **WindowSetup** orchestrates the complete initialization pipeline
- **ScreenManager** detects and selects target display
- All UI components created with corrected dimensions

### Runtime Phase (Cells 8-11)
- **MainWindow** continuously processes Qt events from tablet/mouse/keyboard
- **DataCapture** normalizes event data once per event
- **AppStatus** maintains simple on/off recording flag
- **Trail** always renders comet path (for visual feedback)
- **OutputTablet** conditionally writes to CSV/LSL based on recording flag
- This event-driven loop ensures responsive, low-latency input handling

### Analysis Phase (Cells 12-14)
- **Data Loading** reads CSV files with proper header handling
- **Performance Metrics** calculates latency, sampling frequency, data quality
- **Visualization** plots trajectories, latency histograms, statistics

### Key Design Principles

**1. Event-Driven (NOT Timer-Based)**
- Recording is controlled by a boolean flag, not periodic timers
- Duration calculated by timestamp subtraction, not tick counting
- Events flow through Qt event loop with zero artificial delays

**2. Single Computation Point**
- DataCapture extracts all event data once
- Circle detection performed once per event (expensive operation)
- Results reused for output, trail, and cursor updates

**3. Decoupled Output**
- Trail always updates (for display)
- CSV/LSL only write when recording flag is True
- Pluggable backend architecture (OutputBackend strategy)

**4. Subpixel Precision**
- Coordinates stored as floats (x.xx)
- CSV output rounded to 2 decimal places
- LSL uses float32 for full precision

This architecture mirrors the Java application while leveraging PyQt6's efficient, event-driven model for responsive, real-time interaction.
