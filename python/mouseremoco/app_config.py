"""
Central configuration file for all application startup parameters.

Modify these values to customize the application behavior without editing
multiple files throughout the codebase.
"""

from PyQt6.QtCore import Qt

# ===== Software =====
SOFTWARE_NAME = "mouseReMoCo-Python"
SOFTWARE_VERSION = "2.0.0"

# ===== Window & Display =====
WINDOW_TITLE = "Wacom Tablet Test"
TARGET_MONITOR = 2  # Which monitor to use (1-indexed)
WINDOW_WIDTH = None  # None = auto-size to screen
WINDOW_HEIGHT = None  # None = auto-size to screen
BACKGROUND_COLOR = (0, 0, 0)  # RGB black
FRAME_UNDECORATED = False

# ===== Circular Task Parameters =====
EXTERNAL_RADIUS = 150  # pixels - outer circle radius
INTERNAL_RADIUS = 80  # pixels - inner circle radius
BORDER_RADIUS = 1  # pixels
NB_CURSOR_RADII_FOR_TARGET_MARGIN = 5  # scaling factor for margin

# ===== Visual Styling =====
CURSOR_RADIUS = 16  # pixels
CURSOR_COLOR_RECORDING = (255, 0, 0)  # RGB red
CURSOR_COLOR_WAITING = (255, 255, 0)  # RGB yellow
BORDER_COLOR = (255, 255, 255)  # RGB white
TEXT_COLOR = (255, 255, 255)  # RGB white
FONT_SIZE = 20
FONT_FAMILY = "Courier"

# ===== Recording & Sequence =====
AUTO_START_DELAY = 3600  # seconds before auto start
CYCLE_MAX_NUMBER = 6  # number of Move-Rest cycles
CYCLE_DURATION = 20  # seconds per half-cycle (Move or Rest)
HIDE_TARGET_DURING_PAUSE = False

# ===== Trail Configuration =====
TRAIL_MODE = "path_length"  # Active trail mode
TRAIL_LENGTH = None  # None = 10× cursor_radius (derived at runtime)

# ===== Pressure Band Configuration (0.0 - 1.0) =====
# Band defined by a center and full width; low/high derived at runtime
PRESSURE_BAND_CENTER = 0.5
PRESSURE_BAND_WIDTH = 0.4

# ===== Output Backends =====
ENABLE_CSV = True  # Enable CSV file output
ENABLE_LSL = True  # Enable Lab Streaming Layer (LSL) output

# ===== Audio Parameters =====
RHYTHM_HALF_PERIOD_MS = 2000  # milliseconds for auditory rhythm half-period

# ===== Linear Task Parameters (for future use) =====
INTER_LINE_DISTANCE_MM = 150
LINE_HEIGHT_MM = 100

# ===== Keyboard Controls =====
# Unified command dispatch mapping using Qt.Key enum for all keys
# Provides consistent, type-safe key binding configuration
KEY_COMMANDS = {
    Qt.Key.Key_Q: "_quit_application",
    Qt.Key.Key_C: "_print_config",
    Qt.Key.Key_Space: "_toggle_recording",
    Qt.Key.Key_S: "_toggle_smoothing",
    Qt.Key.Key_G: "_toggle_pressure_gauge_visibility",
    Qt.Key.Key_Up: "_increase_band_center",
    Qt.Key.Key_Down: "_decrease_band_center",
    Qt.Key.Key_Right: "_increase_band_width",
    Qt.Key.Key_Left: "_decrease_band_width",
}


# ===== Derived Colors (computed from recording color) =====
# These are automatically calculated in config.py based on CURSOR_COLOR_RECORDING
# They represent a darkened version for visual distinction
def _calculate_recording_outside_color():
    """Calculate the outside recording color (darkened version)"""
    r, g, b = CURSOR_COLOR_RECORDING
    return (
        max(0, r // 2),
        max(0, g // 2),
        max(0, b // 2),
    )


CURSOR_COLOR_RECORDING_OUTSIDE = _calculate_recording_outside_color()
