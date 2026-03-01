from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QMouseEvent
from .base import BaseTool

# Handle indices: 0=TL 1=T 2=TR 3=R 4=BR 5=B 6=BL 7=L
HANDLE_SIZE = 8  # pixels in widget space


def _handle_rects(rect: QRectF, zoom: float) -> list[QRectF]:
    """Return 8 handle rects in IMAGE coordinates around the given rect."""
    hs = HANDLE_SIZE / zoom / 2
    cx = rect.center().x()
    cy = rect.center().y()
    l, t, r, b = rect.left(), rect.top(), rect.right(), rect.bottom()
    centers = [
        (l, t), (cx, t), (r, t),
        (r, cy),
        (r, b), (cx, b), (l, b),
        (l, cy),
    ]
    return [QRectF(x - hs, y - hs, hs * 2, hs * 2) for x, y in centers]


_RESIZE_CURSORS = [
    Qt.CursorShape.SizeFDiagCursor,  # TL
    Qt.CursorShape.SizeVerCursor,    # T
    Qt.CursorShape.SizeBDiagCursor,  # TR
    Qt.CursorShape.SizeHorCursor,    # R
    Qt.CursorShape.SizeFDiagCursor,  # BR
    Qt.CursorShape.SizeVerCursor,    # B
    Qt.CursorShape.SizeBDiagCursor,  # BL
    Qt.CursorShape.SizeHorCursor,    # L
]


class RectSelectTool(BaseTool):
    def __init__(self, canvas):
        super().__init__(canvas)
        self._start: QPointF | None = None
        self._dragging_selection = False
        self._drag_start: QPointF | None = None
        self._drag_origin_rect: QRectF | None = None
        self._resize_handle: int | None = None   # 0-7
        self._resize_origin_rect: QRectF | None = None
        self._copy_mode: bool = False

    def _get_handle_at(self, image_pos: QPointF) -> int | None:
        sel = self.canvas.selection_rect
        if not sel:
            return None
        for i, hr in enumerate(_handle_rects(sel, self.canvas._zoom)):
            if hr.contains(image_pos):
                return i
        return None

    def mouse_press(self, event: QMouseEvent, image_pos: QPointF):
        sel = self.canvas.selection_rect

        # Check resize handle first
        handle = self._get_handle_at(image_pos)
        if handle is not None:
            self._resize_handle = handle
            self._resize_origin_rect = QRectF(sel)
            self._drag_start = image_pos
            return

        if sel and sel.contains(image_pos):
            self._dragging_selection = True
            self._copy_mode = bool(event.modifiers() & Qt.KeyboardModifier.ControlModifier)
            self._drag_start = image_pos
            self._drag_origin_rect = QRectF(sel)
        else:
            self.canvas.clear_selection()
            self._start = image_pos
            self._dragging_selection = False

    def mouse_move(self, event: QMouseEvent, image_pos: QPointF):
        # Resize
        if self._resize_handle is not None and self._drag_start and self._resize_origin_rect:
            self.canvas.selection_rect = self._calc_resize(image_pos)
            self.canvas.update()
            return

        # Move
        if self._dragging_selection and self._drag_start and self._drag_origin_rect:
            dx = image_pos.x() - self._drag_start.x()
            dy = image_pos.y() - self._drag_start.y()
            self.canvas.selection_rect = self._drag_origin_rect.translated(dx, dy)
            self.canvas.update()
            return

        # Draw new
        if self._start:
            self.canvas.selection_rect = QRectF(self._start, image_pos).normalized()
            self.canvas.update()
            return

        # Cursor hint
        handle = self._get_handle_at(image_pos)
        if handle is not None:
            self.canvas.setCursor(_RESIZE_CURSORS[handle])
        elif sel := self.canvas.selection_rect:
            if sel.contains(image_pos):
                self.canvas.setCursor(Qt.CursorShape.SizeAllCursor)
            else:
                self.canvas.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.canvas.setCursor(Qt.CursorShape.CrossCursor)

    def mouse_release(self, event: QMouseEvent, image_pos: QPointF):
        if self._resize_handle is not None and self._resize_origin_rect:
            new_rect = self._calc_resize(image_pos)
            if new_rect.width() > 1 and new_rect.height() > 1:
                self._commit_resize(self._resize_origin_rect, new_rect)
            self._resize_handle = None
            self._resize_origin_rect = None
            self._drag_start = None
            return

        if self._dragging_selection:
            self._commit_move(image_pos)

        self._start = None
        self._dragging_selection = False
        self._drag_start = None
        self._drag_origin_rect = None
        self._copy_mode = False

    def _calc_resize(self, image_pos: QPointF) -> QRectF:
        r = QRectF(self._resize_origin_rect)
        h = self._resize_handle
        x = image_pos.x()
        y = image_pos.y()
        if h in (0, 6, 7):   r.setLeft(min(x, r.right() - 1))
        if h in (2, 3, 4):   r.setRight(max(x, r.left() + 1))
        if h in (0, 1, 2):   r.setTop(min(y, r.bottom() - 1))
        if h in (4, 5, 6):   r.setBottom(max(y, r.top() + 1))
        return r

    def _commit_move(self, image_pos: QPointF):
        if not self._drag_origin_rect or not self._drag_start:
            return
        dx = int(image_pos.x() - self._drag_start.x())
        dy = int(image_pos.y() - self._drag_start.y())
        if dx == 0 and dy == 0:
            return
        if self._copy_mode:
            self.canvas.copy_selection_pixels(
                int(self._drag_origin_rect.x()), int(self._drag_origin_rect.y()),
                int(self._drag_origin_rect.width()), int(self._drag_origin_rect.height()),
                dx, dy
            )
        else:
            self.canvas.move_selection_pixels(
                int(self._drag_origin_rect.x()), int(self._drag_origin_rect.y()),
                int(self._drag_origin_rect.width()), int(self._drag_origin_rect.height()),
                dx, dy
            )

    def _commit_resize(self, orig: QRectF, new: QRectF):
        self.canvas.resize_selection_pixels(
            int(orig.x()), int(orig.y()), int(orig.width()), int(orig.height()),
            int(new.x()),  int(new.y()),  int(new.width()),  int(new.height()),
        )

    def cursor(self):
        return Qt.CursorShape.CrossCursor
