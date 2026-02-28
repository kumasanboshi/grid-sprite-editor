from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QMouseEvent, QPolygonF
from .base import BaseTool


class LassoSelectTool(BaseTool):
    def __init__(self, canvas):
        super().__init__(canvas)
        self._points: list[QPointF] = []
        self._dragging_selection = False
        self._drag_start: QPointF | None = None

    def mouse_press(self, event: QMouseEvent, image_pos: QPointF):
        if self.canvas.lasso_polygon and self._polygon_contains(self.canvas.lasso_polygon, image_pos):
            self._dragging_selection = True
            self._drag_start = image_pos
        else:
            self.canvas.clear_selection()
            self._points = [image_pos]
            self._dragging_selection = False

    def mouse_move(self, event: QMouseEvent, image_pos: QPointF):
        if self._dragging_selection and self._drag_start:
            dx = image_pos.x() - self._drag_start.x()
            dy = image_pos.y() - self._drag_start.y()
            self.canvas.lasso_polygon = QPolygonF(
                [QPointF(p.x() + dx, p.y() + dy) for p in self.canvas.lasso_polygon]
            )
            self._drag_start = image_pos
            self.canvas.update()
        elif self._points:
            self._points.append(image_pos)
            self.canvas.lasso_polygon = QPolygonF(self._points)
            self.canvas.update()

    def mouse_release(self, event: QMouseEvent, image_pos: QPointF):
        if self._dragging_selection:
            self.canvas.commit_lasso_move()
        elif len(self._points) > 2:
            self._points.append(self._points[0])  # close polygon
            self.canvas.lasso_polygon = QPolygonF(self._points)
            self.canvas.update()
        self._points = []
        self._dragging_selection = False
        self._drag_start = None

    def _polygon_contains(self, poly: QPolygonF, pt: QPointF) -> bool:
        return poly.containsPoint(pt, Qt.FillRule.OddEvenFill)

    def cursor(self):
        return Qt.CursorShape.CrossCursor
