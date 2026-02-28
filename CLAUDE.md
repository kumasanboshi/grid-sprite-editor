# CLAUDE.md

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
# 依存インストール
pip install -r requirements.txt

# アプリ起動
python main.py

# exe ビルド
pyinstaller --onefile --windowed main.py
```

## Project Structure
```
grid-sprite-editor/
├── main.py               # エントリーポイント
├── requirements.txt      # 依存パッケージ
├── src/
│   ├── app.py            # QApplication 初期化
│   ├── main_window.py    # メインウィンドウ
│   ├── canvas.py         # 画像描画・編集キャンバス
│   ├── tools/            # ツール実装（選択・移動・消しゴム等）
│   │   ├── rect_select.py
│   │   ├── lasso_select.py
│   │   ├── eraser.py
│   │   └── ...
│   ├── grid.py           # グリッド管理（N×M、セル計算）
│   ├── animation.py      # アニメーションプレビュー
│   ├── history.py        # Undo/Redo 管理
│   └── export.py         # 画像エクスポート
├── docs/
│   ├── SPEC.md           # 機能仕様
│   └── ARCHITECTURE.md   # 技術設計
└── assets/               # アイコン等
```

## Important Files
- `docs/SPEC.md` - 機能仕様・要件定義
- `docs/ARCHITECTURE.md` - 技術設計・データモデル

## Domain Terms
- **スプライトシート（Sprite Sheet）**: 複数のコマ画像を1枚に並べたPNG
- **セル（Cell）**: グリッドで分割された各コマ
- **グリッド（Grid）**: N×M の分割ライン
- **ラッソ選択（Lasso Select）**: 自由形状で範囲選択するツール
- **コマ（Frame）**: アニメーション上の1フレーム＝1セル

## Guidelines
- 不明点は確認してから実装
- 既存のコードスタイルを尊重
- TDD は採用しない。動作確認は手動で行う
- PyQt6 のシグナル/スロット機構を積極的に活用
- 画像操作は Pillow で行い、表示は QPixmap に変換

## ワークフロー

### 基本フロー
```
feature ブランチ → 実装 → 動作確認（python main.py） → PR → マージ
```

### ルール
- **main ブランチへの直接プッシュ禁止** — 必ず feature ブランチを切る
- **PR を作成する** — CodeRabbit の自動レビューを活用、変更履歴がポートフォリオ映えする
- **コミットは小さめに** — 後から巻き戻しやすくする

### コミットメッセージ規則
```
feat: add lasso selection tool
fix: grid line not rendering at edges
refactor: extract canvas drawing logic
docs: update README with screenshots
```

### やらなくていいこと
- テスト（pytest 等）の作成
- 型チェック（mypy）のCI
- 厳密なコードレビュープロセス

## サブエージェント一覧

| エージェント | 用途 |
|-------------|------|
| **Plan** | 実装計画・設計 |
| **Explore** | コードベース調査 |
| **Bash** | git操作、コマンド実行 |
| **general-purpose** | 複雑なマルチステップタスク |
