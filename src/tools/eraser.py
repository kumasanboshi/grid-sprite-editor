from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QMouseEvent
from .base import BaseTool


class EraserTool(BaseTool):
    def __init__(self, canvas):
        super().__init__(canvas)
        self.brush_size = 20
        self._drawing = False
        self._last_pos: QPointF | None = None

    def mouse_press(self, event: QMouseEvent, image_pos: QPointF):
        self.canvas.history.push(self.canvas.image)
        self._drawing = True
        self._last_pos = image_pos
        self._erase(image_pos)

    def mouse_move(self, event: QMouseEvent, image_pos: QPointF):
        if self._drawing:
            self._erase(image_pos)
            self._last_pos = image_pos

    def mouse_release(self, event: QMouseEvent, image_pos: QPointF):
        self._drawing = False
        self._last_pos = None

    def _erase(self, pos: QPointF):
        from PIL import ImageDraw
        img = self.canvas.image
        draw = ImageDraw.Draw(img)
        r = self.brush_size // 2
        x, y = int(pos.x()), int(pos.y())
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(0, 0, 0, 0))
        self.canvas.refresh_pixmap()
        self.canvas.update()

    def cursor(self):
        return Qt.CursorShape.CrossCursor
