import os
from pathlib import Path
from PIL import Image
from .grid import GridManager


def export_cells(image: Image.Image, grid: GridManager, output_dir: str, base_name: str):
    """Export each cell as individual PNG files."""
    iw, ih = image.size
    cfg = grid.config
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    stem = Path(base_name).stem
    exported = []
    for row in range(cfg.rows):
        for col in range(cfg.cols):
            x, y, w, h = grid.cell_rect(iw, ih, col, row)
            cell = image.crop((x, y, x + w, y + h))
            filename = f"{stem}_{row}_{col}.png"
            path = os.path.join(output_dir, filename)
            cell.save(path)
            exported.append(path)
    return exported


RESIZE_PRESETS = [
    ("768 × 768  (1コマ 256×256)", 768, 768),
    ("1536 × 1536  (1コマ 512×512)  ★推奨", 1536, 1536),
    ("1920 × 1920  (1コマ 640×640)", 1920, 1920),
    ("2400 × 2400  (1コマ 800×800)", 2400, 2400),
    ("3072 × 3072  (1コマ 1024×1024)", 3072, 3072),
]


def resize_image(image: Image.Image, width: int, height: int) -> Image.Image:
    return image.resize((width, height), Image.LANCZOS)
