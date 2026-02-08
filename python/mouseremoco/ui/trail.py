# Trail Class — Comet trail rendering and management

from collections import deque
import time

from PyQt6.QtGui import QColor, QPainter, QPen
import math
from ..geometry import is_inside as geom_is_inside


class Trail:
    """
    Manages comet trail rendering.

    Modes:
    - path_length - fade based on cumulative distance traveled

    Trail data structure: deque of (x, y, timestamp, cumulative_distance, pressure,
    tablet_detected)
    Each point remembers the pressure when it was recorded.
    """

    # Single source of truth for all valid trail modes
    VALID_MODES = ["path_length", "None"]

    def __init__(self, config, app_status=None):
        """Initialize Trail with configuration reference and app status"""
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
        self.visual_smoothing = True
        self.set_mode(self.config.trail_mode)  # Initialize mode and related settings

    def set_mode(self, mode_name: str):
        """Switch to a new trail mode and reset trail state.

        Validates mode name against VALID_MODES and clears trail points
        and cumulative distance tracking when switching modes.

        Args:
            mode_name: Trail mode name (must be in Trail.VALID_MODES)
        """
        if mode_name not in self.VALID_MODES:
            raise ValueError(f"Invalid trail mode: {mode_name}")

        if mode_name == "None":
            self.config.trail_mode = "None"
            self.config.trail_length = 0.0

        elif mode_name == "path_length":
            self.config.trail_mode = "path_length"

            # Trail length is derived from cursor radius if not explicitly set
            if self.config.trail_length == 0 or self.config.trail_length is None:
                one_lap_length = int(2 * 3.14159 * self.config.internal_radius)
                self.config.trail_length = one_lap_length

        # In all cases, clear trail and reset distance tracking
        self.clear()

    def add_point(self, x: float, y: float, timestamp_ms: int, call_time_ms: int):
        """Add point with subpixel coordinates and pressure tracking.

        Updates cumulative distance and current speed based on Euclidean movement.

        Args:
            x, y: Subpixel cursor coordinates (float)
            timestamp_ms: Timestamp from Qt event.timestamp (since app start)
            call_time_ms: Timestamp when event handler was called (since 01 Jan 1970)
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
        tablet_detected = self.app_status and self.app_status.tablet_detected
        self.trail.append(
            (
                x,
                y,
                time.time(),
                self.cumulative_distance,
                self.current_pressure,
                tablet_detected,
            )
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
            (x, y, t, d, p, tablet)
            for x, y, t, d, p, tablet in self.trail
            if self.cumulative_distance - d <= threshold
        )

    def get_length(self) -> float:
        """Compute trail length based on path_length mode"""
        base = self.config.get_trail_length()  # 10×cursor_radius or explicit value
        return base  # Uses cumulative distance, not Euclidean

    def _get_color_for_position(self, x: int, y: int) -> tuple[int, int, int]:
        """Determine trail color based on position relative to target"""
        is_inside = geom_is_inside(self.config, x, y)

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
        tablet_detected: bool,
    ) -> bool:
        """Draw a single trail segment.

        No tablet detected: 3px blue trail (fixed thickness, blue color)
        Tablet detected: Pressure-dependent thickness, position-based color

        Both use opacity fading based on trail mode.

        Args:
            painter: QPainter instance for drawing
            x1, y1, x2, y2: Segment endpoints (int coordinates)
            pressure: Stylus pressure (0.0-1.0) for thickness scaling
            opacity: Alpha value (0.0-1.0) for fade effect
            tablet_detected: Whether a tablet is detected (bool)
        Returns:
            bool: True if segment was drawn, False if skipped (thickness < 1px)
        """
        # Determine thickness and base color based on tablet detection
        if not tablet_detected:
            # NO TABLET → 3px BLUE trail (fixed thickness, blue color)
            thickness = 3
            base_color = (0, 0, 255)  # Blue RGB
        else:
            # TABLET DETECTED → Pressure-scaled RED trail
            # (pressure-dependent thickness, position-based color)
            thickness = 2 * self.config.cursor_radius * pressure
            # Determine color based on pressure band: green when within band,
            # else position-based red
            center = getattr(self.config, "pressure_band_center", 0.5)
            width = getattr(self.config, "pressure_band_width", 0.4)
            low = max(0.0, center - width / 2)
            high = min(1.0, center + width / 2)

            if low <= pressure <= high:
                # Determine if point is inside target to darken color when outside
                is_inside = geom_is_inside(self.config, x2, y2)

                if is_inside:
                    base_color = (
                        0,
                        200,
                        0,
                    )  # bright green when inside band and inside target
                else:
                    base_color = (
                        0,
                        100,
                        0,
                    )  # darker green when inside band but outside target
            else:
                base_color = self._get_color_for_position(x2, y2)

        # Skip if thickness is too thin
        if thickness < 0.1:
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

        # Visual-only smoothing using a small Gaussian kernel
        n = len(trail_list)
        if n < 2:
            return

        # If visual smoothing is disabled, draw using raw stored points
        if not self.visual_smoothing:
            threshold = self.get_length()
            for i in range(n - 1):
                x1, y1, _, d1, pressure1, tablet_detected1 = trail_list[i]
                x2, y2, _, d2, pressure2, tablet_detected2 = trail_list[i + 1]

                path_distance = self.cumulative_distance - d2
                opacity = max(0, 1 - path_distance / threshold)

                self._draw_segment(
                    painter, x1, y1, x2, y2, pressure2, opacity, tablet_detected2
                )
            return

        # Kernel parameters (tunable)
        k = 2  # radius -> window size = 2*k+1 (e.g., 5)
        sigma = 1.0
        kernel = [math.exp(-0.5 * (i / sigma) ** 2) for i in range(-k, k + 1)]
        k_sum = sum(kernel)
        kernel = [w / k_sum for w in kernel]

        # Prepare smoothed coordinate list (keep other fields unchanged)
        smoothed = []
        for i in range(n):
            acc_x = 0.0
            acc_y = 0.0
            for j, w in enumerate(kernel):
                idx = i + (j - k)
                if idx < 0:
                    idx = 0
                if idx >= n:
                    idx = n - 1
                xj, yj, tj, dj, pj, tabletj = trail_list[idx]
                acc_x += w * xj
                acc_y += w * yj
            _, _, tj, dj, pj, tablet = trail_list[i]
            smoothed.append((acc_x, acc_y, tj, dj, pj, tablet))

        # Draw using smoothed coordinates but original pressures for styling
        for i in range(n - 1):
            x1, y1, _, d1, pressure1, tablet_detected1 = smoothed[i]
            x2, y2, _, d2, pressure2, tablet_detected2 = smoothed[i + 1]

            path_distance = self.cumulative_distance - d2
            opacity = max(0, 1 - path_distance / threshold)

            self._draw_segment(
                painter, x1, y1, x2, y2, pressure2, opacity, tablet_detected2
            )

    def clear(self):
        """Clear all trail points and reset distance tracking"""
        self.trail.clear()
        self.cumulative_distance = 0.0
        self._current_speed = 0.0
        self._last_x = None
        self._last_y = None
