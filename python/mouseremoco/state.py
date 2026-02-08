# WindowSetup — Application window orchestration

from PyQt6.QtWidgets import QApplication

from .config import Configuration, OutputConfiguration
from .screen import ScreenManager, ScreenInfo
from .output.manager import OutputTablet
from .ui.target import CircularTaskConfig
from .types import AppStatus
from . import app_config


class WindowSetup:
    """Encapsulates the complete window setup and initialization process.

    Manages both window AND configuration lifecycle, making WindowSetup
    the true orchestrator of the complete initialization workflow.

    Configuration is created internally and can be customized via the
    config property before calling create_and_display().
    """

    def __init__(
        self,
        app: QApplication,
        tablet_test_class,
    ):
        self.app = app
        self.tablet_test_class = tablet_test_class

        # Create configuration internally - owned by WindowSetup
        self.config = Configuration()

        self.screens = None
        self.target_screen_info: ScreenInfo | None = None
        self.usable_width: int = 0
        self.usable_height: int = 0
        self.widget = None
        self.app_status = AppStatus()
        self.output_data = None
        self.circle_config = None

    def initialize_screens(self):
        """Step 1: Detect screens and select target"""
        self.screens = ScreenManager.get_all_screens(self.app)
        ScreenManager.print_all_screens(self.screens)
        self.target_screen_info = ScreenManager.get_target_screen(
            self.screens, self.config
        )
        self.usable_width, self.usable_height = ScreenManager.get_usable_screen_size(
            self.app, self.target_screen_info
        )

    def set_frame_geometry(self):
        """Set window geometry to target screen with frame insets."""

        if self.target_screen_info is None:
            raise RuntimeError(
                "initialize_screens() must be called before set_frame_geometry()"
            )

        # create a temporary widget with only the frame to measure insets
        from PyQt6.QtWidgets import QWidget

        temp_widget = QWidget()
        temp_widget.setWindowTitle("Measuring frame insets...")
        temp_widget.move(self.target_screen_info.pos_x, self.target_screen_info.pos_y)
        temp_widget.show()
        self.app.processEvents()
        actual_width, actual_height, insets = ScreenManager.get_window_drawable_area(
            temp_widget, self.usable_width, self.usable_height
        )
        self.config._frame_insets = insets
        self.config._frame_width = actual_width
        self.config._frame_height = actual_height
        self.config.screen_width = actual_width
        self.config.screen_height = actual_height
        self.config._frame_location_x = self.target_screen_info.pos_x
        self.config._frame_location_y = self.target_screen_info.pos_y
        self.config._screen_used_id = self.target_screen_info.index
        temp_widget.close()

        print(f"DEBUG state.py set_frame_geometry: insets = {insets}")
        print(
            f"DEBUG state.py set_frame_geometry: frame = "
            f"{self.config._frame_width}x{self.config._frame_height}"
        )

    def calculate_initial_radii(self) -> tuple[int, int, CircularTaskConfig]:
        """Step 2-3: Calculate initial radii and create circle config"""
        external_radius, internal_radius = self.config.calculate_default_circle_radii(
            screen_width=self.usable_width,
            screen_height=self.usable_height,
        )

        circle_config = CircularTaskConfig(
            external_radius=external_radius,
            internal_radius=internal_radius,
            background_color=CircularTaskConfig.rgb_to_hex(
                self.config.background_color
            ),
        )
        return external_radius, internal_radius, circle_config

    def create_widget(self):
        """Step 4: Create and position window widget"""
        if self.target_screen_info is None:
            raise RuntimeError(
                "initialize_screens() must be called before create_widget()"
            )
        widget = self.tablet_test_class(
            config=self.config,
            window_setup=self,
            output_data=None,
            app_status=self.app_status,
        )
        widget.setWindowTitle(self.config._title)
        widget.move(self.target_screen_info.pos_x, self.target_screen_info.pos_y)

        window_width = self.config._frame_width
        window_height = self.config._frame_height
        widget.resize(window_width, window_height)

        return widget

    def add_circular_task_to_widget(self):
        """Add circular task widget to main window"""
        if self.widget is None:
            raise RuntimeError("Widget must be created before adding task")
        from .ui.target import CircularTargetWidget

        # Create corrected circle config
        corrected_circle_config = CircularTaskConfig(
            external_radius=self.config.external_radius,
            internal_radius=self.config.internal_radius,
            background_color=CircularTaskConfig.rgb_to_hex(
                self.config.background_color
            ),
        )

        self.widget.circular_target = CircularTargetWidget(
            config=corrected_circle_config
        )
        self.widget.update()

    def set_config_default_circle_for_frame_geometry(self):
        """set configuration values for a circular target sized on actual drawable area
        of the window"""

        print("DEBUG state.py set_config_default_circle_for_frame")

        external_radius, internal_radius = self.config.calculate_default_circle_radii(
            screen_width=self.config.screen_width,
            screen_height=self.config.screen_height,
        )

        # Update config with corrected radii and actual dimensions
        self.config.external_radius = external_radius
        self.config.internal_radius = internal_radius

        # Calculate and set center coordinates
        center_x = self.config.screen_width // 2
        center_y = self.config.screen_height // 2
        self.config.set_center_x(center_x)
        self.config.set_center_y(center_y)

        # Update derived values
        self.config._update_circular_task()

    def _update_widget(self):

        print("DEBUG state.py _update_widget: creating corrected circle config with ")

        # Create corrected circle config
        corrected_circle_config = CircularTaskConfig(
            external_radius=self.config.external_radius,
            internal_radius=self.config.internal_radius,
            background_color=CircularTaskConfig.rgb_to_hex(
                self.config.background_color
            ),
        )
        # Update widget with corrected values
        if self.widget is None:
            raise RuntimeError("Widget must be created before updating circular target")

        from .ui.target import CircularTargetWidget

        self.widget.circular_target = CircularTargetWidget(
            config=corrected_circle_config
        )
        self.widget.update()

    def is_lsl_available(self) -> bool:
        """Check if LSL backend can be initialized"""
        print("✓ Scouting for LSL availability...")

        try:
            import pylsl
        except ImportError:
            print("⚠ LSL library not available (pylsl not installed)")
            return False

        # try to create a StreamOutlet to check if LSL is fully functional
        try:
            test_outlet = pylsl.StreamOutlet(
                pylsl.StreamInfo("TestStream", "Markers", 1, 0, pylsl.cf_string)
            )
        except Exception as e:
            print(f"⚠ LSL StreamOutlet initialization failed: {e}")
            return False

        if test_outlet is None:
            print("⚠ LSL is NOT functional")
            return False

        print("✓ LSL functional")
        return True

    def initialize_backends(self):
        """Create output backends with finalized configuration"""

        # check LSL availability and update config accordingly
        if app_config.ENABLE_LSL:
            self.config.is_with_lsl = self.is_lsl_available()

        # Create OutputConfiguration based on final config
        self.config._output_config = OutputConfiguration(self.config)

        # Create OutputData with the final configuration
        self.output_data = OutputTablet(
            config=self.config,
            app_status=self.app_status,
            output_config=self.config._output_config,
            enable_csv=app_config.ENABLE_CSV,
            enable_lsl=app_config.ENABLE_LSL,
        )

        # Assign output_data to widget and trail
        if self.widget is None:
            raise RuntimeError("Widget must be created before initialize_backends()")
        self.widget.output_data = self.output_data
        self.widget.trail.output_data = self.output_data

    def update_configuration(self, **kwargs):
        """Update configuration parameters and refresh the display.

        Args:
            **kwargs: Configuration parameters to update
                e.g., update_configuration(cursor_radius=20, index_of_difficulty=100)

        Supports any configuration property:
            - cursor_radius, cycle_max_number, background_color, etc.
            - index_of_difficulty (calls set_index_of_difficulty internally)
            - circle_perimeter (tuple: (perimeter_mm, screen_resolution_ppi))
        """

        for key, value in kwargs.items():
            if key == "index_of_difficulty":
                self.config.set_index_of_difficulty(value)
            elif key == "circle_perimeter":
                # Expects tuple: (perimeter_mm, screen_resolution_ppi)
                perimeter_mm, screen_resolution_ppi = value
                self.config.set_circle_perimeter(perimeter_mm, screen_resolution_ppi)
            elif key == "trail_mode":
                self.config.trail_mode = value
                if self.widget and self.widget.trail:
                    self.widget.trail.set_mode(value)
            elif hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                print(f"⚠ Warning: Configuration has no attribute '{key}'")

        # Update circular task derived values
        self.config._update_circular_task()

        # Print configuration
        print("\n" + "=" * 60)
        print("Configuration at startup:")
        print(self.config.to_string())
        print("=" * 60 + "\n")

    def setup_and_run(self, config_updates: dict | None = None):
        """Complete initialization workflow from startup to ready-to-run.

        Steps:
            1. Detect screens and calculate dimensions
            2. Create window widget
            3. Measure actual drawable area
            4. Apply user configuration updates (if any)
            5. Auto-calculate trail_length if not provided
            6. Create output backends with final configuration
            7. Display and focus window

        Args:
            config_updates: Optional dict of configuration parameters to apply
                        e.g., {"index_of_difficulty": 70.0}
                        If "trail_length" is not provided, it's auto-calculated

        Returns:
            The configured main window widget
        """
        # LOGIC: at each step, the configuration is updated
        # and used for the next step, ensuring all components are in sync

        # Step 1: Detect screens and calculate drawable dimensions
        self.initialize_screens()
        self.set_frame_geometry()

        # Step 2: Set circle config, with updates if provided (e.g., from command line)
        self.set_config_default_circle_for_frame_geometry()
        if config_updates:
            self.update_configuration(**config_updates)

        # Step 3: Create window widget with config
        self.widget = self.create_widget()
        self.add_circular_task_to_widget()

        self.initialize_backends()

        # Last: Display and focus the window
        self.widget.update()
        self.widget.show()
        self.widget.raise_()
        self.widget.setFocus()
