# OutputTablet unified output manager

from datetime import datetime
from .backends import CSVBackend, LSLBackend


class OutputTablet:
    """Unified output manager with pluggable backends (CSV, LSL) - Subpixel support"""

    def __init__(
        self,
        config,
        app_status,
        output_config=None,
        enable_csv: bool = True,
        enable_lsl: bool = False,
    ):
        """
        Initialize OutputTablet with desired backends.

        Args:
            config: Configuration object with screen and task parameters
            app_status: AppStatus instance for recording state tracking
            output_config: OutputConfiguration instance (default: None)
            enable_csv: Enable CSV file output with subpixel precision (default: True)
            enable_lsl: Enable LSL streaming output (default: False)
        """
        self.config = config
        self.app_status = app_status  # For state tracking if needed
        self.backends = []

        # Create single timestamp for all backends to ensure consistency
        creation_timestamp = datetime.now()

        if enable_csv:
            self.backends.append(
                CSVBackend(config, output_config, creation_timestamp=creation_timestamp)
            )

        if enable_lsl:
            lsl_backend = LSLBackend(
                config,
                self.config._output_config,
                creation_timestamp=creation_timestamp,
            )
            if lsl_backend.lsl:
                self.backends.append(lsl_backend)
            else:
                print("⚠ LSL Backend not added due to initialization failure")

        if not self.backends:
            raise ValueError("At least one backend must be enabled (CSV or LSL)")

        self._is_recording = False

    def start_recording(self):
        """Start recording: mark exact moment all backends begin recording.

        Call this BEFORE any data collection starts to ensure CSV and LSL
        backends timestamp their initialization identically.
        """
        if self._is_recording:
            print("⚠ Recording already started")
            return

        self._is_recording = True

    def stop_recording(self):
        """Stop recording: mark exact moment all backends stop recording.

        Call this AFTER data collection ends to ensure both backends
        captured the same event range.
        """
        if not self._is_recording:
            print("⚠ Recording not active")
            return

        self._is_recording = False

    def is_recording(self) -> bool:
        """Check if recording is active"""
        return self._is_recording

    def write_data(
        self,
        event_timestamp_ms: int,
        call_time_ms: int,
        x: float,
        y: float,
        is_inside: bool,
        pressure: float = 0.0,
        tilt_x: float = 0.0,
        tilt_y: float = 0.0,
    ):
        """Write position data with subpixel precision to all active backends"""
        # Only write if explicitly recording via start_recording()
        if not self._is_recording:
            return

        for backend in self.backends:
            backend.write_data(
                event_timestamp_ms,
                call_time_ms,
                x,
                y,
                is_inside,
                pressure,
                tilt_x,
                tilt_y,
            )

    def write_marker(self, marker_text: str):
        """Write event marker to all active backends"""
        for backend in self.backends:
            backend.write_marker(marker_text)

    def close(self):
        """Close all backends gracefully"""
        for backend in self.backends:
            try:
                backend.close()
            except Exception:
                pass
        # Clear backends to prevent double-closing from __del__ or later calls
        self.backends = []

    def __del__(self):
        """Ensure backends are closed when object is garbage collected"""
        self.close()
