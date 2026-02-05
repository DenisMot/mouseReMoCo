# OutputTablet class -- Manage output of tablet/mouse to CSV files or to LSL stream

# Output Backend Architecture — With subpixel coordinate support

from abc import ABC, abstractmethod
import csv
from datetime import datetime
from ..config import OutputConfiguration
from typing import Any


# ===== Shared Data Schema =====
# Single source of truth for all output formats (CSV, LSL, etc.)
# Each field is self-contained with all its metadata, similar to LSL channel definitions
DATA_SCHEMA = {
    "fields": [
        {
            "name": "event_timestamp",
            "type": "timestamp",
            "unit": "milliseconds",
            "rounding": 0,
        },
        {
            "name": "unix_timestamp",
            "type": "timestamp",
            "unit": "milliseconds",
            "rounding": 0,
        },
        {
            "name": "mouseX",
            "type": "PositionX",
            "unit": "pixels",
            "rounding": 2,
        },
        {
            "name": "mouseY",
            "type": "PositionY",
            "unit": "pixels",
            "rounding": 2,
        },
        {
            "name": "mouseInTarget",
            "type": "flag",
            "unit": "boolean",
            "rounding": 0,
        },
        {
            "name": "pressure",
            "type": "pressure",
            "unit": "normalized",
            "rounding": 4,
        },
        {
            "name": "tiltX",
            "type": "tilt",
            "unit": "degrees",
            "rounding": 0,
        },
        {
            "name": "tiltY",
            "type": "tilt",
            "unit": "degrees",
            "rounding": 0,
        },
    ]
}


class OutputBackend(ABC):
    """Abstract base class for output targets (CSV, LSL, etc.)"""

    def __init__(self, config, output_config=None):
        """Store config and output_config for shared methods

        Args:
            config: Configuration object
            output_config: Optional OutputConfiguration for coordinate transformation
        """
        self.config = config
        self.output_config = output_config

    def _config_to_string(self) -> str:
        """Convert config to semicolon-separated string for metadata headers

        Uses output_config's modified copy (with coordinate transformation info)
        if available, otherwise uses self.config.
        """
        # Use output_config's modified copy if available for consistent metadata
        config_to_serialize = (
            self.output_config.config if self.output_config else self.config
        )
        config_dict = {}

        for key, value in config_to_serialize.__dict__.items():
            if key.startswith("_"):
                continue

            if isinstance(value, bool):
                config_dict[key] = str(value).lower()
            elif isinstance(value, float):
                config_dict[key] = round(value, 2)
            else:
                config_dict[key] = value

        return ";".join([f"{k} {v}" for k, v in config_dict.items()])

    @staticmethod
    def format_data(config):
        """Format data identically for all backends using DATA_SCHEMA

        Args:
            config: Dictionary or object with keys/attributes:
                - event_timestamp_ms: Hardware event timestamp from Qt event
                - call_time_ms: System time when event handler was called
                - x: Mouse X coordinate (pixels, with subpixel precision)
                - y: Mouse Y coordinate (pixels, with subpixel precision)
                - is_inside: Whether cursor is inside target region
                - pressure: Pen pressure (0.0-1.0 normalized), optional default 0.0
                - tilt_x: Tilt angle X (degrees), optional default 0.0
                - tilt_y: Tilt angle Y (degrees), optional default 0.0
                - output_config: Optional for coordinate transformation

        Returns:
            List of formatted values in DATA_SCHEMA field order
        """
        # Extract values from config
        event_timestamp_ms = (
            config.get("event_timestamp_ms")
            if isinstance(config, dict)
            else getattr(config, "event_timestamp_ms")
        )
        call_time_ms = (
            config.get("call_time_ms")
            if isinstance(config, dict)
            else getattr(config, "call_time_ms")
        )
        x = config.get("x") if isinstance(config, dict) else getattr(config, "x")
        y = config.get("y") if isinstance(config, dict) else getattr(config, "y")
        is_inside = (
            config.get("is_inside")
            if isinstance(config, dict)
            else getattr(config, "is_inside")
        )
        pressure = (
            config.get("pressure", 0.0)
            if isinstance(config, dict)
            else getattr(config, "pressure", 0.0)
        )
        tilt_x = (
            config.get("tilt_x", 0.0)
            if isinstance(config, dict)
            else getattr(config, "tilt_x", 0.0)
        )
        tilt_y = (
            config.get("tilt_y", 0.0)
            if isinstance(config, dict)
            else getattr(config, "tilt_y", 0.0)
        )
        output_config = (
            config.get("output_config")
            if isinstance(config, dict)
            else getattr(config, "output_config", None)
        )

        # Transform coordinates if output_config available
        if output_config:
            x, y = output_config.transform_coordinates(x, y)

        # Build raw values directly in DATA_SCHEMA field order
        raw_values = [
            event_timestamp_ms,  # event_timestamp
            call_time_ms,  # unix_timestamp
            x,  # mouseX
            y,  # mouseY
            1 if is_inside else 0,  # mouseInTarget
            pressure,  # pressure
            tilt_x,  # tiltX
            tilt_y,  # tiltY
        ]

        # Apply rounding per field using DATA_SCHEMA
        formatted = []
        for value, field in zip(raw_values, DATA_SCHEMA["fields"]):
            decimals = field["rounding"]
            if decimals == 0:
                formatted.append(value)
            else:
                formatted.append(round(value, decimals))

        return formatted

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
        """Write position data point with subpixel precision.

        Formats data using shared format_data() and delegates to _push_sample()
        for backend-specific output (CSV or LSL).

        Args:
            event_timestamp_ms: Hardware event timestamp from Qt event
            call_time_ms: System time when event handler was called
            x: Mouse X coordinate (pixels, with subpixel precision)
            y: Mouse Y coordinate (pixels, with subpixel precision)
            is_inside: Whether cursor is inside target region
            pressure: Pen pressure (0.0-1.0 normalized)
            tilt_x: Tilt angle X (degrees)
            tilt_y: Tilt angle Y (degrees)
        """
        try:
            data_config = {
                "event_timestamp_ms": event_timestamp_ms,
                "call_time_ms": call_time_ms,
                "x": x,
                "y": y,
                "is_inside": is_inside,
                "pressure": pressure,
                "tilt_x": tilt_x,
                "tilt_y": tilt_y,
                "output_config": self.output_config,
            }
            formatted = self.format_data(data_config)
            self._push_sample(formatted)
        except Exception as e:
            print(f"ERROR writing data: {e}")

    @abstractmethod
    def _push_sample(self, formatted: list):
        """Push formatted sample to backend (CSV row or LSL stream)

        Args:
            formatted: List of formatted values in DATA_SCHEMA order
        """
        pass

    @abstractmethod
    def write_marker(self, marker_text: str):
        """Write event marker"""
        pass

    @abstractmethod
    def close(self):
        """Close backend resources"""
        pass


class CSVBackend(OutputBackend):
    """CSV file output backend (data.csv, marker.csv) with subpixel support"""

    def __init__(
        self,
        config,
        output_config=None,
        data_filename="data.csv",
        marker_filename="marker.csv",
        creation_timestamp=None,
    ) -> None:
        super().__init__(config, output_config)
        if creation_timestamp is None:
            raise ValueError(
                "creation_timestamp is required to ensure CSV and LSL consistency"
            )
        # Use output_config's modified copy if available, otherwise use original
        self.config = output_config.config if output_config else config
        self.output_config: OutputConfiguration | None = output_config
        self.data_filename = data_filename
        self.marker_filename = marker_filename
        self.creation_timestamp = creation_timestamp

        self.data_file = None
        self.marker_file = None
        self.data_writer = None
        self.marker_writer = None
        self._closed = False

        self._init_files()

    def _init_files(self):
        """Create and write headers to both CSV files"""
        # Create data.csv
        self.data_file = open(self.data_filename, "w", newline="")
        self.data_writer = csv.writer(self.data_file)

        # Write configuration header (line 1)
        config_line = self._config_to_string()
        self.data_file.write(config_line + "\n")

        # Write creation timestamp as ISO8601 with timezone (line 2)
        timestamp_str = self.creation_timestamp.astimezone().isoformat()
        self.data_file.write(timestamp_str + "\n")
        self.data_file.write("\n")

        # Write column headers using shared DATA_SCHEMA
        headers = [field["name"] for field in DATA_SCHEMA["fields"]]
        self.data_writer.writerow(headers)

        self.data_file.flush()

        # Create marker.csv
        self.marker_file = open(self.marker_filename, "w", newline="")
        self.marker_writer = csv.writer(self.marker_file)

        # Write same headers to marker file
        self.marker_file.write(config_line + "\n")
        self.marker_file.write(timestamp_str + "\n")
        self.marker_file.write("\n")

        # Write marker column headers
        self.marker_writer.writerow(["timestamp", "unix_timestamp", "marker"])
        self.marker_file.flush()

        print(f"✓ CSV Backend: Created {self.data_filename} and {self.marker_filename}")

    def _push_sample(self, formatted: list):
        """Write formatted sample to CSV"""
        if not self.data_writer:
            return
        self.data_writer.writerow(formatted)
        if self.data_file:
            self.data_file.flush()

    def write_marker(self, marker_text: str):
        """Write event marker to CSV"""
        try:
            if not self.marker_writer:
                return

            current_time = datetime.now()
            # UNIX epoch time in milliseconds for automated sync
            unix_timestamp_ms = int(current_time.timestamp() * 1000)
            timestamp_str = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            self.marker_writer.writerow(
                [
                    timestamp_str,  # Human-readable ISO8601 for manual log inspection
                    unix_timestamp_ms,  # UNIX epoch ms for automated sync
                    marker_text,
                ]
            )
            if self.marker_file:
                self.marker_file.flush()
        except Exception as e:
            print(f"ERROR writing marker to {self.marker_filename}: {e}")

    def close(self):
        """Close CSV files (idempotent)."""
        if self._closed:
            return
        self._closed = True

        try:
            if self.data_file:
                try:
                    self.data_file.close()
                finally:
                    self.data_file = None
                print(f"✓ Closed {self.data_filename}")
            if self.marker_file:
                try:
                    self.marker_file.close()
                finally:
                    self.marker_file = None
                print(f"✓ Closed {self.marker_filename}")
        except Exception as e:
            print(f"ERROR closing CSV files: {e}")


class LSLBackend(OutputBackend):
    """LSL (Lab Streaming Layer) output backend with subpixel support"""

    def __init__(self, config, output_config=None, creation_timestamp=None) -> None:
        if creation_timestamp is None:
            raise ValueError(
                "creation_timestamp is required to ensure CSV and LSL consistency"
            )
        super().__init__(config, output_config)
        self.output_config = output_config
        self.creation_timestamp = creation_timestamp
        self.data_outlet = None
        self.marker_outlet = None
        self.numeric_marker_outlet = None
        self.lsl: Any = None
        self._closed = False

        try:
            # Local import to handle missing dependency
            import pylsl as lsl_module  # type: ignore

            self.lsl = lsl_module
            self._init_lsl()
            print("✓ LSL Backend: Initialized successfully")
        except ImportError:
            print("⚠ LSL library not available - LSL backend disabled")
            self.lsl = None

    def _add_lsl_metadata(self, stream_info, config_str: str, timestamp_str: str):
        """Add configuration and timestamp metadata to LSL stream info

        Args:
            stream_info: LSL StreamInfo object
            config_str: Configuration string to add
            timestamp_str: ISO8601 timestamp string to add

        Returns:
            The root descriptor element for further modifications
        """
        root = stream_info.desc()
        root.append_child_value("configuration_str", config_str)
        root.append_child_value("timestamp_str", timestamp_str)
        return root

    def _init_lsl(self):
        """Initialize LSL streams with metadata matching CSV format"""
        if not self.lsl:
            return

        # Data stream with channel descriptions from shared DATA_SCHEMA
        data_info = self.lsl.StreamInfo(
            name="MouseData",
            type="MoCap",
            channel_count=len(DATA_SCHEMA["fields"]),
            nominal_srate=self.lsl.IRREGULAR_RATE,
            channel_format=self.lsl.cf_double64,  # for timestamp accuracy
            source_id="mouseReMoCo",
        )

        # Add metadata to stream description (matching CSV header lines 1-2)
        config_str = self._config_to_string()
        timestamp_str = self.creation_timestamp.astimezone().isoformat()
        root = self._add_lsl_metadata(data_info, config_str, timestamp_str)

        # Add channel descriptions from shared DATA_SCHEMA
        chns = root.append_child("channels")
        for field in DATA_SCHEMA["fields"]:
            chns.append_child("channel").append_child_value(
                "label", field["name"]
            ).append_child_value("type", field["type"]).append_child_value(
                "unit", field["unit"]
            )
        self.data_outlet = self.lsl.StreamOutlet(data_info)

        # Marker stream
        marker_info = self.lsl.StreamInfo(
            name="MouseMarkers",
            type="Markers",
            channel_count=1,
            nominal_srate=self.lsl.IRREGULAR_RATE,
            channel_format=self.lsl.cf_string,
            source_id="mouseReMoCo_markers",
        )

        # Add metadata to marker stream
        self._add_lsl_metadata(marker_info, config_str, timestamp_str)

        self.marker_outlet = self.lsl.StreamOutlet(marker_info)

        # Numeric marker stream (for sync)
        numeric_info = self.lsl.StreamInfo(
            name="MouseMarkersNumeric",
            type="Markers",
            channel_count=1,
            nominal_srate=self.lsl.IRREGULAR_RATE,
            channel_format=self.lsl.cf_int32,
            source_id="mouseReMoCo_markers_numeric",
        )

        # Add metadata to numeric marker stream
        self._add_lsl_metadata(numeric_info, config_str, timestamp_str)

        self.numeric_marker_outlet = self.lsl.StreamOutlet(numeric_info)

    def _push_sample(self, formatted: list):
        """Push formatted sample to LSL stream"""
        if not self.lsl or not self.data_outlet:
            return
        # Convert to float64 for LSL (cf_double64 format ensures exact precision)
        sample = [float(v) for v in formatted]

        self.data_outlet.push_sample(sample)

    def write_marker(self, marker_text: str):
        """Push event marker to LSL"""
        if not self.lsl or not self.marker_outlet:
            return

        try:
            self.marker_outlet.push_sample([marker_text])
        except Exception as e:
            print(f"ERROR pushing marker to LSL: {e}")

    def close(self):
        """Close LSL outlets (safe even if labRecorder is recording)

        Gracefully disconnects from labRecorder. If labRecorder is actively reading,
        it will detect the disconnection and continue recording with what it received.
        """
        if self._closed:
            return
        self._closed = True

        if not self.lsl:
            return

        try:
            # Gracefully close outlets - labRecorder handles disconnection
            if self.data_outlet:
                self.data_outlet = None
            if self.marker_outlet:
                self.marker_outlet = None
            if self.numeric_marker_outlet:
                self.numeric_marker_outlet = None
            print("✓ Closed LSL Backend")
        except Exception:
            # Ignore errors
            pass
