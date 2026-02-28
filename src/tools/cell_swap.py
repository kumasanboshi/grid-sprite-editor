from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QMouseEvent
from .base import BaseTool


class CellSwapTool(BaseTool):
    """Click first cell then second cell to swap their contents."""

    def __init__(self, canvas):
        super().__init__(canvas)
        self._first_cell: tuple[int, int] | None = None

    def mouse_press(self, event: QMouseEvent, image_pos: QPointF):
        if not self.canvas.image:
            return
        w, h = self.canvas.image.size
        cell = self.canvas.grid.cell_at(w, h, int(image_pos.x()), int(image_pos.y()))
        if cell is None:
            return
        if self._first_cell is None:
            self._first_cell = cell
            self.canvas.swap_highlight = cell
            self.canvas.update()
        else:
            if cell != self._first_cell:
                self.canvas.history.push(self.canvas.image)
                self.canvas.swap_cells(self._first_cell, cell)
            self._first_cell = None
            self.canvas.swap_highlight = None
            self.canvas.update()

    def cursor(self):
        return Qt.CursorShape.PointingHandCursor
