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

        window_width = self.config._width or self.usable_width
        window_height = self.config._height or self.usable_height
        widget.resize(window_width, window_height)

        return widget

    def measure_and_correct_dimensions(self):
        """Step 5-8: Measure frame insets and update widget with corrected dimensions"""
        if self.target_screen_info is None:
            raise RuntimeError(
                "initialize_screens() must be called before "
                + "measure_and_correct_dimensions()"
            )
        if self.widget is None:
            raise RuntimeError(
                "create_widget() must be called before "
                + "measure_and_correct_dimensions()"
            )
        # Show window to make frame insets calculable
        self.widget.show()
        self.app.processEvents()

        # Measure actual drawable area
        actual_width, actual_height, insets = ScreenManager.get_window_drawable_area(
            self.widget, self.usable_width, self.usable_height
        )
        print(
            f"\nWindow frame insets: "
            f"Top={insets['top']}, Bottom={insets['bottom']}, "
            f"Left={insets['left']}, Right={insets['right']}"
        )

        # Recalculate radii with actual drawable area
        external_radius, internal_radius = self.config.calculate_default_circle_radii(
            actual_width, actual_height
        )

        # Update config with corrected radii and actual dimensions
        self.config.screen_width = actual_width
        self.config.screen_height = actual_height
        # self.config.drawable_width = actual_width
        # self.config.drawable_height = actual_height
        self.config._frame_location_x = self.target_screen_info.pos_x
        self.config._frame_location_y = self.target_screen_info.pos_y
        self.config._frame_insets = insets
        self.config._used_screen_id = self.target_screen_info.index
        self.config.external_radius = external_radius
        self.config.internal_radius = internal_radius

        # Calculate and set center coordinates
        center_x = actual_width // 2
        center_y = actual_height // 2
        self.config.set_center_x(center_x)
        self.config.set_center_y(center_y)

        # Update derived values
        self.config._update_circular_task()

        # Create corrected circle config
        corrected_circle_config = CircularTaskConfig(
            external_radius=external_radius,
            internal_radius=internal_radius,
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
        # self.widget.drawable_width = actual_width
        # self.widget.drawable_height = actual_height
        # self.widget.center_x = center_x
        # self.widget.center_y = center_y
        self.widget.update()

    def finalize_display(self):
        """Step 9: Finalize window display"""

        # Create OutputConfiguration after center is determined
        self.config._output_config = OutputConfiguration(self.config)

        # DON'T create backends here anymore
        # Just assign widget references
        if self.widget is None:
            raise RuntimeError("Widget must be created before finalize_display()")

        # Bring window to front and focus
        self.widget.raise_()
        self.widget.setFocus()

    def initialize_backends(self):
        """Create output backends with finalized configuration"""
        # Create OutputData NOW = with the final configuration
        self.output_data = OutputTablet(
            config=self.config,
            app_status=self.app_status,
            output_config=self.config._output_config,
            enable_csv=app_config.ENABLE_CSV,
            enable_lsl=app_config.ENABLE_LSL,
        )

        # Update is_with_lsl based on LSL backend availability
        self.config.is_with_lsl = any(
            backend.__class__.__name__ == "LSLBackend"
            for backend in self.output_data.backends
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
        from .ui.target import CircularTargetWidget

        for key, value in kwargs.items():
            if key == "index_of_difficulty":
                # Special handling for index_of_difficulty
                self.config.set_index_of_difficulty(value)
            elif key == "circle_perimeter":
                # Expects tuple: (perimeter_mm, screen_resolution_ppi)
                perimeter_mm, screen_resolution_ppi = value
                self.config.set_circle_perimeter(perimeter_mm, screen_resolution_ppi)
            elif hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                print(f"⚠ Warning: Configuration has no attribute '{key}'")

        # Update circular task derived values
        self.config._update_circular_task()

        # Recreate OutputConfiguration with updated config
        if self.config._output_config:
            self.config._output_config = OutputConfiguration(self.config)

            # Update all backends with new output_config
            if self.output_data:
                for backend in self.output_data.backends:
                    backend.output_config = self.config._output_config

        # Recreate circle config with updated radii if needed
        corrected_circle_config = CircularTaskConfig(
            external_radius=self.config.external_radius,
            internal_radius=self.config.internal_radius,
            background_color=CircularTaskConfig.rgb_to_hex(
                self.config.background_color
            ),
        )

        # Update widget
        if self.widget is None:
            raise RuntimeError("Widget must be created before updating circular target")
        self.widget.circular_target = CircularTargetWidget(
            config=corrected_circle_config
        )
        self.widget.update()

        # Print configuration
        print("\n" + "=" * 60)
        print("Configuration:")
        print(self.config.to_string())
        print("=" * 60 + "\n")
        if self.config._output_config:
            print("Output Configuration:")
            print(self.config._output_config.to_string())
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
        # Step 1: Detect screens and calculate dimensions
        self.initialize_screens()
        _, _, self.circle_config = self.calculate_initial_radii()

        # Step 2: Create window widget
        self.widget = self.create_widget()

        # Step 3: Measure actual drawable area
        self.measure_and_correct_dimensions()

        # Step 4: Apply user configuration updates
        if config_updates:
            self.update_configuration(**config_updates)

        # Step 5: Auto-calculate trail_length if not explicitly set
        if config_updates is None or "trail_length" not in config_updates:
            one_lap_length = int(2 * 3.14159 * self.config.internal_radius)
            self.update_configuration(trail_length=one_lap_length)

        # Step 6: Create output backends with final configuration
        self.finalize_display()
        self.initialize_backends()

        # Step 7: Display and focus window
        self.widget.raise_()
        self.widget.setFocus()

        return self.widget
