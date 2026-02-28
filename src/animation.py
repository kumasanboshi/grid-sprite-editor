from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QSpinBox, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QImage
from PIL import Image
from .canvas import pil_to_qimage
from .grid import GridManager


class AnimationPreviewDialog(QDialog):
    def __init__(self, image: Image.Image, grid: GridManager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Animation Preview")
        self.setMinimumSize(400, 480)

        self._image = image
        self._grid = grid
        self._frames: list[QPixmap] = []
        self._current = 0
        self._playing = False

        self._build_frames()
        self._setup_ui()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._next_frame)

    def _build_frames(self):
        cfg = self._grid.config
        iw, ih = self._image.size
        self._frames = []
        for row in range(cfg.rows):
            for col in range(cfg.cols):
                x, y, w, h = self._grid.cell_rect(iw, ih, col, row)
                cell = self._image.crop((x, y, x + w, y + h))
                qi = pil_to_qimage(cell)
                self._frames.append(QPixmap.fromImage(qi))

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        self._label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self._label.setMinimumSize(300, 300)
        self._label.setStyleSheet("background: #222;")
        layout.addWidget(self._label)

        info_layout = QHBoxLayout()
        self._frame_label = QLabel("Frame: 1 / {}".format(len(self._frames)))
        info_layout.addWidget(self._frame_label)
        layout.addLayout(info_layout)

        ctrl_layout = QHBoxLayout()
        self._btn_prev = QPushButton("◀")
        self._btn_play = QPushButton("▶ Play")
        self._btn_next = QPushButton("▶")
        self._btn_prev.clicked.connect(self._prev_frame_manual)
        self._btn_play.clicked.connect(self._toggle_play)
        self._btn_next.clicked.connect(lambda: self._next_frame(manual=True))
        ctrl_layout.addWidget(self._btn_prev)
        ctrl_layout.addWidget(self._btn_play)
        ctrl_layout.addWidget(self._btn_next)
        layout.addLayout(ctrl_layout)

        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel("FPS:"))
        self._fps_spin = QSpinBox()
        self._fps_spin.setRange(1, 60)
        self._fps_spin.setValue(8)
        fps_layout.addWidget(self._fps_spin)

        self._loop_check = QCheckBox("Loop")
        self._loop_check.setChecked(True)
        fps_layout.addWidget(self._loop_check)
        layout.addLayout(fps_layout)

        self._show_frame(0)

    def _show_frame(self, idx: int):
        if not self._frames:
            return
        self._current = idx % len(self._frames)
        pix = self._frames[self._current]
        self._label.setPixmap(
            pix.scaled(self._label.size(), Qt.AspectRatioMode.KeepAspectRatio,
                       Qt.TransformationMode.SmoothTransformation)
        )
        self._frame_label.setText(f"Frame: {self._current + 1} / {len(self._frames)}")

    def _next_frame(self, manual=False):
        next_idx = self._current + 1
        if next_idx >= len(self._frames):
            if self._loop_check.isChecked():
                next_idx = 0
            else:
                self._stop()
                return
        self._show_frame(next_idx)

    def _prev_frame_manual(self):
        self._show_frame(self._current - 1)

    def _toggle_play(self):
        if self._playing:
            self._stop()
        else:
            self._playing = True
            self._btn_play.setText("⏸ Pause")
            self._timer.start(1000 // self._fps_spin.value())

    def _stop(self):
        self._playing = False
        self._timer.stop()
        self._btn_play.setText("▶ Play")
