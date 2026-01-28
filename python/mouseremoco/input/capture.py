# DataCapture class — Event data extraction and normalization

import time
from ..geometry import is_inside as geom_is_inside


class DataCapture:
    """Centralized event data extraction and normalization.

    Captures event data once and provides normalized output for:
    - CSV persistence (OutputCSV)
    - Trail rendering (Trail)
    - Cursor updates

    Key principle: Compute expensive operations (circle detection)
    once per event, not multiple times.
    """

    def __init__(self, config):
        """Initialize with configuration for circle detection."""
        self.config = config

    def capture_tablet_event(self, event) -> dict:
        """Extract and normalize tablet event data.

        Performs circle detection once per event for efficiency (avoids redundant calculations).

        Returns:
            dict with keys:
                - x, y (float): Subpixel cursor coordinates
                - pressure (float): Stylus pressure 0.0-1.0
                - tilt_x, tilt_y (float): Stylus tilt in degrees (-60 to +60)
                - event_timestamp_ms (int): Hardware event timestamp
                - computed_timestamp_ms (int): System time when handler was called
                - is_inside (bool): Whether position is inside target tolerance band
                - input_type (str): "tablet"
        """
        x = event.position().x()
        y = event.position().y()
        pressure = event.pressure()
        tilt_x = event.xTilt()  # Range: -60 to +60 degrees
        tilt_y = event.yTilt()  # Range: -60 to +60 degrees
        # event_timestamp_ms = event.timestamp()
        event_timestamp_ms = int(event.timestamp())
        computed_timestamp_ms = int(time.time() * 1000)
        is_inside = geom_is_inside(self.config, x, y)

        return {
            "x": x,
            "y": y,
            "pressure": pressure,
            "tilt_x": tilt_x,
            "tilt_y": tilt_y,
            "event_timestamp_ms": event_timestamp_ms,
            "computed_timestamp_ms": computed_timestamp_ms,
            "is_inside": is_inside,
            "input_type": "tablet",
        }

    def capture_mouse_event(self, event) -> dict:
        """Extract and normalize mouse event data.

        Returns the same format as capture_tablet_event with pressure=0.0 and tilt=0.0 (no stylus input).
        Performs circle detection once per event for efficiency.

        Returns:
            dict with keys:
                - x, y (float): Subpixel cursor coordinates
                - pressure (float): Always 0.0 for mouse input
                - tilt_x, tilt_y (float): Always 0.0 for mouse input (no tilt sensing)
                - event_timestamp_ms (int): Hardware event timestamp
                - computed_timestamp_ms (int): System time when handler was called
                - is_inside (bool): Whether position is inside target tolerance band
                - input_type (str): "mouse"
        """
        x = event.position().x()
        y = event.position().y()
        pressure = 0.0
        tilt_x = 0.0  # Mouse has no tilt sensing
        tilt_y = 0.0  # Mouse has no tilt sensing
        # event_timestamp_ms = event.timestamp()
        event_timestamp_ms = int(event.timestamp())
        computed_timestamp_ms = int(time.time() * 1000)
        is_inside = geom_is_inside(self.config, x, y)

        return {
            "x": x,
            "y": y,
            "pressure": pressure,
            "tilt_x": tilt_x,
            "tilt_y": tilt_y,
            "event_timestamp_ms": event_timestamp_ms,
            "computed_timestamp_ms": computed_timestamp_ms,
            "is_inside": is_inside,
            "input_type": "mouse",
        }

    def _is_point_inside_circle(self, x: float, y: float) -> bool:
        """Legacy wrapper kept for compatibility; delegates to geometry.is_inside."""
        return geom_is_inside(self.config, x, y)
