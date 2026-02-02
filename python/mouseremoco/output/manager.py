# OutputTablet unified output manager

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

        if enable_csv:
            self.backends.append(CSVBackend(config, output_config))

        if enable_lsl:
            lsl_backend = LSLBackend(config)
            if lsl_backend.lsl:  # Only add if LSL initialized successfully
                self.backends.append(lsl_backend)
            else:
                print("⚠ LSL Backend not added due to initialization failure")

        if not self.backends:
            raise ValueError("At least one backend must be enabled (CSV or LSL)")

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
        # Only write if recording
        if not self.app_status.is_recording:
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
