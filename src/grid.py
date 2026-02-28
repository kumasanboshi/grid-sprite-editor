from dataclasses import dataclass


@dataclass
class GridConfig:
    cols: int = 3
    rows: int = 3
    line_color: tuple[int, int, int, int] = (255, 0, 0, 180)    # RGBA
    guide_color: tuple[int, int, int, int] = (0, 180, 255, 120)  # RGBA center guides
    show_grid: bool = True
    show_guides: bool = True
    # User-placed cell ruler lines (relative 0.0-1.0 within each cell)
    h_rulers: list = None   # horizontal lines: list of float (relative Y)
    v_rulers: list = None   # vertical lines:   list of float (relative X)
    ruler_color: tuple[int, int, int, int] = (255, 220, 0, 200)  # RGBA
    show_rulers: bool = True

    def __post_init__(self):
        if self.h_rulers is None:
            self.h_rulers = []
        if self.v_rulers is None:
            self.v_rulers = []


class GridManager:
    def __init__(self, config: GridConfig | None = None):
        self.config = config or GridConfig()

    def cell_rect(self, image_w: int, image_h: int, col: int, row: int) -> tuple[int, int, int, int]:
        """Returns (x, y, w, h) of the cell in image coordinates."""
        cw = image_w // self.config.cols
        ch = image_h // self.config.rows
        x = col * cw
        y = row * ch
        # last cell absorbs remainder
        w = image_w - x if col == self.config.cols - 1 else cw
        h = image_h - y if row == self.config.rows - 1 else ch
        return x, y, w, h

    def cell_at(self, image_w: int, image_h: int, px: int, py: int) -> tuple[int, int] | None:
        """Returns (col, row) for the given pixel position, or None if out of bounds."""
        if px < 0 or py < 0 or px >= image_w or py >= image_h:
            return None
        col = min(px * self.config.cols // image_w, self.config.cols - 1)
        row = min(py * self.config.rows // image_h, self.config.rows - 1)
        return col, row

    def grid_lines(self, image_w: int, image_h: int) -> list[tuple[int, int, int, int]]:
        """Returns list of (x1, y1, x2, y2) for grid lines."""
        lines = []
        cw = image_w // self.config.cols
        ch = image_h // self.config.rows
        for c in range(1, self.config.cols):
            x = c * cw
            lines.append((x, 0, x, image_h))
        for r in range(1, self.config.rows):
            y = r * ch
            lines.append((0, y, image_w, y))
        return lines

    def ruler_lines(self, image_w: int, image_h: int) -> list[tuple[int, int, int, int]]:
        """Returns (x1,y1,x2,y2) for all user-placed ruler lines across all cells."""
        lines = []
        for c in range(self.config.cols):
            for r in range(self.config.rows):
                x, y, w, h = self.cell_rect(image_w, image_h, c, r)
                for rel in self.config.h_rulers:
                    py = y + int(rel * h)
                    lines.append((x, py, x + w, py))
                for rel in self.config.v_rulers:
                    px = x + int(rel * w)
                    lines.append((px, y, px, y + h))
        return lines

    def add_h_ruler(self, rel: float):
        rel = max(0.0, min(1.0, rel))
        if not any(abs(r - rel) < 0.005 for r in self.config.h_rulers):
            self.config.h_rulers.append(rel)

    def add_v_ruler(self, rel: float):
        rel = max(0.0, min(1.0, rel))
        if not any(abs(r - rel) < 0.005 for r in self.config.v_rulers):
            self.config.v_rulers.append(rel)

    def remove_nearest_ruler(self, image_w: int, image_h: int, px: int, py: int, threshold: int = 8):
        """Remove the ruler line nearest to (px, py). Returns True if removed."""
        iw, ih = image_w, image_h
        cell = self.cell_at(iw, ih, px, py)
        if cell is None:
            return False
        c, r = cell
        cx, cy, cw, ch = self.cell_rect(iw, ih, c, r)
        rel_x = (px - cx) / cw if cw else 0
        rel_y = (py - cy) / ch if ch else 0
        best_dist, best_list, best_idx = threshold + 1, None, -1
        for i, rel in enumerate(self.config.h_rulers):
            dist = abs((cy + rel * ch) - py)
            if dist < best_dist:
                best_dist, best_list, best_idx = dist, self.config.h_rulers, i
        for i, rel in enumerate(self.config.v_rulers):
            dist = abs((cx + rel * cw) - px)
            if dist < best_dist:
                best_dist, best_list, best_idx = dist, self.config.v_rulers, i
        if best_list is not None and best_idx >= 0:
            best_list.pop(best_idx)
            return True
        return False

    def guide_lines(self, image_w: int, image_h: int) -> list[tuple[int, int, int, int]]:
        """Returns list of (x1, y1, x2, y2) for center guide lines inside each cell."""
        lines = []
        for c in range(self.config.cols):
            for r in range(self.config.rows):
                x, y, w, h = self.cell_rect(image_w, image_h, c, r)
                cx = x + w // 2
                cy = y + h // 2
                lines.append((cx, y, cx, y + h))   # vertical center
                lines.append((x, cy, x + w, cy))   # horizontal center
        return lines
