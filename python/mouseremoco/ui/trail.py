# Trail Class — Comet trail rendering and management

from collections import deque
import time

from PyQt6.QtGui import QColor, QPainter, QPen


class Trail:
    """
    Manages comet trail rendering.

    Modes:
    - path_length - fade based on cumulative distance traveled

    Trail data structure: deque of (x, y, timestamp, cumulative_distance, pressure)
    Each point remembers the pressure when it was recorded.
    """

    # Single source of truth for all valid trail modes
    VALID_MODES = ["path_length"]

    def __init__(self, config, app_status=None):
        """Initialize Trail with configuration reference and app status for tablet detection"""
        self.config = config
        self.app_status = app_status  # Reference to app status for tablet detection
        self.trail = deque()  # (x, y, timestamp, cumulative_path_distance, pressure)
        self.current_pressure = 0.0
        self.current_tilt_x = 0.0
        self.current_tilt_y = 0.0
        self.cumulative_distance = 0.0
        self._current_speed = 0.0
        self._last_x = None
        self._last_y = None
        self.output_data = None
        # Set by MainWindow after OutputData is created

    def add_point(self, x: float, y: float, timestamp_ms: int, call_time_ms: int):
        """Add point with subpixel coordinates and pressure tracking.

        Updates cumulative distance and current speed based on Euclidean movement.

        Args:
            x, y: Subpixel cursor coordinates (float)
            timestamp_ms: Hardware event timestamp from Qt event.timestamp()
            call_time_ms: System time when event handler was called (kept for API consistency)
        """

        if self._last_x is not None and self._last_y is not None:
            dx = x - self._last_x
            dy = y - self._last_y
            distance = (dx**2 + dy**2) ** 0.5
            self._current_speed = distance
            self.cumulative_distance += distance
        else:
            self._current_speed = 0.0

        # Add point with timestamp, cumulative distance, and pressure
        self.trail.append(
            (x, y, time.time(), self.cumulative_distance, self.current_pressure)
        )

        # Update last position
        self._last_x = x
        self._last_y = y

        # Prune based on current mode
        self.prune()

    def prune(self):
        """Remove old points from trail based on path length"""
        # Path-distance-based pruning
        threshold = self.get_length()
        self.trail = deque(
            (x, y, t, d, p)
            for x, y, t, d, p in self.trail
            if self.cumulative_distance - d <= threshold
        )

    def get_length(self) -> float:
        """Compute trail length based on path_length mode"""
        base = self.config.get_trail_length()  # 10×cursor_radius or explicit value
        return base  # Uses cumulative distance, not Euclidean

    def _get_color_for_position(self, x: int, y: int) -> tuple[int, int, int]:
        """Determine trail color based on position relative to target"""
        dx = self.config.center_x - x
        dy = self.config.center_y - y
        distance = (dx * dx + dy * dy) ** 0.5

        is_inside = self.config.internal_limit < distance < self.config.external_limit

        # Mouse trails use blue, tablet trails use red
        # Use config colors based on position
        if is_inside:
            return self.config.cursor_color_record  # Inside target
        else:
            return self.config.cursor_color_record_outside  # Outside target

    def _draw_segment(
        self,
        painter: QPainter,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        pressure: float,
        opacity: float,
    ) -> bool:
        """Draw a single trail segment with conditional styling based on tablet detection.

        No tablet detected: 3px blue trail (fixed thickness, blue color)
        Tablet detected: Pressure-scaled red trail (thickness varies with pressure, position-based color)

        Both use opacity fading based on trail mode.

        Args:
            painter: QPainter instance for drawing
            x1, y1, x2, y2: Segment endpoints (int coordinates)
            pressure: Stylus pressure (0.0-1.0) for thickness scaling
            opacity: Alpha value (0.0-1.0) for fade effect

        Returns:
            bool: True if segment was drawn, False if skipped (thickness < 1px)
        """
        # Determine thickness and base color based on tablet detection
        if self.app_status and not self.app_status.tablet_detected:
            # NO TABLET → 3px BLUE trail (fixed thickness, blue color)
            thickness = 3
            base_color = (0, 0, 255)  # Blue RGB
        else:
            # TABLET DETECTED → Pressure-scaled RED trail (pressure-dependent thickness, position-based color)
            thickness = 2 * self.config.cursor_radius * pressure
            base_color = self._get_color_for_position(
                x2, y2
            )  # Red inside/dark red outside

        # Skip if thickness is too thin
        if thickness < 1:
            return False

        # Apply opacity fading to the color (same for both modes)
        color = QColor(*base_color)
        color.setAlpha(int(255 * opacity))  # Fade out as trail ages

        # Draw the segment
        painter.setPen(QPen(color, thickness))
        painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        return True

    def draw(self, painter: QPainter, center_x: int, center_y: int):
        """Draw the entire trail with path-distance-based opacity fade"""
        if len(self.trail) < 2:
            return

        trail_list = list(self.trail)
        self._draw_path_distance_based(painter, trail_list)

    def _draw_path_distance_based(self, painter: QPainter, trail_list: list):
        """Draw trail with path-distance-based opacity fade"""
        threshold = self.get_length()
        for i in range(len(trail_list) - 1):
            x1, y1, _, d1, pressure1 = trail_list[i]
            x2, y2, _, d2, pressure2 = trail_list[i + 1]

            # Path distance from newest point
            path_distance = self.cumulative_distance - d2
            opacity = max(0, 1 - path_distance / threshold)

            self._draw_segment(painter, x1, y1, x2, y2, pressure2, opacity)

    def clear(self):
        """Clear all trail points and reset distance tracking"""
        self.trail.clear()
        self.cumulative_distance = 0.0
        self._current_speed = 0.0
        self._last_x = None
        self._last_y = None

    def set_mode(self, mode_name: str):
        """Switch to a new trail mode and reset trail state.

        Validates mode name against VALID_MODES and clears trail points
        and cumulative distance tracking when switching modes.

        Args:
            mode_name: Trail mode name (must be in Trail.VALID_MODES)
        """
