from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QMouseEvent, QKeyEvent
from .base import BaseTool


class CellScaleTool(BaseTool):
    """Click to select cells, then scale their content."""

    def __init__(self, canvas):
        super().__init__(canvas)
        self.selected_cells: set[tuple[int, int]] = set()

    def mouse_press(self, event: QMouseEvent, image_pos: QPointF):
        if not self.canvas.image:
            return
        iw, ih = self.canvas.image.size
        cell = self.canvas.grid.cell_at(iw, ih, int(image_pos.x()), int(image_pos.y()))
        if cell is None:
            return

        shift = event.modifiers() & Qt.KeyboardModifier.ShiftModifier
        if shift:
            if cell in self.selected_cells:
                self.selected_cells.discard(cell)
            else:
                self.selected_cells.add(cell)
        else:
            if self.selected_cells == {cell}:
                self.selected_cells.clear()
            else:
                self.selected_cells = {cell}

        self.canvas.cell_scale_selected = set(self.selected_cells)
        self.canvas.update()

    def select_all(self):
        cfg = self.canvas.grid.config
        self.selected_cells = {
            (c, r) for r in range(cfg.rows) for c in range(cfg.cols)
        }
        self.canvas.cell_scale_selected = set(self.selected_cells)
        self.canvas.update()

    def clear_selection(self):
        self.selected_cells.clear()
        self.canvas.cell_scale_selected = set()
        self.canvas.update()

    def cursor(self):
        return Qt.CursorShape.PointingHandCursor
