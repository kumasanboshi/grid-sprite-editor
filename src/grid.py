from dataclasses import dataclass


@dataclass
class GridConfig:
    cols: int = 3
    rows: int = 3
    line_color: tuple[int, int, int, int] = (255, 0, 0, 180)    # RGBA
    guide_color: tuple[int, int, int, int] = (0, 180, 255, 120)  # RGBA center guides
    show_grid: bool = True
    show_guides: bool = True


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
