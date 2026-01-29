# MainWindow - Main application window

import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPen, QTabletEvent
from PyQt6.QtWidgets import QApplication, QWidget

from .cursor import CursorFactory
from .target import CircularTargetWidget
from .trail import Trail
from ..input.capture import DataCapture
from ..types import AppStatus
from ..geometry import is_inside as geom_is_inside


class MainWindow(QWidget):
    """Main application window handling rendering and input events."""

    # Map keyboard keys to trail modes from Trail class
    # Dynamically built to stay in sync if Trail.VALID_MODES changes
    TRAIL_MODES = {str(i + 1): mode for i, mode in enumerate(Trail.VALID_MODES)}

    # Command dispatch mapping for keyboard shortcuts
    KEY_COMMANDS = {
        "q": "_quit_application",
        "c": "_print_config",
        " ": "_toggle_recording",
        "w": "_increase_band_width",
        "x": "_decrease_band_width",
        "p": "_increase_band_center",
        "m": "_decrease_band_center",
        "s": "_toggle_smoothing",
        # 'f': '_toggle_fullscreen', # only for testing:
        # !!! screen size must not change during task !!!
    }

    def __init__(
        self,
        config=None,
        window_setup=None,
        output_data=None,
        app_status=None,
    ):
        # arguments checks
        if config is None:
            raise ValueError("Config must be provided to MainWindow.")
        if window_setup is None:
            raise ValueError("WindowSetup must be provided to MainWindow.")
        if app_status is None:
            pass  # will create new AppStatus instance in the end of __init__

        super().__init__()
        self.config = config
        self.window_setup = window_setup
        self.data_capture = DataCapture(config) if config else None
        self.circular_target = CircularTargetWidget(
            config=self.window_setup.circle_config
        )

        # Single trail with tablet detection awareness
        self.trail = Trail(config, app_status=app_status)
        self.last_mouse_x = None
        self.last_mouse_y = None

        # Accept OutputData passed from WindowSetup (created after config correction)
        self.output_data = output_data
        if self.output_data:
            self.trail.output_data = self.output_data

        # Use shared AppStatus instance from WindowSetup
        self.status = app_status if app_status else AppStatus()

        # Enable mouse tracking to receive mouseMoveEvent even when no button is pressed
        self.setMouseTracking(True)
        self.setFocus()

        # Print controls on startup
        self._print_control_instructions()

    def paintEvent(self, event):
        """Handle all drawing operations"""
        painter = QPainter(self)
        # Use background color from config, or default to black
        if self.config and self.config.background_color:
            bg_color = QColor(*self.config.background_color)
        else:
            bg_color = Qt.GlobalColor.black
        painter.fillRect(self.rect(), bg_color)

        # Draw the circular target
        self.circular_target.draw(painter, self.config.center_x, self.config.center_y)

        # Draw the unified trail
        self.trail.draw(painter, self.config.center_x, self.config.center_y)

        # Draw mode indicator on screen
        self._draw_mode_indicator(painter)

        # Optionally draw limits rectangles for debugging
        self._draw_limits_retangles(painter)

    def _draw_limits_retangles(self, painter: QPainter):
        """Draw non-filled rectangles showing drawable screen limits"""
        # Draw green-yellow rectangles showing drawable screen limits

        original_brush = painter.brush()
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # small shift to see the border more clearly (-1,suppresses the green rect)
        shift = 0
        painter.setPen(QPen(Qt.GlobalColor.green, 1))

        # get screen dimensions from config
        screen_width = self.config.screen_width
        screen_height = self.config.screen_height

        # Outer rectangle (green)
        painter.drawRect(
            shift,
            shift + 1,  # drawRect needs this correction (test on OSx)
            screen_width - 2 * shift,
            screen_height - 2 * shift - 1,
        )
        # Inner rectangle (yellow)
        shift += 5
        painter.setPen(QPen(Qt.GlobalColor.yellow, 1))
        painter.drawRect(
            shift,
            shift + 1,
            screen_width - 2 * (shift),
            screen_height - 2 * (shift) - 1,
        )
        painter.setBrush(original_brush)

    def _draw_string_in_corner(
        self, painter: QPainter, text: str, x: int, y: int, corner: str, color: QColor
    ):
        """Draw a string at specified corner coordinates"""
        painter.setPen(QPen(color))
        fm = painter.fontMetrics()
        text_w = fm.horizontalAdvance(text)
        text_h = fm.height()

        if corner == "top-left":
            painter.drawText(x, y + text_h, text)
        elif corner == "top-right":
            painter.drawText(self.width() - text_w - x, y + text_h, text)
        elif corner == "bottom-left":
            painter.drawText(x, self.height() - y, text)
        elif corner == "bottom-right":
            painter.drawText(self.width() - text_w - x, self.height() - y, text)

    def _draw_mode_indicator(self, painter: QPainter):
        """Draw current trail mode and recording status in corner"""

        # Pressure band info
        center = getattr(self.config, "pressure_band_center", 0.5)
        width = getattr(self.config, "pressure_band_width", 0.4)
        # low = max(0.0, center - width / 2)
        # high = min(1.0, center + width / 2)q

        low = center - width / 2
        high = center + width / 2
        # allow display of out-of-bounds values for debugging
        band_text = f"{center:.2f}+/-{width/2:.2f} [{low:.2f} , {high:.2f}]"

        # Draw texts in top-left corner with some margin
        margin = 10
        self._draw_string_in_corner(
            painter,
            f"Mode: {self.config.trail_mode.upper()}",
            x=margin,
            y=margin,
            corner="top-left",
            color=QColor(Qt.GlobalColor.white),
        )
        status_color = (
            Qt.GlobalColor.green if self.status.is_recording else Qt.GlobalColor.red
        )
        self._draw_string_in_corner(
            painter,
            "● RECORDING" if self.status.is_recording else "○ PAUSED",
            x=margin,
            y=margin + 20,
            corner="top-left",
            color=(
                Qt.GlobalColor.green if self.status.is_recording else Qt.GlobalColor.red
            ),
        )
        # Show pressure band info only when a tablet has been detected
        if getattr(self.status, "tablet_detected", False):
            self._draw_string_in_corner(
                painter,
                band_text,
                x=margin,
                y=margin + 40,
                corner="top-left",
                color=QColor(Qt.GlobalColor.white),
            )

    def _toggle_recording(self):
        """Toggle recording on/off with spacebar"""
        self.status.toggle_recording()

        # Write marker to CSV
        marker = "RecordingStarted" if self.status.is_recording else "RecordingPaused"
        if self.output_data:
            self.output_data.write_marker(marker)

        # Print status to console (use unified method)
        self._print_status(self.status.get_status_string())

        # Redraw screen
        self.update()

    def _print_config(self):
        """Print configuration to console"""
        print("\n" + "=" * 60)
        print(self.config.to_string())
        print("=" * 60 + "\n")

    def _print_status(self, title: str, message: str = ""):
        """Print formatted status message with consistent formatting.

        Centralizes console output for status updates, making it easy to:
        - Redirect output to logs or UI
        - Change formatting globally
        - Suppress output (e.g., in tests)

        Args:
            title: Main message/title to display
            message: Optional secondary message (printed on new line if provided)
        """
        print("\n" + "=" * 60)
        print(title)
        if message:
            print(message)
        print("=" * 60 + "\n")

    def _print_fullscreen_status(self, mode: str):
        """Print fullscreen mode change notification.

        Args:
            mode: Either "BORDERLESS" or "WINDOWED"
        """
        if mode.upper() == "BORDERLESS":
            self._print_status(
                "✓ Fullscreen Mode Changed",
                "Switched to BORDERLESS FULLSCREEN (no system UI access)",
            )
        else:
            self._print_status("✓ Fullscreen Mode Changed", "Switched to WINDOWED mode")

    # --- Pressure band adjustment handlers ---
    def _increase_band_width(self):
        if not getattr(self.status, "tablet_detected", False):
            self._print_status(
                "Pressure band inactive",
                "No tablet detected — band controls disabled.",
            )
            return

        self.config.pressure_band_width += 0.02
        self.config._update_pressure_band("width")
        self._print_status(f"Band width={self.config.pressure_band_width:.2f}", "")
        self.update()

    def _decrease_band_width(self):
        if not getattr(self.status, "tablet_detected", False):
            self._print_status(
                "Pressure band inactive",
                "No tablet detected — band controls disabled.",
            )
            return

        self.config.pressure_band_width -= 0.02
        self.config._update_pressure_band("width")
        self._print_status(f"Band width={self.config.pressure_band_width:.2f}", "")
        self.update()

    def _increase_band_center(self):
        if not getattr(self.status, "tablet_detected", False):
            self._print_status(
                "Pressure band inactive",
                "No tablet detected — band controls disabled.",
            )
            return

        self.config.pressure_band_center += 0.02
        self.config._update_pressure_band("center")
        self._print_status(f"Band center={self.config.pressure_band_center:.2f}", "")
        self.update()

    def _decrease_band_center(self):
        if not getattr(self.status, "tablet_detected", False):
            self._print_status(
                "Pressure band inactive",
                "No tablet detected — band controls disabled.",
            )
            return

        self.config.pressure_band_center -= 0.02
        self.config._update_pressure_band("center")
        self._print_status(f"Band center={self.config.pressure_band_center:.2f}", "")
        self.update()

    def _toggle_smoothing(self):
        """Toggle visual-only smoothing for the trail"""
        current = getattr(self.trail, "visual_smoothing", True)
        self.trail.visual_smoothing = not current
        state = "ON" if self.trail.visual_smoothing else "OFF"
        self._print_status(f"Visual smoothing: {state}")
        self.update()

    def _toggle_fullscreen(self):
        """Toggle between windowed and borderless fullscreen"""
        if self.status.fullscreen_mode == 0:
            # Switch to borderless fullscreen (no system UI)
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            self.setGeometry(self.screen().geometry())
            self.showFullScreen()
            self.status.fullscreen_mode = 1
            self._print_fullscreen_status("BORDERLESS")
        else:
            # Return to windowed
            self.setWindowFlags(Qt.WindowType.Widget)
            self.showNormal()
            self.status.fullscreen_mode = 0
            self._print_fullscreen_status("WINDOWED")

        # Process events to apply window state changes
        QApplication.instance().processEvents()

        # Recalculate drawable dimensions using WindowSetup's method
        if self.window_setup:
            self.window_setup.measure_and_correct_dimensions()

        self.setFocus()

    def _print_tablet_detected(self):
        """Print tablet detection confirmation"""
        self._print_status("✓ Tablet detected and active!")

    def _print_control_instructions(self):
        """Print keyboard control instructions on startup"""
        print(
            f"\n{'='*60}\nControls:\n"
            f"Press F: Toggle Fullscreen (Windowed ↔ Borderless)\n"
            f"Press C: Print Configuration\n"
            f"Press Q: Quit\n"
            f"Press SPACE: Toggle Record/Pause\n"
            f"Press W / X: Increase / Decrease pressure-band WIDTH\n"
            f"Press P / M: Move pressure-band CENTER up / down (tablet only)\n"
            f"Press S: Toggle visual smoothing ON/OFF\n"
            f"HUD: Band info shown only when a tablet is detected\n"
            f"Note: Changes are immediate and not saved to disk\n"
            f"{'='*60}\n"
        )

    def _quit_application(self):
        """Gracefully quit application, handling fullscreen state"""
        # Disable all input to suppress user interaction during shutdown
        self.setEnabled(False)

        # If in fullscreen, toggle to windowed first, wait 1 sec, then close
        # (fullscreen close is buggy on macOS, so bypass by going windowed first)
        if self.status.fullscreen_mode == 1:
            self._toggle_fullscreen()
            # Delay close by 1 second to let window state settle
            from PyQt6.QtCore import QTimer

            QTimer.singleShot(1000, self.close)
        else:
            # Already windowed, close immediately
            self.close()

    def closeEvent(self, event):
        """Handle window close - exit fullscreen before closing"""
        # If in fullscreen, explicitly return to windowed BEFORE closing
        if self.status.fullscreen_mode == 1:
            self.setWindowFlags(Qt.WindowType.Widget)
            self.showNormal()
            self.status.fullscreen_mode = 0
            # CRITICAL: Let windowing system process state changes before accepting close
            QApplication.instance().processEvents()

        # Stop recording and log end marker before closing
        if self.status.is_recording:
            self.status.pause_recording()
            if self.output_data:
                self.output_data.write_marker("RecordingEnded")
        event.accept()

    def showEvent(self, event):
        """Initialize cursor when widget is shown"""
        super().showEvent(event)
        # Set initial cursor to "out" state
        self.setCursor(CursorFactory.create_out_cursor(self.config))

    def _update_cursor_for_position(self, x: float, y: float):
        """Update cursor color based on distance from circle center"""
        is_inside = geom_is_inside(self.config, x, y)

        if is_inside:
            self.setCursor(CursorFactory.create_record_cursor(self.config))
        else:
            self.setCursor(CursorFactory.create_out_cursor(self.config))

    def _process_input_event(self, data: dict):
        """Unified input processing for both mouse and tablet events.

        Handles all common operations for any input type:
        - Write data to output backends (CSV, LSL)
        - Update trail with position and timestamp
        - Update cursor appearance based on position
        - Trigger screen repaint

        Args:
            data: Dictionary from DataCapture.capture_*_event() containing:
                  x, y, pressure, event_timestamp_ms, computed_timestamp_ms, is_inside
        """
        # Write to CSV/LSL output
        if self.output_data:
            self.output_data.write_data(
                event_timestamp_ms=data["event_timestamp_ms"],
                call_time_ms=data["computed_timestamp_ms"],
                x=data["x"],
                y=data["y"],
                is_inside=data["is_inside"],
                pressure=data["pressure"],
                tilt_x=data.get("tilt_x", 0.0),
                tilt_y=data.get("tilt_y", 0.0),
            )

        # Update trail with captured data
        self.trail.current_pressure = data["pressure"]
        self.trail.current_tilt_x = data.get("tilt_x", 0.0)
        self.trail.current_tilt_y = data.get("tilt_y", 0.0)
        self.trail.add_point(
            data["x"],
            data["y"],
            timestamp_ms=data["event_timestamp_ms"],
            call_time_ms=data["computed_timestamp_ms"],
        )

        # Update cursor based on position
        self._update_cursor_for_position(data["x"], data["y"])

        # Trigger repaint
        self.update()

    def _detect_tablet(self, data: dict):
        """Detect and log first tablet input with pressure."""
        if not self.status.tablet_detected and data["pressure"] > 0:
            self.status.tablet_detected = True
            self.status.active_input_type = "tablet"
            if self.output_data:
                self.output_data.write_marker("TabletDetected")
            self._print_tablet_detected()

    def tabletOrMouseEvent(self, data: dict, is_tablet: bool = False):
        """Orchestrate input event handling for tablet or mouse.

        Central handler that routes input-specific logic while delegating
        common processing to _process_input_event().

        Args:
            data: Dictionary from DataCapture.capture_*_event()
            is_tablet: True for tablet events, False for mouse events
        """
        # Tablet-specific: detect on first input
        if is_tablet:
            self._detect_tablet(data)

        # Common processing for both input types
        self._process_input_event(data)

        # Mouse-specific: store position for reference
        if not is_tablet:
            self.last_mouse_x = data["x"]
            self.last_mouse_y = data["y"]

    def tabletEvent(self, event: QTabletEvent):
        """Handle tablet input event"""
        # Capture data
        data = self.data_capture.capture_tablet_event(event)

        # Process (detect tablet, write output, update trail/cursor/display)
        self.tabletOrMouseEvent(data, is_tablet=True)

        # Mark event as handled
        event.accept()

    def mouseMoveEvent(self, event):
        """Handle mouse movement event"""
        # Capture data
        data = self.data_capture.capture_mouse_event(event)

        # Process (write output, update trail/cursor/display, store position)
        self.tabletOrMouseEvent(data, is_tablet=False)

    def mousePressEvent(self, event):
        """Print mouse click position"""
        print(
            f"Mouse click at: X={event.position().x():.1f}, Y={event.position().y():.1f}"
        )
        sys.stdout.flush()

    def keyPressEvent(self, event):
        """Handle keyboard input using command dispatch"""
        key = event.text()

        # Look up handler method name from KEY_COMMANDS dictionary
        # Use original key for space, lowercased for letter keys
        lookup_key = key if key == " " else key.lower()
        handler_name = self.KEY_COMMANDS.get(lookup_key)

        # Execute handler if found
        if handler_name:
            handler = getattr(self, handler_name, None)
            if handler:
                handler()
