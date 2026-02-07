# configuration class for mouseReMoCo application

from enum import Enum
import copy
from . import app_config


class TaskType(Enum):
    """Task types supported by the application"""

    CIRCULAR = "circular"
    LINEAR = "linear"


class OutputConfiguration:
    """Configuration for data output coordinate system (CSV, LSL).

    Creates a copy of the Configuration object and modifies it for output.
    Handles coordinate transformation:
    screen → center-origin with y-reversed (matplotlib style).

    Stores pressure threshold values for data output.
    """

    def __init__(self, config):
        """Initialize with Configuration object and create a working copy.

        Args:
            config: Configuration instance to copy and modify for output
        """
        # Store original screen center for transformation calculations
        self.origin_x = config.center_x
        self.origin_y = config.center_y

        # Store pressure thresholds from original config                # ← NEW
        # These represent the pressure band active when recording started
        self.pressure_band_low = config.pressure_band_low  # ← NEW
        self.pressure_band_high = config.pressure_band_high  # ← NEW

        self.config = copy.deepcopy(config)

        # update the config copy to reflect output coordinate system
        self.config.center_x = self.config.center_x - self.origin_x
        self.config.center_y = self.config.center_y - self.origin_y
        self.config.corner_x = self.config.corner_x - self.origin_x
        self.config.corner_y = self.config.corner_y - self.origin_y
        self.config.origin_mode = "center"
        self.config.y_reversed = True

    def transform_coordinates(self, x: float, y: float) -> tuple[float, float]:
        """Convert screen coordinates to output coordinates."""
        x_out = x - self.origin_x  # Use origin_x, not center_x
        y_out = self.origin_y - y  # Use origin_y, not center_y
        return x_out, y_out

    def to_string(self) -> str:
        """Generate output configuration string representation"""

        # print all configuration parameters
        parts = []
        for key, value in self.config.__dict__.items():
            parts.append(f"{key}: {value}")

        return "\n".join(parts)


class Configuration:
    """
    Main configuration class mirroring Java Configuration.java
    Handles all application settings including:
    - Screen and window configuration
    - Circular and linear task parameters
    - Visual styling (colors, cursors, fonts)
    - Input and output settings

    INSTANTIATION: Must be created with NO arguments
        config = Configuration()

    CUSTOMIZATION: Set properties explicitly before setup
        config.cursor_radius = 20
        config.cycle_max_number = 4

    RUNTIME: Call setup.create_and_display() to populate
        - screen_width, screen_height
        - drawable_width, drawable_height
        - center_x, center_y
        - all derived values (internal_limit, external_limit, etc.)
    """

    def __init__(self):
        """Initialize Configuration with NO arguments - use defaults.

        To customize behavior:
        1. Create: config = Configuration()
        2. Modify defaults as needed before setup
        3. Call: setup.create_and_display() which populates runtime values

        This design ensures clarity: anything not explicitly set before
        measure_and_correct_dimensions() gets its runtime value there.
        """

        # ===== Software =====
        self.software = app_config.SOFTWARE_NAME
        self.version = app_config.SOFTWARE_VERSION

        # ===== Window Configuration =====
        self._title = app_config.WINDOW_TITLE
        self._target_monitor = app_config.TARGET_MONITOR
        self._width = app_config.WINDOW_WIDTH
        self._height = app_config.WINDOW_HEIGHT
        self._nb_cursor_radii_for_target_margin = (
            app_config.NB_CURSOR_RADII_FOR_TARGET_MARGIN
        )

        # ===== Screen & Window Configuration =====
        # These are set during setup.create_and_display()
        self.screen_width = 0  # in pixels: drawable area width
        self.screen_height = 0  # in pixels: drawable area height
        self._frame_location_x = 0
        self._frame_location_y = 0
        self._frame_insets = {"top": 0, "bottom": 0, "left": 0, "right": 0}
        self._frame_undecorated = False
        self._used_screen_id = 0

        # ===== Circular Task Parameters =====
        self.task_string = "circular"
        self.center_x = 0
        self.center_y = 0
        self.corner_x = 0
        self.corner_y = 0
        self.external_radius = app_config.EXTERNAL_RADIUS
        self.internal_radius = app_config.INTERNAL_RADIUS
        self.border_radius = app_config.BORDER_RADIUS
        self.circle_perimeter_mm = 0

        # ===== Circular task derived values =====
        # These are calculated in _update_circular_task() based on the current radii
        # and cursor size and after screen dimensions are set
        self.task_radius = 0.0
        self.tolerance_px = 0
        self.index_of_difficulty = 0.0
        self.internal_limit = 0
        self.external_limit = 0

        # ===== Linear Task Parameters =====
        # These are set when switching to linear task
        self.inter_line_distance_mm = app_config.INTER_LINE_DISTANCE_MM
        self.line_height_mm = app_config.LINE_HEIGHT_MM
        self.mm2px = 0.0  # To be calculated based on screen PPI during setup

        # ===== Auditory Rhythm =====
        self.half_period = app_config.RHYTHM_HALF_PERIOD_MS

        # ===== Cursor Configuration =====
        self.cursor_radius = app_config.CURSOR_RADIUS
        self.cursor_color_record = app_config.CURSOR_COLOR_RECORDING
        self.cursor_color_record_outside = app_config.CURSOR_COLOR_RECORDING_OUTSIDE
        self.cursor_color_wait = app_config.CURSOR_COLOR_WAITING

        # ===== Visual Styling =====
        self.border_color = app_config.BORDER_COLOR  # RGB white
        self.background_color = app_config.BACKGROUND_COLOR  # RGB black
        self.text_color = app_config.TEXT_COLOR  # RGB white

        # ===== Sequence Configuration =====
        # seconds before auto start recording
        self.auto_start = app_config.AUTO_START_DELAY
        # Move-Rest cycle number before stopping cycling after last Rest
        self.cycle_max_number = app_config.CYCLE_MAX_NUMBER
        # seconds for a Move or a Rest (half-cycle)
        self.cycle_duration = app_config.CYCLE_DURATION

        # ===== Font Configuration =====
        self.font_size = app_config.FONT_SIZE
        self.font_family = app_config.FONT_FAMILY

        # ===== Flags =====
        # Lab Streaming Layer present and enabled (or not)
        self.is_with_lsl = False  # will be set if LSL is successfully initialized
        # Whether to show target during pause (rest)
        self.is_target_hidden_during_pause = app_config.HIDE_TARGET_DURING_PAUSE

        # ===== Trail Configuration =====
        self.trail_mode = app_config.TRAIL_MODE  # Active trail mode
        # Trail length in pixels; None means 10×cursor_radius
        self.trail_length = app_config.TRAIL_LENGTH

        # ===== Pressure band configuration (0.0 - 1.0) =====
        # Band defined by a center and full width;
        # low/high are derived at runtime
        self.pressure_band_center = app_config.PRESSURE_BAND_CENTER
        self.pressure_band_width = app_config.PRESSURE_BAND_WIDTH
        self.pressure_band_low = None  # derived at runtime
        self.pressure_band_high = None  # derived at runtime

        # ===== Output Configuration =====
        # Will be created after center_x, center_y are determined
        self._output_config: OutputConfiguration | None = None

        # ===== Initialize derived values at runtime =====
        # Initialize derived values
        self._update_circular_task()
        self._update_pressure_band()

    def _update_pressure_band(self, to_adapt: str | None = None):
        """Update pressure band derived values"""

        if to_adapt not in (None, "center", "width"):
            raise ValueError("to_adapt must be None, 'center', or 'width'")

        if to_adapt is None:
            # Initial calculation: just compute low/high based on current center/width
            to_adapt = "center"

        center = self.pressure_band_center
        width = self.pressure_band_width
        half_width = width / 2
        # ensure center+/-width/2 are within [0.02, 1.0]
        if to_adapt == "center":
            # clip center if changed
            center = max(center, 0.0 + half_width)
            center = min(center, 1.0 - half_width)
        elif to_adapt == "width":
            # clip half_width if changed
            half_width = min(half_width, center - 0.01)  # ensure low >= 0.01
            half_width = min(half_width, 1.0 - center)  # ensure high <= 0.99
            half_width = max(half_width, 0.01)  # minimum width of 0.02 to ensure a band
            width = half_width * 2

        low = center - half_width
        high = center + half_width

        self.pressure_band_low = low
        self.pressure_band_high = high
        self.pressure_band_width = width
        self.pressure_band_center = center

    def _update_circular_task(self):
        """Update circular task derived values"""
        if self.task_string == "circular":
            # Limits of the path
            self.internal_limit = self.internal_radius + self.cursor_radius
            self.external_limit = (
                self.external_radius - self.cursor_radius - self.border_radius
            )

            # ID in the steering law (Accot & Zhai 1999)
            self.task_radius = (self.internal_limit + self.external_limit) / 2.0
            self.tolerance_px = self.external_limit - self.internal_limit

            if self.tolerance_px > 0:
                self.index_of_difficulty = (
                    2.0 * 3.14159 * self.task_radius
                ) / self.tolerance_px

    def get_trail_length(self) -> int:
        """Get trail length for current mode,
        defaulting to 10×cursor_radius if not set"""
        if self.trail_length is not None:
            return self.trail_length
        return 10 * self.cursor_radius

    def set_index_of_difficulty(self, index_of_difficulty: float):
        """Set index of difficulty and adjust circle parameters"""
        if self.task_string != "circular":
            return

        # Calculate new tolerance width
        w = (3.14159 * self.external_limit) / (index_of_difficulty + 3.14159)
        wn = round(2 * w)

        # Update internal limit and radius
        self.internal_limit = self.external_limit - wn
        self.internal_radius = self.internal_limit - self.cursor_radius

        # Recalculate derived values
        self._update_circular_task()

    def set_circular_task(self):
        """Initialize circular task parameters"""
        self._update_circular_task()

    def set_linear_task(self):
        """Initialize linear task parameters"""
        # Linear task setup would go here
        pass

    def set_circle_perimeter(self, perimeter_mm: int, screen_resolution_ppi: float):
        """Set circle perimeter and adjust circle parameters accordingly"""
        if perimeter_mm <= 0 or screen_resolution_ppi <= 0:
            return

        # Convert mm to pixels. (1 inch = 25.4 mm)
        self.circle_perimeter_mm = perimeter_mm
        perimeter_px = perimeter_mm * screen_resolution_ppi / 25.4

        # Calculate new radius and tolerance
        self.task_radius = perimeter_px / (2.0 * 3.14159)
        tolerance = perimeter_px / self.index_of_difficulty

        external_limit = self.task_radius + tolerance / 2.0
        internal_limit = self.task_radius - tolerance / 2.0

        external_radius = external_limit + self.cursor_radius + self.border_radius
        internal_radius = internal_limit - self.cursor_radius

        self.external_radius = round(external_radius)
        self.internal_radius = round(internal_radius)

        self.corner_x = self.screen_width // 2 - self.external_radius
        self.corner_y = self.screen_height // 2 - self.external_radius

        self._update_circular_task()

    def calculate_default_circle_radii(
        self, screen_width: int, screen_height: int
    ) -> tuple[int, int]:
        """Calculate circle radii based on screen dimensions and margin"""
        # NOTE: default margin is 5 times cursor radius
        # Calculate available space accounting for margins
        margin_px = self._nb_cursor_radii_for_target_margin * self.cursor_radius
        available_width = screen_width - 2 * margin_px
        available_height = screen_height - 2 * margin_px

        # Use smaller dimension to ensure circle fits
        max_diameter = min(available_width, available_height)

        if max_diameter <= 0:
            return self.external_radius, self.internal_radius

        # External radius is half the maximum diameter
        external_radius = max_diameter // 2

        # Internal radius is 60% of external radius
        internal_radius = int(external_radius * 0.6)

        return external_radius, internal_radius

    def set_center_x(self, center_x: int):
        """Set center X and update corner X accordingly"""
        self.center_x = center_x
        self.corner_x = center_x - self.external_radius

    def set_center_y(self, center_y: int):
        """Set center Y and update corner Y accordingly"""
        self.center_y = center_y
        self.corner_y = center_y - self.external_radius

    def set_corner_x(self, corner_x: int):
        """Set corner X and update center X accordingly"""
        self.corner_x = corner_x
        self.center_x = corner_x + self.external_radius

    def set_corner_y(self, corner_y: int):
        """Set corner Y and update center Y accordingly"""
        self.corner_y = corner_y
        self.center_y = corner_y + self.external_radius

    def to_string(self) -> str:
        """Generate configuration string representation"""

        # print all configuration parameters
        parts = []
        for key, value in self.__dict__.items():
            parts.append(f"{key}: {value}")

        return "\n".join(parts)
