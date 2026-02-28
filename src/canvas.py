from __future__ import annotations
import io
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPointF, QRectF, pyqtSignal
from PyQt6.QtGui import (
    QPainter, QPixmap, QImage, QColor, QPen, QPolygonF,
    QMouseEvent, QWheelEvent, QKeyEvent
)
from PIL import Image, ImageChops
from .grid import GridManager, GridConfig
from .history import HistoryManager


def pil_to_qimage(img: Image.Image) -> QImage:
    img_rgba = img.convert("RGBA")
    data = img_rgba.tobytes("raw", "RGBA")
    return QImage(data, img_rgba.width, img_rgba.height, QImage.Format.Format_RGBA8888)


class SpriteCanvas(QWidget):
    image_changed = pyqtSignal()
    file_dropped = pyqtSignal(str)
    viewport_changed = pyqtSignal()  # emits on zoom or pan

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)

        self.image: Image.Image | None = None
        self._pixmap: QPixmap | None = None

        self.grid = GridManager()
        self.history = HistoryManager()

        # view transform
        self._zoom = 1.0
        self._offset = QPointF(0, 0)
        self._pan_start: QPointF | None = None
        self._pan_offset_start: QPointF | None = None

        # selection state
        self.selection_rect: QRectF | None = None
        self.lasso_polygon: QPolygonF | None = None
        self._lasso_snapshot: Image.Image | None = None       # image snapshot before drag
        self._lasso_original_polygon: QPolygonF | None = None  # polygon position before drag

        # cell move preview
        self._cell_move_delta: tuple[int, int] | None = None
        self._cell_move_cell: tuple[int, int] | None = None

        # cell swap highlight
        self.swap_highlight: tuple[int, int] | None = None

        # active tool (set by MainWindow)
        self._tool = None

        # alt key state for cell move shortcut
        self._alt_active = False

        from .tools.rect_select import RectSelectTool
        from .tools.lasso_select import LassoSelectTool
        from .tools.eraser import EraserTool
        from .tools.cell_move import CellMoveTool
        from .tools.cell_swap import CellSwapTool

        self.tools = {
            "rect": RectSelectTool(self),
            "lasso": LassoSelectTool(self),
            "eraser": EraserTool(self),
            "cell_move": CellMoveTool(self),
            "cell_swap": CellSwapTool(self),
        }
        self.set_tool("rect")

    # ------------------------------------------------------------------
    # Tool management
    # ------------------------------------------------------------------
    def set_tool(self, name: str):
        self._tool_name = name
        self._tool = self.tools[name]
        self.setCursor(self._tool.cursor())

    # ------------------------------------------------------------------
    # Image loading
    # ------------------------------------------------------------------
    def load_image(self, path: str):
        self.image = Image.open(path).convert("RGBA")
        self.history.clear()
        self.clear_selection()
        self.refresh_pixmap()
        self.fit_view()
        self.image_changed.emit()

    def refresh_pixmap(self):
        if self.image:
            qi = pil_to_qimage(self.image)
            self._pixmap = QPixmap.fromImage(qi)

    def fit_view(self):
        if not self.image:
            return
        w, h = self.image.size
        scale_x = self.width() / w if w else 1
        scale_y = self.height() / h if h else 1
        self._zoom = min(scale_x, scale_y) * 0.95
        self._offset = QPointF(
            (self.width() - w * self._zoom) / 2,
            (self.height() - h * self._zoom) / 2,
        )
        self.update()
        self.viewport_changed.emit()

    # ------------------------------------------------------------------
    # Coordinate helpers
    # ------------------------------------------------------------------
    def widget_to_image(self, pos: QPointF) -> QPointF:
        return QPointF(
            (pos.x() - self._offset.x()) / self._zoom,
            (pos.y() - self._offset.y()) / self._zoom,
        )

    def image_to_widget(self, pos: QPointF) -> QPointF:
        return QPointF(
            pos.x() * self._zoom + self._offset.x(),
            pos.y() * self._zoom + self._offset.y(),
        )

    # ------------------------------------------------------------------
    # Paint
    # ------------------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(40, 40, 40))

        if not self._pixmap:
            return

        painter.save()
        painter.translate(self._offset)
        painter.scale(self._zoom, self._zoom)

        # checkerboard background to show image boundary and transparency
        iw_cb, ih_cb = self.image.size
        cell = 8
        c1, c2 = QColor(180, 180, 180), QColor(220, 220, 220)
        for cy in range(0, ih_cb, cell):
            for cx in range(0, iw_cb, cell):
                color = c1 if ((cx // cell + cy // cell) % 2 == 0) else c2
                painter.fillRect(cx, cy, min(cell, iw_cb - cx), min(cell, ih_cb - cy), color)

        painter.drawPixmap(0, 0, self._pixmap)

        iw, ih = self.image.size

        # cell move preview overlay
        if self._cell_move_delta and self._cell_move_cell and self.image:
            col, row = self._cell_move_cell
            dx, dy = self._cell_move_delta
            x, y, w, h = self.grid.cell_rect(iw, ih, col, row)
            cropped = self.image.crop((x, y, x + w, y + h))
            qi = pil_to_qimage(cropped)
            pix = QPixmap.fromImage(qi)
            painter.setOpacity(0.7)
            painter.drawPixmap(x + dx, y + dy, pix)
            painter.setOpacity(1.0)

        # grid lines
        if self.grid.config.show_grid:
            r, g, b, a = self.grid.config.line_color
            pen = QPen(QColor(r, g, b, a))
            pen.setWidth(0)
            painter.setPen(pen)
            for x1, y1, x2, y2 in self.grid.grid_lines(iw, ih):
                painter.drawLine(x1, y1, x2, y2)

        # center guide lines
        if self.grid.config.show_guides:
            r, g, b, a = self.grid.config.guide_color
            pen = QPen(QColor(r, g, b, a))
            pen.setWidth(0)
            pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen)
            for x1, y1, x2, y2 in self.grid.guide_lines(iw, ih):
                painter.drawLine(x1, y1, x2, y2)

        # cell swap highlight
        if self.swap_highlight:
            col, row = self.swap_highlight
            x, y, w, h = self.grid.cell_rect(iw, ih, col, row)
            painter.fillRect(x, y, w, h, QColor(255, 255, 0, 60))

        painter.restore()

        # selection overlay (in widget space)
        if self.selection_rect:
            self._draw_selection_rect(painter)
        if self.lasso_polygon and not self.lasso_polygon.isEmpty():
            self._draw_lasso(painter)

    def _draw_selection_rect(self, painter: QPainter):
        r = self.selection_rect
        tl = self.image_to_widget(r.topLeft())
        br = self.image_to_widget(r.bottomRight())
        rect = QRectF(tl, br)
        pen = QPen(QColor(255, 255, 255, 200))
        pen.setWidth(1)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(QColor(100, 150, 255, 30))
        painter.drawRect(rect)

    def _draw_lasso(self, painter: QPainter):
        poly_widget = QPolygonF([
            self.image_to_widget(pt) for pt in self.lasso_polygon
        ])
        pen = QPen(QColor(255, 255, 255, 200))
        pen.setWidth(1)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(QColor(100, 150, 255, 30))
        painter.drawPolygon(poly_widget)

    # ------------------------------------------------------------------
    # Mouse / Wheel / Key events
    # ------------------------------------------------------------------
    def mousePressEvent(self, event: QMouseEvent):
        image_pos = self.widget_to_image(QPointF(event.position()))

        # Pan: right button, middle button, or space+left
        if event.button() in (Qt.MouseButton.RightButton, Qt.MouseButton.MiddleButton) or (
            event.button() == Qt.MouseButton.LeftButton and self._space_held
        ):
            self._pan_start = QPointF(event.position())
            self._pan_offset_start = QPointF(self._offset)
            return

        if event.button() == Qt.MouseButton.LeftButton and self.image:
            # Alt key = cell move shortcut
            if event.modifiers() & Qt.KeyboardModifier.AltModifier:
                self.tools["cell_move"].mouse_press(event, image_pos)
                self._alt_active = True
            else:
                self._tool.mouse_press(event, image_pos)

    def mouseMoveEvent(self, event: QMouseEvent):
        image_pos = self.widget_to_image(QPointF(event.position()))

        if self._pan_start:
            delta = QPointF(event.position()) - self._pan_start
            self._offset = self._pan_offset_start + delta
            self.update()
            self.viewport_changed.emit()
            return

        if self._alt_active:
            self.tools["cell_move"].mouse_move(event, image_pos)
        else:
            self._tool.mouse_move(event, image_pos)

    def mouseReleaseEvent(self, event: QMouseEvent):
        image_pos = self.widget_to_image(QPointF(event.position()))

        if self._pan_start and event.button() in (
            Qt.MouseButton.RightButton,
            Qt.MouseButton.MiddleButton,
            Qt.MouseButton.LeftButton,
        ):
            self._pan_start = None
            self._pan_offset_start = None
            return

        if self._alt_active:
            self.tools["cell_move"].mouse_release(event, image_pos)
            self._alt_active = False
        else:
            self._tool.mouse_release(event, image_pos)

    def wheelEvent(self, event: QWheelEvent):
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        mouse_pos = QPointF(event.position())
        # zoom around mouse position
        self._offset = mouse_pos - (mouse_pos - self._offset) * factor
        self._zoom *= factor
        self._zoom = max(0.1, min(32.0, self._zoom))
        self.update()
        self.viewport_changed.emit()

    _space_held = False

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Space:
            self._space_held = True
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        elif event.key() == Qt.Key.Key_Delete:
            self._delete_selection()
        elif event.key() == Qt.Key.Key_Escape:
            self.clear_selection()

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Space:
            self._space_held = False
            self.setCursor(self._tool.cursor())

    # ------------------------------------------------------------------
    # Selection helpers
    # ------------------------------------------------------------------
    def clear_selection(self):
        self.selection_rect = None
        self.lasso_polygon = None
        self._lasso_snapshot = None
        self.update()

    def _delete_selection(self):
        if not self.image:
            return
        self.history.push(self.image)
        if self.selection_rect:
            from PIL import ImageDraw
            draw = ImageDraw.Draw(self.image)
            r = self.selection_rect
            draw.rectangle([int(r.x()), int(r.y()), int(r.right()), int(r.bottom())],
                           fill=(0, 0, 0, 0))
        elif self.lasso_polygon and not self.lasso_polygon.isEmpty():
            self._erase_lasso_region()
        self.refresh_pixmap()
        self.image_changed.emit()
        self.update()

    def _erase_lasso_region(self):
        from PIL import ImageDraw
        mask = Image.new("L", self.image.size, 0)
        draw = ImageDraw.Draw(mask)
        pts = [(int(p.x()), int(p.y())) for p in self.lasso_polygon]
        if len(pts) >= 3:
            draw.polygon(pts, fill=255)
        r, g, b, a = self.image.split()
        new_a = ImageChops.difference(a, mask)
        self.image = Image.merge("RGBA", (r, g, b, new_a))

    # ------------------------------------------------------------------
    # move_selection_pixels (rect select move commit)
    # ------------------------------------------------------------------
    def move_selection_pixels(self, sx: int, sy: int, sw: int, sh: int, dx: int, dy: int):
        if not self.image:
            return
        self.history.push(self.image)
        region = self.image.crop((sx, sy, sx + sw, sy + sh))
        # erase source
        from PIL import ImageDraw
        draw = ImageDraw.Draw(self.image)
        draw.rectangle([sx, sy, sx + sw, sy + sh], fill=(0, 0, 0, 0))
        # paste at new location (clipped to image)
        self.image.alpha_composite(region, dest=(sx + dx, sy + dy))
        self.refresh_pixmap()
        self.image_changed.emit()
        self.update()

    # ------------------------------------------------------------------
    # Lasso move commit
    # ------------------------------------------------------------------
    def commit_lasso_move(self):
        """Called by LassoSelectTool after dragging."""
        if not self.image or not self.lasso_polygon or not self._lasso_snapshot:
            return
        if self._lasso_original_polygon is None:
            return

        pts_original = [(int(p.x()), int(p.y())) for p in self._lasso_original_polygon]
        pts_current  = [(int(p.x()), int(p.y())) for p in self.lasso_polygon]
        if len(pts_original) < 3 or len(pts_current) < 3:
            return

        from PIL import ImageDraw

        # Compute move delta from polygon centroid
        ox = sum(p[0] for p in pts_original) / len(pts_original)
        oy = sum(p[1] for p in pts_original) / len(pts_original)
        cx = sum(p[0] for p in pts_current)  / len(pts_current)
        cy = sum(p[1] for p in pts_current)  / len(pts_current)
        dx, dy = int(cx - ox), int(cy - oy)

        # 1. Build mask at original polygon position
        orig_mask = Image.new("L", self.image.size, 0)
        ImageDraw.Draw(orig_mask).polygon(pts_original, fill=255)

        # 2. Cut pixels from snapshot preserving original alpha
        #    multiply(alpha, mask): inside polygon = original alpha, outside = 0
        snap_r, snap_g, snap_b, snap_a = self._lasso_snapshot.split()
        cut_alpha = ImageChops.multiply(snap_a, orig_mask)
        cut = Image.merge("RGBA", (snap_r, snap_g, snap_b, cut_alpha))

        # 3. Shift the cut region by (dx, dy)
        shifted = Image.new("RGBA", self.image.size, (0, 0, 0, 0))
        shifted.paste(cut, (dx, dy))

        # 4. Erase original region from current image
        #    multiply(alpha, inverted_mask): inside polygon = 0, outside = original alpha
        img_r, img_g, img_b, img_a = self.image.split()
        inv_mask = ImageChops.invert(orig_mask)
        new_a = ImageChops.multiply(img_a, inv_mask)
        self.image = Image.merge("RGBA", (img_r, img_g, img_b, new_a))

        # 5. Alpha-composite shifted region onto image (preserves transparency)
        self.image = Image.alpha_composite(self.image, shifted)

        # Update snapshot and original polygon to current state for continued dragging
        self._lasso_snapshot = self.image.copy()
        self._lasso_original_polygon = QPolygonF(self.lasso_polygon)
        # Keep lasso_polygon visible so user can drag again; clear with Escape
        self.refresh_pixmap()
        self.image_changed.emit()
        self.update()

    # ------------------------------------------------------------------
    # Cell move apply
    # ------------------------------------------------------------------
    def apply_cell_move(self, cell: tuple[int, int], dx: int, dy: int):
        if not self.image:
            return
        col, row = cell
        iw, ih = self.image.size
        x, y, w, h = self.grid.cell_rect(iw, ih, col, row)

        # crop cell content
        region = self.image.crop((x, y, x + w, y + h))

        # erase cell
        from PIL import ImageDraw
        draw = ImageDraw.Draw(self.image)
        draw.rectangle([x, y, x + w, y + h], fill=(0, 0, 0, 0))

        # paste shifted (clip to cell bounds)
        new_x = x + dx
        new_y = y + dy
        # create cell-sized canvas and paste shifted region
        cell_canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        cell_canvas.alpha_composite(region, dest=(dx, dy))
        self.image.alpha_composite(cell_canvas, dest=(x, y))

        self.refresh_pixmap()
        self.image_changed.emit()
        self.update()

    # ------------------------------------------------------------------
    # Cell swap
    # ------------------------------------------------------------------
    def swap_cells(self, cell_a: tuple[int, int], cell_b: tuple[int, int]):
        if not self.image:
            return
        iw, ih = self.image.size
        ax, ay, aw, ah = self.grid.cell_rect(iw, ih, *cell_a)
        bx, by, bw, bh = self.grid.cell_rect(iw, ih, *cell_b)
        region_a = self.image.crop((ax, ay, ax + aw, ay + ah))
        region_b = self.image.crop((bx, by, bx + bw, by + bh))
        # resize if cells differ in size (non-uniform grids)
        if (aw, ah) != (bw, bh):
            region_a = region_a.resize((bw, bh), Image.LANCZOS)
            region_b = region_b.resize((aw, ah), Image.LANCZOS)
        from PIL import ImageDraw
        draw = ImageDraw.Draw(self.image)
        draw.rectangle([ax, ay, ax + aw, ay + ah], fill=(0, 0, 0, 0))
        draw.rectangle([bx, by, bx + bw, by + bh], fill=(0, 0, 0, 0))
        self.image.alpha_composite(region_b, dest=(ax, ay))
        self.image.alpha_composite(region_a, dest=(bx, by))
        self.refresh_pixmap()
        self.image_changed.emit()
        self.update()

    # ------------------------------------------------------------------
    # Undo / Redo
    # ------------------------------------------------------------------
    def undo(self):
        if self.image and self.history.can_undo():
            self.image = self.history.undo(self.image)
            self.refresh_pixmap()
            self.image_changed.emit()
            self.update()

    def redo(self):
        if self.image and self.history.can_redo():
            self.image = self.history.redo(self.image)
            self.refresh_pixmap()
            self.image_changed.emit()
            self.update()

    # ------------------------------------------------------------------
    # Drag & drop
    # ------------------------------------------------------------------
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile().lower().endswith(".png"):
                event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if path.lower().endswith(".png"):
                self.load_image(path)
                self.file_dropped.emit(path)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.image and self._zoom == 1.0:
            self.fit_view()
