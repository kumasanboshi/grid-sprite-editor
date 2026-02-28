# /finish-issue - Issue作業完了・PR作成

現在のworktreeでの作業を完了し、PRを作成します。

## 使い方
```
/finish-issue
```

## 実行内容

1. **変更を確認**
   ```bash
   git status
   git diff
   ```

2. **コミット**
   - 変更内容を分析してコミットメッセージ作成
   - `Closes #<番号>` を含める
   - Co-Authored-By を追加

3. **プッシュ & PR作成**
   ```bash
   git push -u origin feature/issue-<番号>
   gh pr create --title "..." --body "..."
   ```

4. **PR URLを報告**

## PR本文テンプレート
```markdown
## Summary
- 変更内容のサマリー

## Test plan
- [ ] テスト項目

Closes #<番号>
```
