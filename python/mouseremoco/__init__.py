"""mouseReMoCo - Wacom Tablet Test Application"""

__version__ = "2.0.0"
__author__ = "Denis Mottet"

# Optional: Export main classes for easier imports
from .config import Configuration, OutputConfiguration
from .types import AppStatus
from .state import WindowSetup
from .ui.window import MainWindow

__all__ = [
    "Configuration",
    "OutputConfiguration",
    "AppStatus",
    "WindowSetup",
    "MainWindow",
]
