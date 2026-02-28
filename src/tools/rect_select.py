from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QMouseEvent
from .base import BaseTool


class RectSelectTool(BaseTool):
    def __init__(self, canvas):
        super().__init__(canvas)
        self._start: QPointF | None = None
        self._dragging_selection = False
        self._drag_start: QPointF | None = None
        self._drag_origin_rect: QRectF | None = None

    def mouse_press(self, event: QMouseEvent, image_pos: QPointF):
        sel = self.canvas.selection_rect
        if sel and sel.contains(image_pos):
            # start moving existing selection
            self._dragging_selection = True
            self._drag_start = image_pos
            self._drag_origin_rect = QRectF(sel)
        else:
            self.canvas.clear_selection()
            self._start = image_pos
            self._dragging_selection = False

    def mouse_move(self, event: QMouseEvent, image_pos: QPointF):
        if self._dragging_selection and self._drag_start and self._drag_origin_rect:
            dx = image_pos.x() - self._drag_start.x()
            dy = image_pos.y() - self._drag_start.y()
            new_rect = self._drag_origin_rect.translated(dx, dy)
            self.canvas.selection_rect = new_rect
            self.canvas.update()
        elif self._start:
            rect = QRectF(self._start, image_pos).normalized()
            self.canvas.selection_rect = rect
            self.canvas.update()

    def mouse_release(self, event: QMouseEvent, image_pos: QPointF):
        if self._dragging_selection:
            self._commit_move(image_pos)
        self._start = None
        self._dragging_selection = False
        self._drag_start = None
        self._drag_origin_rect = None

    def _commit_move(self, image_pos: QPointF):
        if not self._drag_origin_rect or not self._drag_start:
            return
        dx = int(image_pos.x() - self._drag_start.x())
        dy = int(image_pos.y() - self._drag_start.y())
        if dx == 0 and dy == 0:
            return
        self.canvas.move_selection_pixels(
            int(self._drag_origin_rect.x()), int(self._drag_origin_rect.y()),
            int(self._drag_origin_rect.width()), int(self._drag_origin_rect.height()),
            dx, dy
        )

    def cursor(self):
        return Qt.CursorShape.CrossCursor
