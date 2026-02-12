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
    app = QApplication.instance() or QApplication(sys.argv)

    window_setup = WindowSetup(app=app, tablet_test_class=MainWindow)

    window_setup.setup_and_run(
        config_updates={
            # Here, updates supersede app_config.py defaults for this run.
            # NOTE: This is where command-line overrides could be applied in the future.
            # "index_of_difficulty": 70.0,
            # "trail_mode": "path_length",  # "none", "path_length"
        }
    )

    exit_code = app.exec()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
