# AGENTS.md

## Project
grid-sprite-editor - スプライトシート画像エディター（Windows デスクトップアプリ）

ChatGPT 等で生成した N×M グリッドのスプライトシート PNG を修正・編集するためのツール。

## Tech Stack
- Language: Python 3.11+
- UI: PyQt6
- Image: Pillow (PIL)
- Distribution: PyInstaller（Windows exe）

## Key Commands
```bash
pip install -r requirements.txt   # 依存インストール
python main.py                     # アプリ起動
pyinstaller --onefile --windowed main.py  # exeビルド
```

## Project Structure
```
grid-sprite-editor/
├── main.py
├── requirements.txt
├── src/
│   ├── main_window.py
│   ├── canvas.py
│   ├── tools/
│   ├── grid.py
│   ├── animation.py
│   ├── history.py
│   └── export.py
└── docs/
    ├── SPEC.md
    └── ARCHITECTURE.md
```

## Important Files
- `docs/SPEC.md` - 機能仕様・要件定義
- `docs/ARCHITECTURE.md` - 技術設計

## Domain Terms
- **スプライトシート**: 複数コマを1枚に並べたPNG
- **セル**: グリッドで分割された各コマ
- **グリッド**: N×M の分割ライン
- **ラッソ選択**: 自由形状の範囲選択

## Guidelines
- 不明点は確認してから実装
- 既存のコードスタイルを尊重
- TDD は採用しない

## Development Workflow

| ステップ | 内容 |
|---------|------|
| 1. 探索 | 関連ファイル調査・仕様確認 |
| 2. 計画 | 実装方針策定 |
| 3. 実装 | コーディング |
| 4. 確認 | `python main.py` で動作確認 |
| 5. PR | `gh pr create` でPR作成 |
| 6. マージ | レビュー後マージ |
