from __future__ import annotations
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QToolBar, QLabel, QSpinBox, QSlider, QCheckBox,
    QFileDialog, QMessageBox, QGroupBox, QDockWidget,
    QSizePolicy, QColorDialog, QComboBox, QPushButton,
    QDialog, QDialogButtonBox, QFormLayout
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QKeySequence, QColor, QIcon
from .canvas import SpriteCanvas
from .export import export_cells, RESIZE_PRESETS, resize_image


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grid Sprite Editor")
        self.resize(1200, 800)

        self._filepath: str | None = None

        self._canvas = SpriteCanvas()
        self._canvas.image_changed.connect(self._on_image_changed)
        self._canvas.file_dropped.connect(self._on_file_dropped)
        self.setCentralWidget(self._canvas)

        self._build_menu()
        self._build_toolbar()
        self._build_side_panel()
        self._build_status_bar()

    # ------------------------------------------------------------------
    # Menu
    # ------------------------------------------------------------------
    def _build_menu(self):
        mb = self.menuBar()

        # File
        file_menu = mb.addMenu("ファイル(&F)")
        self._act_open = QAction("開く...", self, shortcut=QKeySequence.StandardKey.Open)
        self._act_open.triggered.connect(self._open_file)
        self._act_save = QAction("上書き保存", self, shortcut=QKeySequence.StandardKey.Save)
        self._act_save.triggered.connect(self._save_file)
        self._act_save_as = QAction("名前を付けて保存...", self,
                                     shortcut=QKeySequence("Ctrl+Shift+S"))
        self._act_save_as.triggered.connect(self._save_file_as)
        self._act_resize = QAction("リサイズ...", self)
        self._act_resize.triggered.connect(self._resize_dialog)
        self._act_export = QAction("コマを個別にエクスポート...", self)
        self._act_export.triggered.connect(self._export_cells)
        file_menu.addAction(self._act_open)
        file_menu.addSeparator()
        file_menu.addAction(self._act_save)
        file_menu.addAction(self._act_save_as)
        file_menu.addSeparator()
        file_menu.addAction(self._act_resize)
        file_menu.addSeparator()
        file_menu.addAction(self._act_export)

        # Edit
        edit_menu = mb.addMenu("編集(&E)")
        self._act_undo = QAction("元に戻す", self, shortcut=QKeySequence.StandardKey.Undo)
        self._act_undo.triggered.connect(self._canvas.undo)
        self._act_redo = QAction("やり直し", self, shortcut=QKeySequence.StandardKey.Redo)
        self._act_redo.triggered.connect(self._canvas.redo)
        edit_menu.addAction(self._act_undo)
        edit_menu.addAction(self._act_redo)

        # View
        view_menu = mb.addMenu("表示(&V)")
        self._act_fit = QAction("全体表示", self, shortcut=QKeySequence("Ctrl+0"))
        self._act_fit.triggered.connect(self._canvas.fit_view)
        self._act_zoom_in = QAction("ズームイン", self, shortcut=QKeySequence("Ctrl+="))
        self._act_zoom_in.triggered.connect(lambda: self._zoom_step(1.25))
        self._act_zoom_out = QAction("ズームアウト", self, shortcut=QKeySequence("Ctrl+-"))
        self._act_zoom_out.triggered.connect(lambda: self._zoom_step(0.8))
        view_menu.addAction(self._act_fit)
        view_menu.addAction(self._act_zoom_in)
        view_menu.addAction(self._act_zoom_out)

        # Animation
        anim_menu = mb.addMenu("アニメーション(&A)")
        self._act_preview = QAction("プレビュー...", self)
        self._act_preview.triggered.connect(self._show_animation)
        anim_menu.addAction(self._act_preview)

    # ------------------------------------------------------------------
    # Toolbar
    # ------------------------------------------------------------------
    def _build_toolbar(self):
        tb = QToolBar("ツール")
        tb.setIconSize(QSize(24, 24))
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, tb)

        def tool_action(label: str, tool_name: str, shortcut: str = ""):
            act = QAction(label, self)
            act.setCheckable(True)
            if shortcut:
                act.setShortcut(QKeySequence(shortcut))
            act.triggered.connect(lambda: self._select_tool(tool_name))
            tb.addAction(act)
            return act

        self._tool_actions: dict[str, QAction] = {}
        self._tool_actions["rect"] = tool_action("□ 矩形選択", "rect", "M")
        self._tool_actions["lasso"] = tool_action("⌒ ラッソ選択", "lasso", "L")
        self._tool_actions["eraser"] = tool_action("◯ 消しゴム", "eraser", "E")
        self._tool_actions["cell_swap"] = tool_action("⇄ コマ入れ替え", "cell_swap")

        tb.addSeparator()
        lbl = QLabel("  Alt+ドラッグ\n  = セル移動")
        lbl.setStyleSheet("color: #aaa; font-size: 10px;")
        tb.addWidget(lbl)

        self._select_tool("rect")

    def _select_tool(self, name: str):
        self._canvas.set_tool(name)
        for k, act in self._tool_actions.items():
            act.setChecked(k == name)

    # ------------------------------------------------------------------
    # Side panel
    # ------------------------------------------------------------------
    def _build_side_panel(self):
        dock = QDockWidget("設定", self)
        dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)

        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Grid settings
        grid_group = QGroupBox("グリッド")
        grid_layout = QVBoxLayout(grid_group)

        col_row = QHBoxLayout()
        col_row.addWidget(QLabel("列 (cols):"))
        self._spin_cols = QSpinBox()
        self._spin_cols.setRange(1, 20)
        self._spin_cols.setValue(3)
        self._spin_cols.valueChanged.connect(self._update_grid)
        col_row.addWidget(self._spin_cols)
        grid_layout.addLayout(col_row)

        row_row = QHBoxLayout()
        row_row.addWidget(QLabel("行 (rows):"))
        self._spin_rows = QSpinBox()
        self._spin_rows.setRange(1, 20)
        self._spin_rows.setValue(3)
        self._spin_rows.valueChanged.connect(self._update_grid)
        row_row.addWidget(self._spin_rows)
        grid_layout.addLayout(row_row)

        self._chk_show_grid = QCheckBox("グリッド線表示")
        self._chk_show_grid.setChecked(True)
        self._chk_show_grid.toggled.connect(self._update_grid)
        grid_layout.addWidget(self._chk_show_grid)

        grid_color_row = QHBoxLayout()
        grid_color_row.addWidget(QLabel("  色:"))
        self._btn_grid_color = QPushButton()
        self._grid_line_color = QColor(255, 0, 0)
        self._update_color_button(self._btn_grid_color, self._grid_line_color)
        self._btn_grid_color.setFixedWidth(40)
        self._btn_grid_color.clicked.connect(self._pick_grid_color)
        grid_color_row.addWidget(self._btn_grid_color)
        grid_color_row.addWidget(QLabel("不透明度:"))
        self._slider_grid_alpha = QSlider(Qt.Orientation.Horizontal)
        self._slider_grid_alpha.setRange(10, 255)
        self._slider_grid_alpha.setValue(180)
        self._slider_grid_alpha.valueChanged.connect(self._update_grid)
        grid_color_row.addWidget(self._slider_grid_alpha)
        grid_layout.addLayout(grid_color_row)

        self._chk_show_guides = QCheckBox("中心ガイド線表示")
        self._chk_show_guides.setChecked(True)
        self._chk_show_guides.toggled.connect(self._update_grid)
        grid_layout.addWidget(self._chk_show_guides)

        guide_color_row = QHBoxLayout()
        guide_color_row.addWidget(QLabel("  色:"))
        self._btn_guide_color = QPushButton()
        self._guide_line_color = QColor(0, 180, 255)
        self._update_color_button(self._btn_guide_color, self._guide_line_color)
        self._btn_guide_color.setFixedWidth(40)
        self._btn_guide_color.clicked.connect(self._pick_guide_color)
        guide_color_row.addWidget(self._btn_guide_color)
        guide_color_row.addWidget(QLabel("不透明度:"))
        self._slider_guide_alpha = QSlider(Qt.Orientation.Horizontal)
        self._slider_guide_alpha.setRange(10, 255)
        self._slider_guide_alpha.setValue(120)
        self._slider_guide_alpha.valueChanged.connect(self._update_grid)
        guide_color_row.addWidget(self._slider_guide_alpha)
        grid_layout.addLayout(guide_color_row)

        layout.addWidget(grid_group)

        # Eraser size
        eraser_group = QGroupBox("消しゴム")
        eraser_layout = QVBoxLayout(eraser_group)
        eraser_layout.addWidget(QLabel("ブラシサイズ:"))
        self._eraser_slider = QSlider(Qt.Orientation.Horizontal)
        self._eraser_slider.setRange(2, 100)
        self._eraser_slider.setValue(20)
        self._eraser_slider.valueChanged.connect(self._update_eraser_size)
        eraser_layout.addWidget(self._eraser_slider)
        self._eraser_size_label = QLabel("20px")
        eraser_layout.addWidget(self._eraser_size_label)
        layout.addWidget(eraser_group)

        # Zoom
        zoom_group = QGroupBox("ズーム")
        zoom_layout = QVBoxLayout(zoom_group)
        btn_fit = QPushButton("全体表示")
        btn_fit.clicked.connect(self._canvas.fit_view)
        btn_zoom_in = QPushButton("ズームイン (+)")
        btn_zoom_in.clicked.connect(lambda: self._zoom_step(1.25))
        btn_zoom_out = QPushButton("ズームアウト (-)")
        btn_zoom_out.clicked.connect(lambda: self._zoom_step(0.8))
        zoom_layout.addWidget(btn_fit)
        zoom_layout.addWidget(btn_zoom_in)
        zoom_layout.addWidget(btn_zoom_out)
        layout.addWidget(zoom_group)

        layout.addStretch()

        # Animation preview
        anim_group = QGroupBox("アニメーション")
        anim_layout = QVBoxLayout(anim_group)

        self._anim_label = QLabel()
        self._anim_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._anim_label.setFixedSize(200, 200)
        self._anim_label.setStyleSheet("background: #1a1a1a; border: 1px solid #444;")
        anim_layout.addWidget(self._anim_label)

        anim_ctrl = QHBoxLayout()
        self._btn_anim_play = QPushButton("▶")
        self._btn_anim_play.setFixedWidth(36)
        self._btn_anim_play.clicked.connect(self._toggle_anim)
        anim_ctrl.addWidget(self._btn_anim_play)
        anim_ctrl.addWidget(QLabel("FPS:"))
        self._spin_anim_fps = QSpinBox()
        self._spin_anim_fps.setRange(1, 60)
        self._spin_anim_fps.setValue(8)
        self._spin_anim_fps.valueChanged.connect(self._on_fps_changed)
        anim_ctrl.addWidget(self._spin_anim_fps)
        anim_layout.addLayout(anim_ctrl)

        self._anim_frame_label = QLabel("- / -")
        self._anim_frame_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        anim_layout.addWidget(self._anim_frame_label)

        layout.addWidget(anim_group)

        # Animation state
        from PyQt6.QtCore import QTimer
        self._anim_frames: list = []
        self._anim_current = 0
        self._anim_playing = False
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._anim_next_frame)

        dock.setWidget(panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

    def _update_grid(self):
        cfg = self._canvas.grid.config
        cfg.cols = self._spin_cols.value()
        cfg.rows = self._spin_rows.value()
        cfg.show_grid = self._chk_show_grid.isChecked()
        cfg.show_guides = self._chk_show_guides.isChecked()
        self._anim_rebuild_frames()
        a_grid  = self._slider_grid_alpha.value()
        a_guide = self._slider_guide_alpha.value()
        cfg.line_color  = (self._grid_line_color.red(),  self._grid_line_color.green(),
                           self._grid_line_color.blue(),  a_grid)
        cfg.guide_color = (self._guide_line_color.red(), self._guide_line_color.green(),
                           self._guide_line_color.blue(), a_guide)
        self._canvas.update()

    def _update_color_button(self, btn: QPushButton, color: QColor):
        btn.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #888;")

    def _pick_grid_color(self):
        c = QColorDialog.getColor(self._grid_line_color, self, "グリッド線の色")
        if c.isValid():
            self._grid_line_color = c
            self._update_color_button(self._btn_grid_color, c)
            self._update_grid()

    def _pick_guide_color(self):
        c = QColorDialog.getColor(self._guide_line_color, self, "ガイド線の色")
        if c.isValid():
            self._guide_line_color = c
            self._update_color_button(self._btn_guide_color, c)
            self._update_grid()

    def _update_eraser_size(self, val: int):
        self._eraser_size_label.setText(f"{val}px")
        self._canvas.tools["eraser"].brush_size = val

    def _zoom_step(self, factor: float):
        from PyQt6.QtCore import QPointF
        center = QPointF(self._canvas.width() / 2, self._canvas.height() / 2)
        self._canvas._offset = center - (center - self._canvas._offset) * factor
        self._canvas._zoom *= factor
        self._canvas._zoom = max(0.1, min(32.0, self._canvas._zoom))
        self._canvas.update()

    # ------------------------------------------------------------------
    # Status bar
    # ------------------------------------------------------------------
    def _build_status_bar(self):
        self._status_label = QLabel("画像を開いてください")
        self.statusBar().addWidget(self._status_label)

    def _on_image_changed(self):
        if self._canvas.image:
            w, h = self._canvas.image.size
            self._status_label.setText(f"{w} × {h} px")
        self._anim_rebuild_frames()

    def _anim_rebuild_frames(self):
        """Rebuild animation frames from current image. Called on every image change."""
        from PyQt6.QtGui import QPixmap
        from .canvas import pil_to_qimage
        img = self._canvas.image
        if not img:
            self._anim_frames = []
            self._anim_label.clear()
            self._anim_frame_label.setText("- / -")
            return
        grid = self._canvas.grid
        iw, ih = img.size
        frames = []
        for row in range(grid.config.rows):
            for col in range(grid.config.cols):
                x, y, w, h = grid.cell_rect(iw, ih, col, row)
                cell = img.crop((x, y, x + w, y + h))
                qi = pil_to_qimage(cell)
                frames.append(QPixmap.fromImage(qi))
        self._anim_frames = frames
        # clamp current index
        if self._anim_current >= len(frames):
            self._anim_current = 0
        self._anim_show_frame(self._anim_current)

    def _anim_show_frame(self, idx: int):
        if not self._anim_frames:
            return
        self._anim_current = idx % len(self._anim_frames)
        pix = self._anim_frames[self._anim_current]
        self._anim_label.setPixmap(
            pix.scaled(self._anim_label.size(),
                       Qt.AspectRatioMode.KeepAspectRatio,
                       Qt.TransformationMode.SmoothTransformation)
        )
        total = len(self._anim_frames)
        self._anim_frame_label.setText(f"{self._anim_current + 1} / {total}")

    def _anim_next_frame(self):
        if self._anim_frames:
            self._anim_show_frame((self._anim_current + 1) % len(self._anim_frames))

    def _toggle_anim(self):
        if self._anim_playing:
            self._anim_timer.stop()
            self._anim_playing = False
            self._btn_anim_play.setText("▶")
        else:
            self._anim_timer.start(1000 // self._spin_anim_fps.value())
            self._anim_playing = True
            self._btn_anim_play.setText("⏸")

    def _on_fps_changed(self, val: int):
        if self._anim_playing:
            self._anim_timer.setInterval(1000 // val)

    def _on_file_dropped(self, path: str):
        self._filepath = path
        self.setWindowTitle(f"Grid Sprite Editor — {os.path.basename(path)}")

    # ------------------------------------------------------------------
    # File operations
    # ------------------------------------------------------------------
    def _open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "画像を開く", "", "PNG Files (*.png);;All Files (*)"
        )
        if path:
            self._canvas.load_image(path)
            self._filepath = path
            self.setWindowTitle(f"Grid Sprite Editor — {os.path.basename(path)}")

    def _save_file(self):
        if not self._canvas.image:
            return
        if not self._filepath:
            self._save_file_as()
            return
        self._canvas.image.save(self._filepath)
        self.statusBar().showMessage("保存しました", 2000)

    def _save_file_as(self):
        if not self._canvas.image:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "名前を付けて保存", "", "PNG Files (*.png)"
        )
        if path:
            if not path.lower().endswith(".png"):
                path += ".png"
            self._canvas.image.save(path)
            self._filepath = path
            self.setWindowTitle(f"Grid Sprite Editor — {os.path.basename(path)}")
            self.statusBar().showMessage("保存しました", 2000)

    # ------------------------------------------------------------------
    # Resize
    # ------------------------------------------------------------------
    def _resize_dialog(self):
        if not self._canvas.image:
            return
        dlg = ResizeDialog(self._canvas.image.size, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            w, h = dlg.selected_size()
            self._canvas.history.push(self._canvas.image)
            self._canvas.image = resize_image(self._canvas.image, w, h)
            self._canvas.refresh_pixmap()
            self._canvas.fit_view()
            self._canvas.image_changed.emit()

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------
    def _export_cells(self):
        if not self._canvas.image:
            return
        out_dir = QFileDialog.getExistingDirectory(self, "エクスポート先フォルダ")
        if not out_dir:
            return
        base = os.path.basename(self._filepath) if self._filepath else "sprite.png"
        paths = export_cells(self._canvas.image, self._canvas.grid, out_dir, base)
        QMessageBox.information(self, "エクスポート完了",
                                f"{len(paths)} 枚のPNGを出力しました。\n{out_dir}")

    # ------------------------------------------------------------------
    # Animation
    # ------------------------------------------------------------------
    def _show_animation(self):
        if not self._canvas.image:
            return
        from .animation import AnimationPreviewDialog
        dlg = AnimationPreviewDialog(self._canvas.image, self._canvas.grid, self)
        dlg.exec()


class ResizeDialog(QDialog):
    def __init__(self, current_size: tuple[int, int], parent=None):
        super().__init__(parent)
        self.setWindowTitle("リサイズ")
        layout = QVBoxLayout(self)

        cw, ch = current_size
        layout.addWidget(QLabel(f"現在のサイズ: {cw} × {ch} px"))

        form = QFormLayout()
        self._combo = QComboBox()
        for label, *_ in RESIZE_PRESETS:
            self._combo.addItem(label)
        self._combo.setCurrentIndex(1)  # default 1536
        form.addRow("プリセット:", self._combo)
        layout.addLayout(form)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def selected_size(self) -> tuple[int, int]:
        idx = self._combo.currentIndex()
        _, w, h = RESIZE_PRESETS[idx]
        return w, h
