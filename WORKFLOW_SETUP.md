# 並列開発ワークフロー セットアップ手順

## 概要
- タスクをGitHub Issueで管理
- 各タスクはブランチを切ってworktreeで実施
- PRを作成してCodeRabbitで自動レビュー

## 構成イメージ

```
GitHub Issue #1 → ブランチ feature/issue-1 → worktree: ../work/issue-1/ → PR #1
GitHub Issue #2 → ブランチ feature/issue-2 → worktree: ../work/issue-2/ → PR #2
```

## 手順

### 1. GitHub上でIssueを作成
ブラウザでリポジトリの Issues タブから作成

またはCLI:
```bash
gh issue create --title "タスク名" --body "詳細"
```

並列処理可能なタスクには `parallel-ok` ラベルを付けておくと良い。

### 2. worktreeでブランチを作成
```bash
# Issue番号が #5 の場合
git worktree add ../work/issue-5 -b feature/issue-5
```

### 3. そのディレクトリで作業
```bash
cd ../work/issue-5
# ここでClaude Codeを起動して開発
```

### 4. 完了したらPR作成
```bash
git add .
git commit -m "Issue #5: 機能の説明"
git push -u origin feature/issue-5
```
GitHub上で「Compare & pull request」をクリック → CodeRabbitが自動レビュー

### 5. マージ後、worktreeを削除
```bash
git worktree remove ../work/issue-5
git branch -d feature/issue-5
```

## CodeRabbit設定
1. https://www.coderabbit.ai でGitHubアカウントでサインアップ
2. 対象リポジトリにCodeRabbitをインストール
3. PRを作成すると自動でレビューが走る

※ パブリックリポジトリは無料、プライベートは無料トライアル後に有料

## worktree一覧確認
```bash
git worktree list
```

## 注意事項
- worktreeディレクトリは `.gitignore` に追加推奨（`work/`）
- 各worktreeで別々のClaude Codeセッションを開ける
- mainブランチは常にクリーンな状態を維持
