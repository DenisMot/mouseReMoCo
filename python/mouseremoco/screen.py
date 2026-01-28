# Screen management — ScreenInfo + ScreenManager utilities
from dataclasses import dataclass

from PyQt6.QtWidgets import QApplication, QWidget


@dataclass
class ScreenInfo:
    """Information about a screen"""

    name: str
    index: int
    width: int
    height: int
    pos_x: int
    pos_y: int
    phys_width_mm: float
    phys_height_mm: float
    dpi_x: float
    dpi_y: float
    dpi_avg: float
    diag_inches: float


class ScreenManager:
    """Static utility methods for screen and window management"""

    @staticmethod
    def get_screen_info(screen, app: QApplication) -> ScreenInfo:
        """Extract detailed info from a QScreen object"""
        geometry = screen.geometry()
        phys_size = screen.physicalSize()

        # Calculate DPI
        dpi_x = geometry.width() / (phys_size.width() / 25.4)
        dpi_y = geometry.height() / (phys_size.height() / 25.4)
        dpi_avg = (dpi_x + dpi_y) / 2

        # Calculate diagonal in inches
        diag_inches = (phys_size.width() ** 2 + phys_size.height() ** 2) ** 0.5 / 25.4

        return ScreenInfo(
            name=screen.name(),
            index=app.screens().index(screen),
            width=geometry.width(),
            height=geometry.height(),
            pos_x=geometry.x(),
            pos_y=geometry.y(),
            phys_width_mm=phys_size.width(),
            phys_height_mm=phys_size.height(),
            dpi_x=dpi_x,
            dpi_y=dpi_y,
            dpi_avg=dpi_avg,
            diag_inches=diag_inches,
        )

    @staticmethod
    def get_all_screens(app: QApplication) -> list[ScreenInfo]:
        """Get info for all connected screens"""
        return [ScreenManager.get_screen_info(screen, app) for screen in app.screens()]

    @staticmethod
    def print_all_screens(screens: list[ScreenInfo]):
        """Print formatted screen information"""
        print("=" * 60)
        for s in screens:
            print(f"\nScreen {s.index + 1}: {s.name}")
            print(f"  Geometry: {s.width}×{s.height} @ ({s.pos_x}, {s.pos_y})")
            print(f"  DPI: {s.dpi_x:.1f}×{s.dpi_y:.1f} (avg: {s.dpi_avg:.1f})")
            print(f"  Physical: {s.phys_width_mm:.1f}×{s.phys_height_mm:.1f} mm")
            print(f'  Diagonal: {s.diag_inches:.1f}"')

    @staticmethod
    def get_target_screen(
        screens: list[ScreenInfo], config
    ) -> ScreenInfo:
        """Get the target screen with safe fallback"""
        target_index = config._target_monitor - 1  # Convert 1-indexed to 0-indexed
        if 0 <= target_index < len(screens):
            return screens[target_index]
        print(f"⚠ Monitor {config._target_monitor} not found, using primary screen")
        return screens[0]

    @staticmethod
    def get_usable_screen_size(
        app: QApplication, screen_info: ScreenInfo
    ) -> tuple[int, int]:
        """Get usable screen size (excludes taskbars, etc.)"""
        screen = app.screens()[screen_info.index]
        usable = screen.availableGeometry()
        return usable.width(), usable.height()

    @staticmethod
    def get_window_drawable_area(
        widget: QWidget, initial_width: int, initial_height: int
    ) -> tuple[int, int, dict]:
        """Calculate actual drawable area accounting for window frame insets"""
        frame_geometry = widget.frameGeometry()
        content_geometry = widget.geometry()

        # Calculate frame insets
        insets = {
            "top": content_geometry.top() - frame_geometry.top(),
            "bottom": frame_geometry.bottom() - content_geometry.bottom(),
            "left": content_geometry.left() - frame_geometry.left(),
            "right": frame_geometry.right() - content_geometry.right(),
        }

        # Calculate actual drawable dimensions
        actual_width = initial_width - insets["left"] - insets["right"]
        actual_height = initial_height - insets["top"] - insets["bottom"]

        return actual_width, actual_height, insets


class TabletDetector:
    """Detect graphics tablets using Qt's QInputDevice"""

    @staticmethod
    def get_tablets():
        """Returns list of detected stylus/tablet devices"""
        from PyQt6.QtGui import QInputDevice

        tablets = []
        for device in QInputDevice.devices():
            if device.type() == QInputDevice.DeviceType.Stylus:
                tablets.append(device.name())
        return tablets

    @staticmethod
    def has_tablet():
        """Returns True if any tablet is detected"""
        return len(TabletDetector.get_tablets()) > 0

    @staticmethod
    def print_tablet_status():
        """Print tablet detection status to console"""
        tablets = TabletDetector.get_tablets()
        print("\n" + "=" * 60)
        if tablets:
            print(f"✓ Tablet detected: {tablets[0]}")
            if len(tablets) > 1:
                print(f"  ({len(tablets)} total devices found)")
        else:
            print("⚠ No tablet detected - will use mouse input only")
        print("=" * 60)

    @staticmethod
    def print_all_devices():
        """Debug: Print all input devices Qt sees"""
        from PyQt6.QtGui import QInputDevice

        print("\n" + "=" * 60)
        print("All detected input devices:")
        devices = QInputDevice.devices()
        if not devices:
            print("  (no devices found)")
        else:
            for device in devices:
                print(f"  - {device.name()}: {device.type()}")
        print("=" * 60)
