"""
resize_tool.py
画像を 128x128 / 256x256 / 1536x1536 にリサイズするドラッグ&ドロップツール。
使い方: python resize_tool.py
"""
import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QCheckBox, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PIL import Image


SIZES = [128, 256, 1536]


class DropArea(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Resizer")
        self.setMinimumSize(400, 260)
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        self._label = QLabel("ここに画像をドロップ\n（複数ファイル可）")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setStyleSheet("font-size: 16px; color: #555;")
        layout.addWidget(self._label)

        # サイズチェックボックス
        size_row = QHBoxLayout()
        size_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._checks: dict[int, QCheckBox] = {}
        for size in SIZES:
            cb = QCheckBox(f"{size}×{size}")
            cb.setChecked(True)
            self._checks[size] = cb
            size_row.addWidget(cb)
        layout.addLayout(size_row)

        self._result_label = QLabel("")
        self._result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._result_label.setWordWrap(True)
        self._result_label.setStyleSheet("font-size: 12px; color: #333;")
        layout.addWidget(self._result_label)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        paths = [u.toLocalFile() for u in event.mimeData().urls()]
        image_paths = [p for p in paths if p.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp"))]

        if not image_paths:
            self._result_label.setText("対応画像が見つかりませんでした")
            return

        sizes = [s for s, cb in self._checks.items() if cb.isChecked()]
        if not sizes:
            self._result_label.setText("サイズを1つ以上選択してください")
            return

        ok, ng = [], []
        for path in image_paths:
            try:
                img = Image.open(path).convert("RGBA")
                base, ext = os.path.splitext(path)
                for size in sizes:
                    resized = img.resize((size, size), Image.LANCZOS)
                    out_path = f"{base}_{size}x{size}{ext}"
                    resized.save(out_path)
                ok.append(os.path.basename(path))
            except Exception as e:
                ng.append(f"{os.path.basename(path)}: {e}")

        lines = []
        if ok:
            size_str = " / ".join(f"{s}×{s}" for s in sizes)
            lines.append(f"✓ {len(ok)}ファイル → {size_str} で出力完了")
        if ng:
            lines.append("✗ " + "\n✗ ".join(ng))
        self._result_label.setText("\n".join(lines))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = DropArea()
    w.show()
    sys.exit(app.exec())
