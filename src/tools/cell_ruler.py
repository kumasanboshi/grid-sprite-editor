from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QMouseEvent
from .base import BaseTool


class CellRulerTool(BaseTool):
    """Left-click to place H or V ruler line synced across all cells.
    Right-click to remove nearest ruler line."""

    def __init__(self, canvas):
        super().__init__(canvas)
        self.mode = "H"  # "H" or "V"

    def mouse_press(self, event: QMouseEvent, image_pos: QPointF):
        if not self.canvas.image:
            return
        iw, ih = self.canvas.image.size
        px, py = int(image_pos.x()), int(image_pos.y())
        grid = self.canvas.grid

        if event.button() == Qt.MouseButton.RightButton:
            if grid.remove_nearest_ruler(iw, ih, px, py):
                self.canvas.update()
            return

        cell = grid.cell_at(iw, ih, px, py)
        if cell is None:
            return
        c, r = cell
        cx, cy, cw, ch = grid.cell_rect(iw, ih, c, r)

        if self.mode == "H":
            rel = (py - cy) / ch if ch else 0.5
            grid.add_h_ruler(rel)
        else:
            rel = (px - cx) / cw if cw else 0.5
            grid.add_v_ruler(rel)

        self.canvas.update()

    def cursor(self):
        return Qt.CursorShape.CrossCursor
