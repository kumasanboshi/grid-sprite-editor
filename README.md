# Project Template

AIエージェント対応のプロジェクトテンプレート。

## 含まれるファイル

| ファイル | 用途 |
|----------|------|
| `CLAUDE.md` | Claude Code用の設定（要カスタマイズ） |
| `AGENTS.md` | 他AIエージェント用（Codex, Cursor等） |
| `WORKFLOW_SETUP.md` | Issue + worktree + PR のワークフロー説明 |
| `.gitignore` | 汎用的な除外設定 |
| `.claude/settings.local.json` | Claude Code権限設定 |
| `docs/CONTRIBUTING.md` | Git規約・開発フロー |

## 使い方

### 1. このテンプレートから新規リポジトリ作成
```bash
gh repo create my-new-project --template kumasanboshi/project-template
```

または GitHub上で「Use this template」ボタン

### 2. CLAUDE.md / AGENTS.md をカスタマイズ
プロジェクト固有の情報を記入：
- プロジェクト名・説明
- 技術スタック
- コマンド
- ディレクトリ構造
- ドメイン用語

### 3. 必要に応じてdocsを追加
- `docs/PROJECT.md` - プロジェクト詳細
- `docs/ARCHITECTURE.md` - 技術設計

## AIエージェント対応

### Claude Code
`CLAUDE.md` を自動で読み込み

### OpenAI Codex
`AGENTS.md` を自動で読み込み

### Cursor / Zed / その他
`AGENTS.md` または同等のファイルを参照

## CodeRabbit設定（推奨）

1. https://www.coderabbit.ai でサインアップ
2. リポジトリにインストール
3. PR作成時に自動レビュー

## ライセンス
MIT
