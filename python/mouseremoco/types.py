"""Shared lightweight types used across modules.

This module holds small data/state classes referenced by both
`state` and UI modules to avoid circular imports.
"""
import time


class AppStatus:
    """Centralized application and UI state management.

    Groups all application state logically:
    - Record/pause state
    - Input device state
    - Display/window state
    - Task/task execution state

    Keep this class minimal to avoid importing heavy UI or state modules here.
    """

    def __init__(self):
        # ===== Recording & Output State =====
        self.is_recording = False  # default: not recording at start
        self.recording_start_time = None
        self.total_recording_duration = 0.0  # Accumulates across pause/resume cycles
        self.pause_count = 0  # How many times paused

        # ===== Input Device State =====
        self.tablet_detected = False
        self.active_input_type = "mouse"  # "mouse" or "tablet"
        self.last_input_time = None

        # ===== Display State =====
        self.fullscreen_mode = 0  # 0=windowed, 1=fullscreen
        self.show_debug_info = False  # Future: toggle debug rectangles

        # ===== Trail State =====
        self.current_trail_mode = "fixed"  # One of Trail.VALID_MODES

        # ===== Task State =====
        self.task_started = False
        self.task_start_time = None
        self.task_elapsed_time = 0.0

    def start_recording(self):
        """Start or resume recording"""
        self.is_recording = True
        self.recording_start_time = time.time()

    def pause_recording(self):
        """Pause recording and accumulate duration"""
        if self.is_recording and self.recording_start_time:
            elapsed = time.time() - self.recording_start_time
            self.total_recording_duration += elapsed
            self.pause_count += 1
        self.is_recording = False

    def toggle_recording(self):
        """Toggle recording state"""
        if self.is_recording:
            self.pause_recording()
        else:
            self.start_recording()
        return self.is_recording

    def get_status_string(self) -> str:
        """Get human-readable status for display or logging"""
        status_lines = [
            f"Recording: {'ON' if self.is_recording else 'PAUSED'}",
            f"Input: {self.active_input_type.upper()}",
            f"Trail Mode: {self.current_trail_mode.upper()}",
            f"Pause Count: {self.pause_count}",
        ]

        if self.task_started:
            status_lines.append(f"Task Time: {self.task_elapsed_time:.1f}s")

        return " | ".join(status_lines)
