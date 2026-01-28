# OutputTablet class -- Manage output of tablet/mouse to CSV files or to LSL stream

# Output Backend Architecture — With subpixel coordinate support

from abc import ABC, abstractmethod
import csv
from datetime import datetime


class OutputBackend(ABC):
    """Abstract base class for output targets (CSV, LSL, etc.)"""

    @abstractmethod
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

        Args:
            event_timestamp_ms: Hardware event timestamp from Qt event
            call_time_ms: System time when event handler was called
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
    ):
        # Use output_config's modified copy if available, otherwise use original
        self.config = output_config.config if output_config else config
        self.output_config = output_config
        self.data_filename = data_filename
        self.marker_filename = marker_filename
        self.creation_timestamp = datetime.now()

        self.data_file = None
        self.marker_file = None
        self.data_writer = None
        self.marker_writer = None

        self._init_files()

    def _init_files(self):
        """Create and write headers to both CSV files"""
        # Create data.csv
        self.data_file = open(self.data_filename, "w", newline="")
        self.data_writer = csv.writer(self.data_file)

        # Write configuration header
        config_line = self._config_to_string()
        self.data_file.write(config_line + "\n")

        # Write creation timestamp as ISO8601 with timezone (for manual log inspection)
        timestamp_str = self.creation_timestamp.astimezone().isoformat()

        self.data_file.write(timestamp_str + "\n")
        self.data_file.write("\n")

        # Write column headers (updated to reflect subpixel precision)
        self.data_writer.writerow(
            [
                "event_timestamp",  # from event.timestamp()
                "call_time",  # from time.time() at handler call
                "mouseX",
                "mouseY",
                "mouseInTarget",
                "pressure",
                "tiltX",
                "tiltY",
            ]
        )
        self.data_file.flush()

        # Create marker.csv
        self.marker_file = open(self.marker_filename, "w", newline="")
        self.marker_writer = csv.writer(self.marker_file)

        # Write same headers to marker file
        self.marker_file.write(config_line + "\n")
        self.marker_file.write(timestamp_str + "\n")
        self.marker_file.write("\n")

        # Write marker column headers
        self.marker_writer.writerow(["timestamp", "milliseconds", "marker"])
        self.marker_file.flush()

        print(f"✓ CSV Backend: Created {self.data_filename} and {self.marker_filename}")

    def _config_to_string(self) -> str:
        """Convert all configuration attributes to semicolon-separated string for CSV header"""
        config_dict = {}

        # Write all config attributes
        for key, value in self.config.__dict__.items():
            # Skip private/protected attributes
            if key.startswith("_"):
                continue

            # Format the value appropriately
            if isinstance(value, bool):
                config_dict[key] = str(value).lower()
            elif isinstance(value, float):
                config_dict[key] = round(value, 2)
            else:
                config_dict[key] = value

        return ";".join([f"{k} {v}" for k, v in config_dict.items()])

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
        """Write event data to CSV with coordinate transformation"""
        try:
            # Transform coordinates if output_config is available
            if self.output_config:
                x, y = self.output_config.transform_coordinates(x, y)

            # Format values for CSV output
            # Wacom 0–8191 mapped to 0.0–1.0 => 4 decimal places
            pressure = round(pressure, 4)
            # Wacom tilt -60° to +60° with 1° precision => int
            tilt_x = int(tilt_x)
            tilt_y = int(tilt_y)
            # Subpixel precision: 2 decimal places is overkill
            x = round(x, 2)
            y = round(y, 2)

            self.data_writer.writerow(
                [
                    event_timestamp_ms,
                    call_time_ms,
                    x,
                    y,
                    1 if is_inside else 0,
                    pressure,
                    tilt_x,
                    tilt_y,
                ]
            )
            self.data_file.flush()
        except Exception as e:
            print(f"ERROR writing data to {self.data_filename}: {e}")

    def write_marker(self, marker_text: str):
        """Write event marker to CSV"""
        try:
            current_time = datetime.now()
            # millisecond accuracy for humans and machines
            timestamp_ms = int(current_time.timestamp() * 1000)
            timestamp_str = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            self.marker_writer.writerow(
                [
                    timestamp_str,  # Human-readable for manual log inspection
                    timestamp_ms,  # Epoch ms for automated sync
                    marker_text,
                ]
            )
            self.marker_file.flush()
        except Exception as e:
            print(f"ERROR writing marker to {self.marker_filename}: {e}")

    def close(self):
        """Close CSV files (idempotent)."""
        if getattr(self, "_closed", False):
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

    def __init__(self, config):
        self.config = config
        self.data_outlet = None
        self.marker_outlet = None
        self.numeric_marker_outlet = None

        try:
            import lsl as lsl_module

            self.lsl = lsl_module
            self._init_lsl()
            print("✓ LSL Backend: Initialized successfully")
        except ImportError:
            print("⚠ LSL library not available - LSL backend disabled")
            self.lsl = None

    def _init_lsl(self):
        """Initialize LSL streams for data and markers"""
        if not self.lsl:
            return

        # Data stream (float32 supports subpixel precision)
        data_info = self.lsl.StreamInfo(
            name="MouseData",
            type="MoCap",
            channel_count=3,
            nominal_srate=self.lsl.IRREGULAR_RATE,
            channel_format=self.lsl.cf_float32,
            source_id="mouseReMoCo",
        )

        # Add channel descriptions
        chns = data_info.desc().append_child("channels")
        labels = ["mouseX", "mouseY", "mouseInTarget"]
        types = ["PositionX", "PositionY", "flag"]
        units = ["pixels", "pixels", "boolean"]

        for label, type_, unit in zip(labels, types, units):
            chns.append_child("channel").append_child_value(
                "label", label
            ).append_child_value("type", type_).append_child_value("unit", unit)

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
        self.numeric_marker_outlet = self.lsl.StreamOutlet(numeric_info)

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
        """Push position data to LSL with full subpixel precision"""
        if not self.lsl or not self.data_outlet:
            return

        try:
            # LSL float32 preserves subpixel precision
            sample = [float(x), float(y), float(1 if is_inside else 0)]
            self.data_outlet.push_sample(sample)
        except Exception as e:
            print(f"ERROR pushing data to LSL: {e}")

    def write_marker(self, marker_text: str):
        """Push event marker to LSL"""
        if not self.lsl or not self.marker_outlet:
            return

        try:
            sample = [marker_text]
            self.marker_outlet.push_sample(sample)
        except Exception as e:
            print(f"ERROR pushing marker to LSL: {e}")

    def close(self):
        """Close LSL outlets"""
        if not self.lsl:
            return

        try:
            if self.data_outlet:
                self.data_outlet = None
            if self.marker_outlet:
                self.marker_outlet = None
            if self.numeric_marker_outlet:
                self.numeric_marker_outlet = None
            print("✓ Closed LSL Backend")
        except Exception as e:
            print(f"ERROR closing LSL: {e}")
