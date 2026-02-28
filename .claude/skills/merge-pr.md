# /merge-pr - PRをマージしてクリーンアップ

PRをマージし、worktreeを削除します。

## 使い方
```
/merge-pr 7
```

## 実行内容

1. **PRの状態確認**
   ```bash
   gh pr view <番号>
   gh pr checks <番号>
   ```

2. **レビュー結果確認**
   - CodeRabbitのコメントをチェック
   - 重大な指摘がないか確認

3. **マージ実行**
   ```bash
   gh pr merge <番号> --merge --delete-branch
   ```

4. **ローカルクリーンアップ**
   ```bash
   git worktree remove ../work/issue-<番号>
   git fetch --prune
   ```

5. **mainを最新化**
   ```bash
   git checkout main
   git pull
   ```

6. **関連Issueの確認**
   - このPRでブロック解除されたIssueを報告
