# Cursor Factory — Generate custom cursor images

from PyQt6.QtGui import QPixmap, QPainter, QColor, QCursor
from PyQt6.QtCore import Qt, QPoint


class CursorFactory:
    """Factory for creating custom cursor images with filled circles and crosshairs"""

    @staticmethod
    def create_cursor(
        radius: int,
        color: tuple[int, int, int],
        background_color: tuple[int, int, int] = (0, 0, 0),
    ) -> QCursor:
        """
        Create a custom cursor with a filled circle and center crosshair.

        The crosshair helps identify the exact click point during tablet input.
        Hotspot is placed at center for pixel-accurate targeting.

        Args:
            radius: Cursor circle radius in pixels
            color: RGB tuple (r, g, b) for circle color
            background_color: RGB tuple for crosshair (contrasts with circle for visibility)

        Returns:
            QCursor with hotspot positioned at center (radius, radius) for precision targeting
        """
        diameter = radius * 2

        # Create transparent pixmap
        pixmap = QPixmap(diameter, diameter)
        pixmap.fill(Qt.GlobalColor.transparent)

        # Create painter and draw on pixmap
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw filled circle
        circle_color = QColor(*color)
        painter.setBrush(circle_color)
        painter.setPen(circle_color)
        painter.drawEllipse(0, 0, diameter, diameter)

        # Draw center crosshair (two perpendicular lines)
        crosshair_color = QColor(*background_color)
        painter.setPen(crosshair_color)

        crosshair_length = 4  # pixels extending from center in each direction
        center = radius

        # Horizontal line
        painter.drawLine(
            center - crosshair_length, center, center + crosshair_length, center
        )

        # Vertical line
        painter.drawLine(
            center, center - crosshair_length, center, center + crosshair_length
        )

        painter.end()

        # Create cursor with hotspot at center
        hotspot = QPoint(radius, radius)
        cursor = QCursor(pixmap, hotspot.x(), hotspot.y())

        return cursor

    @staticmethod
    def create_record_cursor(config) -> QCursor:
        """Create cursor for recording state (red circle)"""
        return CursorFactory.create_cursor(
            radius=config.cursor_radius,
            color=config.cursor_color_record,
            background_color=config.background_color,
        )

    @staticmethod
    def create_wait_cursor(config) -> QCursor:
        """Create cursor for waiting state (yellow circle)"""
        return CursorFactory.create_cursor(
            radius=config.cursor_radius,
            color=config.cursor_color_wait,
            background_color=config.background_color,
        )

    @staticmethod
    def create_out_cursor(config) -> QCursor:
        """Create cursor for outside target state (darkened record color)"""
        return CursorFactory.create_cursor(
            radius=config.cursor_radius,
            color=config.cursor_color_record_outside,
            background_color=config.background_color,
        )
