# Circular target rendering

from dataclasses import dataclass
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen


@dataclass
class CircularTaskConfig:
    """Configuration for circular target task"""

    external_radius: int = 150  # pixels
    internal_radius: int = 80  # pixels
    background_color: str = "black"
    path_color: str = "#333333"  # darkgray < "#333333"  < "#1a1a1a" < black
    circle_border_color: str = "white"
    circle_border_width: int = 2

    @staticmethod
    def rgb_to_hex(rgb_tuple: tuple[int, int, int]) -> str:
        """Convert RGB tuple (r, g, b) to hex color string"""
        r, g, b = rgb_tuple
        return f"#{r:02x}{g:02x}{b:02x}"


class CircularTargetWidget:
    """Draw circular target with tolerance band"""

    def __init__(self, config: CircularTaskConfig | None = None):
        self.config = config or CircularTaskConfig()

    def draw(self, painter: QPainter, center_x: int, center_y: int):
        """Draw the circular target"""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw external circle (border)
        self._draw_filled_circle(
            painter=painter,
            x=center_x,
            y=center_y,
            radius=self.config.external_radius,
            fill_color=self.config.path_color,
            border_color=self.config.circle_border_color,
            border_width=self.config.circle_border_width,
        )

        # Draw internal circle (background)
        self._draw_filled_circle(
            painter=painter,
            x=center_x,
            y=center_y,
            radius=self.config.internal_radius,
            fill_color=self.config.background_color,
            border_color=self.config.circle_border_color,
            border_width=self.config.circle_border_width,
        )

    def _draw_filled_circle(
        self,
        painter: QPainter,
        x: int,
        y: int,
        radius: int,
        fill_color: str,
        border_color: str,
        border_width: int,
    ):
        """Helper to draw filled circle with border"""
        # Set fill color
        fill = QColor(fill_color)
        painter.setBrush(QBrush(fill))

        # Set border (pen)
        border = QColor(border_color)
        pen = QPen(border)
        pen.setWidth(border_width)
        painter.setPen(pen)

        # Draw circle
        painter.drawEllipse(x - radius, y - radius, 2 * radius, 2 * radius)
