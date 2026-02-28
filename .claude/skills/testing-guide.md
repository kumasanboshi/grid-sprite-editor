# テストガイドライン

プロジェクトのテスト方針とTDDプロセスです。

## TDDサイクル

### RED → GREEN → REFACTOR

```
1. RED: 失敗するテストを書く
   - 期待する動作をテストで表現
   - テストが失敗することを確認

2. GREEN: テストをパスする最小実装
   - 最もシンプルな実装でテストをパス
   - 過剰な実装は避ける

3. REFACTOR: コードを改善
   - テストがパスしたまま品質向上
   - 重複排除、可読性向上
```

### 実践例

```typescript
// 1. RED: 失敗するテストを書く
describe('calculateTotal', () => {
  it('should return 0 when no scores provided', () => {
    const item = createEmptyItem();
    expect(calculateTotal(item)).toBe(0);
  });
});

// 2. GREEN: 最小実装
export const calculateTotal = (item: Item): number => {
  return 0; // まずはハードコード
};

// 3. REFACTOR: 実際のロジックに改善
export const calculateTotal = (item: Item): number => {
  const scores = [
    item.quality_score,
    item.value_score,
    // ...
  ].filter((s): s is number => s !== null);

  if (scores.length === 0) return 0;

  const average = scores.reduce((a, b) => a + b, 0) / scores.length;
  return Math.round(average * 20);
};
```

## テスト対象の優先度

### P0: 必須
| 対象 | 配置場所 | 理由 |
|------|---------|------|
| ビジネスロジック | `src/utils/` | 計算ミスは致命的 |
| データアクセス | `src/services/*Repository` | データ整合性 |

### P1: 推奨
| 対象 | 配置場所 | 理由 |
|------|---------|------|
| カスタムフック | `src/hooks/` | 状態管理の正確性 |
| ユーティリティ | `src/utils/` | 再利用性が高い |

### P2: 必要に応じて
| 対象 | 配置場所 | 理由 |
|------|---------|------|
| UIコンポーネント | `src/components/` | 表示ロジックがある場合 |
| 画面 | `src/screens/` | 複雑なインタラクション |

## テストファイル構成

```
src/
├── __tests__/
│   ├── calculator.test.ts
│   ├── itemRepository.test.ts
│   └── userRepository.test.ts
├── utils/
│   └── calculator.ts
└── services/
    ├── itemRepository.ts
    └── userRepository.ts
```

## テストパターン

### Arrange-Act-Assert (AAA)

```typescript
describe('calculator', () => {
  it('should calculate average of provided scores', () => {
    // Arrange: テストデータを準備
    const item = createItem({
      quality_score: 4,
      value_score: 5,
      usability_score: 3,
    });

    // Act: テスト対象を実行
    const result = calculateTotal(item);

    // Assert: 結果を検証
    expect(result).toBe(80); // (4+5+3)/3 * 20 = 80
  });
});
```

### テストデータのファクトリ関数

```typescript
// テストヘルパー
const createItem = (overrides: Partial<Item> = {}): Item => ({
  id: 1,
  name: 'Test Item',
  created_date: '2024-01-01',
  status: 'active',
  quality_score: null,
  value_score: null,
  usability_score: null,
  design_score: null,
  reliability_score: null,
  total_score: 0,
  description: '',
  is_featured: false,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  ...overrides,
});
```

### 境界値テスト

```typescript
describe('calculateTotal edge cases', () => {
  it('should return 0 when all scores are null', () => {
    const item = createItem(); // すべてnull
    expect(calculateTotal(item)).toBe(0);
  });

  it('should return 100 when all scores are 5', () => {
    const item = createItem({
      quality_score: 5,
      value_score: 5,
      usability_score: 5,
      design_score: 5,
      reliability_score: 5,
    });
    expect(calculateTotal(item)).toBe(100);
  });

  it('should return 20 when all scores are 1', () => {
    const item = createItem({
      quality_score: 1,
      value_score: 1,
    });
    expect(calculateTotal(item)).toBe(20);
  });
});
```

## テスト実行

### コマンド
```bash
# 全テスト実行
npm test

# ウォッチモード
npm test -- --watch

# カバレッジ
npm test -- --coverage

# 特定ファイル
npm test -- calculator
```

### CI/CD連携
- コミット前に `npm test` が成功することを確認
- PRマージ前にすべてのテストがパスしていること

## モック

### 外部依存のモック

```typescript
// 外部APIのモック
jest.mock('../services/api', () => ({
  searchItems: jest.fn().mockResolvedValue({
    results: [{ id: 1, name: 'Test Item' }],
  }),
}));
```

### AsyncStorageのモック

```typescript
jest.mock('@react-native-async-storage/async-storage', () => ({
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
}));
```

## テストの品質基準

### 良いテストの特徴
- [ ] 1テスト1アサーション（原則）
- [ ] テスト名が期待動作を説明している
- [ ] 独立して実行可能（他テストに依存しない）
- [ ] 実行が速い（外部依存はモック）

### 避けるべきパターン
- [ ] 実装詳細のテスト（内部状態を直接検証）
- [ ] 脆いテスト（実装変更で壊れやすい）
- [ ] 遅いテスト（実際のAPI呼び出し等）
- [ ] フレーキーなテスト（たまに失敗する）
