from abc import ABC, abstractmethod
from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QMouseEvent


class BaseTool(ABC):
    """Base class for all canvas tools."""

    def __init__(self, canvas):
        self.canvas = canvas  # ref to SpriteCanvas

    def mouse_press(self, event: QMouseEvent, image_pos: QPointF):
        pass

    def mouse_move(self, event: QMouseEvent, image_pos: QPointF):
        pass

    def mouse_release(self, event: QMouseEvent, image_pos: QPointF):
        pass

    def cursor(self):
        from PyQt6.QtCore import Qt
        return Qt.CursorShape.ArrowCursor
