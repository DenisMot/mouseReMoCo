# MainWindow - Main application window

import sys

from PyQt6.QtCore import Qt, QTimer, QObject
from PyQt6.QtGui import QColor, QPainter, QPen, QTabletEvent, QFont, QFontMetrics
from PyQt6.QtWidgets import QApplication, QWidget

from .cursor import CursorFactory
from .target import CircularTargetWidget
from .trail import Trail
from ..input.capture import DataCapture
from ..types import AppStatus
from ..geometry import is_inside as geom_is_inside
from .. import app_config


class TabletProximityFilter(QObject):
    """Global event filter to detect tablet proximity events"""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def eventFilter(self, obj, event):
        """Intercept proximity events at application level"""
        if event.type() == QTabletEvent.Type.TabletEnterProximity:

            self.main_window.status.tablet_detected = True
            self.main_window.status.active_input_type = "tablet"
            if self.main_window.output_data:
                self.main_window.output_data.write_marker("TabletDetected")
            self.main_window._print_status("✓ Tablet detected and active!")

            return False  # Continue processing

        elif event.type() == QTabletEvent.Type.TabletLeaveProximity:
            self.main_window.status.tablet_detected = False
            self.main_window.status.active_input_type = "mouse"
            if self.main_window.output_data:
                self.main_window.output_data.write_marker("TabletLeftProximity")
            self.main_window._print_status(
                "✓ Tablet left proximity (no longer detected)"
            )

            return False

        return super().eventFilter(obj, event)


class MainWindow(QWidget):
    """Main application window handling rendering and input events."""

    # Map keyboard keys to trail modes from Trail class
    # Dynamically built to stay in sync if Trail.VALID_MODES changes
    TRAIL_MODES = {str(i + 1): mode for i, mode in enumerate(Trail.VALID_MODES)}

    # Import unified keyboard commands from app_config
    KEY_COMMANDS = app_config.KEY_COMMANDS

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

        # Flag to track goodbye mode (showing "bye" message before exit)
        self.goodbye_mode = False

        # Flag to track pressure gauge visibility
        self.show_pressure_gauge = True

        # Enable mouse tracking to receive mouseMoveEvent even when no button is pressed
        self.setMouseTracking(True)
        self.setFocus()

        # Print controls on startup
        self._print_control_instructions()

        # Install global tablet proximity event filter
        self.tablet_proximity_filter = TabletProximityFilter(self)
        QApplication.instance().installEventFilter(self.tablet_proximity_filter)

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

        # Draw goodbye message if in goodbye mode
        if self.goodbye_mode:
            self._draw_goodbye_message(painter)

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

        # Show pressure band gauge on the right side when visible
        if self.show_pressure_gauge:
            self._draw_pressure_band_gauge_vertical(painter)

    def _draw_pressure_band_gauge_vertical(self, painter: QPainter):
        """Draw vertical color gauge for pressure band on the right side.

        Shows red-green-red zones vertically where:
        - Red (top): pressure above valid band (high to 1.0)
        - Green (middle): pressure inside valid band (low to high)
        - Red (bottom): pressure below valid band (0.0 to low)
        - White line: center of band

        Args:
            painter: QPainter instance
        """
        center = getattr(self.config, "pressure_band_center", 0.5)
        width = getattr(self.config, "pressure_band_width", 0.4)
        low = center - width / 2
        high = center + width / 2

        gauge_height = 300  # pixels
        gauge_width = 10  # pixels
        margin = 20

        # Position on right side
        x = self.width() - gauge_width - margin
        y = (self.height() - gauge_height) // 2

        # Calculate pixel positions (inverted: top=1.0, bottom=0.0)
        low_px = int((1.0 - low) * gauge_height)  # Distance from top
        high_px = int((1.0 - high) * gauge_height)  # Distance from top
        center_px = int((1.0 - center) * gauge_height)  # Distance from top

        # Save painter state
        painter.save()

        # Draw red zone (above band) - top part
        painter.setBrush(QColor(200, 50, 50))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(x, y, gauge_width, high_px)

        # Draw green zone (band) - middle part
        painter.setBrush(QColor(50, 200, 50))
        painter.drawRect(x, y + high_px, gauge_width, low_px - high_px)

        # Draw red zone (below band) - bottom part
        painter.setBrush(QColor(200, 50, 50))
        painter.drawRect(x, y + low_px, gauge_width, gauge_height - low_px)

        # Draw center marker (white horizontal line)
        painter.setPen(QPen(QColor(Qt.GlobalColor.white), 1))
        painter.drawLine(x, y + center_px, x + gauge_width, y + center_px)

        # Draw labels on the left (facing window center)
        font = QFont()
        font.setPointSize(7)
        painter.setFont(font)
        painter.setPen(QColor(Qt.GlobalColor.white))
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # Center value label (on the left, vertically centered with white line)
        metrics = QFontMetrics(font)
        text_h = metrics.height()
        text_w = metrics.horizontalAdvance(f"{center:.2f}")
        shift_x = text_w + 5  # space between text and gauge
        shift_y = text_h // 2

        painter.drawText(x - shift_x, y + high_px + shift_y - text_h, f"{high:.2f}")
        painter.drawText(x - shift_x, y + center_px + shift_y, f"{center:.2f}")
        painter.drawText(x - shift_x, y + low_px + shift_y + text_h, f"{low:.2f}")

        # Draw current pressure indicator line
        current_pressure = self.trail.current_pressure
        current_px = int((1.0 - current_pressure) * gauge_height)

        # Draw thick cyan line showing current position
        painter.setPen(QPen(QColor(0, 255, 255), 3))  # Cyan, 3px thick
        painter.drawLine(x - 5, y + current_px, x + gauge_width + 5, y + current_px)

        # Add numeric label near the line
        painter.setPen(QColor(0, 255, 255))
        painter.drawText(
            x + gauge_width + 10, y + current_px - 5, f"{current_pressure:.2f}"
        )

        # Restore painter state
        painter.restore()

    def _draw_goodbye_message(self, painter: QPainter):
        """Draw 'bye' message centered in the window - only if LSL is activated"""
        if not self.config.is_with_lsl:
            return

        font = QFont()
        font.setPointSize(72)
        font.setBold(True)
        text = "You should manually stop LabRecorder recording before quitting..."

        metrics = QFontMetrics(font)
        text_width = metrics.horizontalAdvance(text)
        text_height = metrics.height()

        # Reduce font size until it fits within 90% of window width
        while text_width > self.width() * 0.9 and font.pointSize() > 10:
            font.setPointSize(font.pointSize() - 2)
            metrics = QFontMetrics(font)
            text_width = metrics.horizontalAdvance(text)
            text_height = metrics.height()

        # Set font once before drawing
        painter.setFont(font)
        painter.setPen(QColor(Qt.GlobalColor.white))

        x = (self.width() - text_width) // 2
        y = (self.height() + text_height) // 2

        painter.drawText(x, y, text)

    def _toggle_recording(self):
        """Toggle recording on/off with spacebar"""
        self.status.toggle_recording()

        # Synchronize output backends explicitly
        if self.output_data:
            if self.status.is_recording:
                self.output_data.start_recording()
            else:
                self.output_data.stop_recording()

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
        print(title)
        if message:
            print(message)

        # send a marker to output backends
        if self.output_data:
            self.output_data.write_marker(title)

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

    def _adjust_pressure_band(self, attr_name: str, delta: float, update_type: str):
        """Adjust pressure band (center or width) with tablet detection check.

        Args:
            attr_name: "pressure_band_center" or "pressure_band_width"
            delta: adjustment amount (+0.02 or -0.02)
            update_type: "center" or "width" for _update_pressure_band()
        """
        # Adjust the attribute in self.config (UI state)
        current = getattr(self.config, attr_name)
        setattr(self.config, attr_name, current + delta)

        # Update derived values in self.config
        self.config._update_pressure_band(update_type)

        # IMPORTANT: Update output_config with new pressure thresholds for data output
        if self.config._output_config:
            self.config._output_config.pressure_band_low = self.config.pressure_band_low
            self.config._output_config.pressure_band_high = (
                self.config.pressure_band_high
            )

        new_value = getattr(self.config, attr_name)
        label = "Band width" if update_type == "width" else "Band center"
        self._print_status(f"{label}={new_value:.2f}", "")
        self.update()

    def _increase_band_width(self):
        self._adjust_pressure_band("pressure_band_width", 0.01, "width")

    def _decrease_band_width(self):
        self._adjust_pressure_band("pressure_band_width", -0.01, "width")

    def _increase_band_center(self):
        self._adjust_pressure_band("pressure_band_center", 0.01, "center")

    def _decrease_band_center(self):
        self._adjust_pressure_band("pressure_band_center", -0.01, "center")

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

    def _toggle_pressure_gauge_visibility(self):
        """Toggle pressure gauge HUD visibility"""
        self.show_pressure_gauge = not self.show_pressure_gauge
        state = "ON" if self.show_pressure_gauge else "OFF"
        self._print_status(f"Pressure gauge visibility: {state}")
        self.update()

    def _print_control_instructions(self):
        """Print keyboard control instructions on startup"""
        print(
            f"\n{'='*60}\nControls:\n"
            f"Press F: Toggle Fullscreen (Windowed ↔ Borderless)\n"
            f"Press C: Print Configuration\n"
            f"Press Q: Quit\n"
            f"Press SPACE: Toggle Record/Pause\n"
            f"Press ← / →: Decrease / Increase pressure-band WIDTH\n"
            f"Press ↓ / ↑: Decrease / Increase pressure-band CENTER\n"
            f"Press S: Toggle visual smoothing ON/OFF\n"
            f"Press G: Toggle pressure band gauge visibility ON/OFF\n"
            f"Note: Changes are immediate and not saved to disk\n"
            f"{'='*60}\n"
        )

    def _quit_application(self):
        """Quit application, showing bye message if LabRecorder is recording"""
        # Disable all input to suppress user interaction during shutdown
        self.setEnabled(False)

        # Only show goodbye message if LabRecorder is actively recording
        show_goodbye = self.is_labrecorder_listening()
        delay_ms = 10 if show_goodbye else 0

        if show_goodbye:
            # Enter goodbye mode to display "bye" message
            self.goodbye_mode = True
            self.update()  # Trigger paintEvent to show "bye" text

        # If in fullscreen, toggle to windowed first, then close
        # (fullscreen close is buggy on macOS, so bypass by going windowed first)
        if self.status.fullscreen_mode == 1:
            self._toggle_fullscreen()
            # Delay close to let window state settle (+ goodbye message if needed)
            QTimer.singleShot(delay_ms + 500, self.close)
        else:
            # delay close to show bye message (if LabRecorder recording)
            QTimer.singleShot(delay_ms, self.close)

    def closeEvent(self, event):
        """Handle window close - exit fullscreen before closing"""
        # If in fullscreen, explicitly return to windowed BEFORE closing
        if self.status.fullscreen_mode == 1:
            self.setWindowFlags(Qt.WindowType.Widget)
            self.showNormal()
            self.status.fullscreen_mode = 0
            # CRITICAL: Let system process state changes before accepting close
            QApplication.instance().processEvents()

        # Stop recording and log end marker before closing
        if self.status.is_recording:
            self.status.pause_recording()
            if self.output_data:
                self.output_data.write_marker("RecordingEnded")

        # Explicitly close output backends before exit
        if self.output_data:
            self.output_data.close()

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

    def tabletOrMouseEvent(self, data: dict, is_tablet: bool = False):
        """Orchestrate input event handling for tablet or mouse.

        Central handler that routes input-specific logic while delegating
        common processing to _process_input_event().

        Args:
            data: Dictionary from DataCapture.capture_*_event()
            is_tablet: True for tablet events, False for mouse events
        """

        # Common processing for both input types
        self._process_input_event(data)

        # Mouse-specific: store position for reference
        if not is_tablet:
            self.last_mouse_x = data["x"]
            self.last_mouse_y = data["y"]

    def tabletEvent(self, event: QTabletEvent):
        """Handle tablet input event"""
        if not self.data_capture:
            raise ValueError(
                "DataCapture instance is required for tablet event handling."
            )

        # Capture data
        data = self.data_capture.capture_tablet_event(event)

        # Process (detect tablet, write output, update trail/cursor/display)
        self.tabletOrMouseEvent(data, is_tablet=True)

        # Mark event as handled
        event.accept()

    def mouseMoveEvent(self, event):
        """Handle mouse movement event"""
        if not self.data_capture:
            raise ValueError(
                "DataCapture instance is required for mouse event handling."
            )

        # Capture data
        data = self.data_capture.capture_mouse_event(event)

        # Process (write output, update trail/cursor/display, store position)
        self.tabletOrMouseEvent(data, is_tablet=False)

    def mousePressEvent(self, event):
        """Print mouse click position"""
        print(
            f"Mouse click: X={event.position().x():.1f}, Y={event.position().y():.1f}"
        )
        sys.stdout.flush()

    @staticmethod
    def is_labrecorder_listening():
        """Check if LabRecorder process is running (multiplatform via psutil)"""
        try:
            import psutil

            # psutil: Works on Windows, macOS, Linux
            for proc in psutil.process_iter(["name"]):
                if "LabRecorder" in proc.info["name"]:
                    return True
            return False
        except Exception:
            return False

    def _emit_key_marker(self, event, handler_name: str | None):
        """Emit marker + console print for key events."""

        # Try to get human-readable key name, fallback to numeric code if unknown
        try:
            key_name = Qt.Key(event.key()).name
        except Exception:
            key_name = str(event.key())

        # Get text representation of the key if available (e.g., for character keys)
        text = event.text() or ""
        handler_label = handler_name or "None"

        # Create a structured marker for key events, with handler name and key info
        marker = f"KeyPress:{key_name}:{handler_label}"
        if text:
            marker = f"{marker}:{text}"

        if self.output_data:
            self.output_data.write_marker(marker)
        print(marker)
        sys.stdout.flush()

    def keyPressEvent(self, event):
        """Handle keyboard input using command dispatch"""
        handler_name = self.KEY_COMMANDS.get(event.key())

        # Call the handler method if it exists
        if handler_name:
            handler = getattr(self, handler_name, None)
            if handler:
                self._emit_key_marker(event, handler_name)
                handler()
