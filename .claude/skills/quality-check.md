# /quality-check - 品質チェック

コード変更後の品質を5段階で自動検証します。

## 使い方
```
/quality-check
/quality-check src/services
```

## 5段階チェックフロー

### Phase 1: TypeScript型チェック
```bash
npx tsc --noEmit
```
- 型エラーがないことを確認
- `any` 型の使用がないことを確認

### Phase 2: 構造検証
- ディレクトリ構造が Claude.md に準拠しているか
- 命名規則の遵守:
  - コンポーネント: PascalCase
  - 関数: camelCase
  - 定数: UPPER_SNAKE_CASE
  - 型/インターフェース: PascalCase
- 未使用のimport/exportがないか

### Phase 3: テスト実行
```bash
npm test
```
- 全テストがパスすることを確認
- 新規ロジックにはテストが追加されているか

### Phase 4: 型安全性チェック
- `any` 型の使用禁止（`unknown` + 型ガードを使用）
- null/undefined の適切なハンドリング
- 型アサーション（as）の最小化

### Phase 5: 設計準拠チェック
- Requirements.md の仕様に準拠
- Claude.md のコーディング規約に準拠
- 既存パターンとの一貫性

## 判定基準

### approved（コミット可能）
- 全Phaseでエラー0
- 警告のみの場合は許容

### blocked（修正必要）
- いずれかのPhaseでエラーあり
- 修正後、再度 /quality-check を実行

## 出力形式

```markdown
## 品質チェック結果

### Phase 1: TypeScript型チェック
- [ ] 型エラー: 0件
- [ ] any型使用: 0件

### Phase 2: 構造検証
- [ ] ディレクトリ構造: OK
- [ ] 命名規則: OK

### Phase 3: テスト実行
- [ ] テスト結果: 全パス (X/X)

### Phase 4: 型安全性
- [ ] 型安全性: OK

### Phase 5: 設計準拠
- [ ] Requirements.md準拠: OK
- [ ] Claude.md準拠: OK

### 判定: approved / blocked
```

## 自動修正対象

以下は自動で修正を試みる:
- 未使用import の削除
- フォーマット（インデント、セミコロン）
- 型注釈の追加（推論可能な場合）

## 手動対応が必要

以下は人間の判断が必要:
- ビジネスロジックの修正
- テストの正確性確認
- アーキテクチャに関わる変更
