from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QMouseEvent
from .base import BaseTool


class CellMoveTool(BaseTool):
    """Alt+drag to move the entire content of a cell."""

    def __init__(self, canvas):
        super().__init__(canvas)
        self._active = False
        self._cell: tuple[int, int] | None = None
        self._start: QPointF | None = None

    def mouse_press(self, event: QMouseEvent, image_pos: QPointF):
        if not self.canvas.image:
            return
        w, h = self.canvas.image.size
        cell = self.canvas.grid.cell_at(w, h, int(image_pos.x()), int(image_pos.y()))
        if cell is None:
            return
        self.canvas.history.push(self.canvas.image)
        self._active = True
        self._cell = cell
        self._start = image_pos

    def mouse_move(self, event: QMouseEvent, image_pos: QPointF):
        if not self._active or not self._start or not self._cell:
            return
        # live preview: just store delta for paint
        self.canvas._cell_move_delta = (
            int(image_pos.x() - self._start.x()),
            int(image_pos.y() - self._start.y()),
        )
        self.canvas._cell_move_cell = self._cell
        self.canvas.update()

    def mouse_release(self, event: QMouseEvent, image_pos: QPointF):
        if not self._active or not self._start or not self._cell:
            return
        dx = int(image_pos.x() - self._start.x())
        dy = int(image_pos.y() - self._start.y())
        if dx != 0 or dy != 0:
            self.canvas.apply_cell_move(self._cell, dx, dy)
        self.canvas._cell_move_delta = None
        self.canvas._cell_move_cell = None
        self._active = False
        self._cell = None
        self._start = None

    def cursor(self):
        return Qt.CursorShape.SizeAllCursor
