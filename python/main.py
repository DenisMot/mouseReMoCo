#!/usr/bin/env python3
"""
mouseReMoCo - Wacom Tablet Test Application

A PyQt6-based application for testing circular target tracing with pen tablets.
Logs position, pressure, and tilt data to CSV and optionally LSL streams.

Usage:
    python main.py
"""

import sys

from PyQt6.QtWidgets import QApplication

from mouseremoco.state import WindowSetup
from mouseremoco.ui.window import MainWindow


def main():
    """Main application entry point"""
    # Create or retrieve the Qt application singleton
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Initialize window orchestrator (creates Configuration internally)
    # Handles: screen detection, dimension calculation, configuration lifecycle,
    # window creation
    window_setup = WindowSetup(
        app=app,
        tablet_test_class=MainWindow,
    )

    # Execute complete initialization pipeline
    # Detects screens → calculates circle radii → creates window →
    # measures frame insets → corrects drawable dimensions → displays window
    main_window = window_setup.create_and_display()
    assert isinstance(main_window, MainWindow)

    # Update configuration MUST be after main_window knows drawable area
    one_lap_length = int(2 * 3.14159 * window_setup.config.internal_radius)
    window_setup.update_configuration(
        trail_length=one_lap_length,  # set trail length to ~ one full circle
        # index_of_difficulty=70.0,  # sets circle perimeter accordingly
    )

    # Launch the Qt event loop
    # Blocks until user closes the window; handles all input and rendering
    exit_code = app.exec()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
