# コーディング基準

プロジェクトのコーディング基準です。

## TypeScript

### 型安全性
```typescript
// NG: any型の使用
const data: any = response.data;

// OK: unknown + 型ガード
const data: unknown = response.data;
if (isItem(data)) {
  // data は Item 型として扱える
}
```

### 型定義
- すべての型定義は `src/types/` に集約
- インターフェースは PascalCase
- 型エイリアスも PascalCase
- ユニオン型は明示的に定義

```typescript
// src/types/item.ts
export interface Item {
  id: number;
  name: string;
  // ...
}

export type ItemStatus = 'active' | 'inactive' | 'archived' | 'draft';
```

### Null/Undefined ハンドリング
```typescript
// NG: 暗黙的なnullチェック
const name = item && item.name;

// OK: Optional chaining + Nullish coalescing
const name = item?.name ?? 'Unknown';
```

## React Native

### コンポーネント
- 関数コンポーネントのみ使用（クラスコンポーネント禁止）
- Props はインターフェースで明示的に型定義
- デフォルト値は引数で設定

```typescript
interface ItemCardProps {
  item: Item;
  onPress?: () => void;
}

export const ItemCard: React.FC<ItemCardProps> = ({
  item,
  onPress = () => {}
}) => {
  // ...
};
```

### スタイル
- `StyleSheet.create()` を使用
- インラインスタイルは避ける
- テーマ色は `theme.colors` から取得

```typescript
const styles = StyleSheet.create({
  container: {
    padding: 16,
    backgroundColor: theme.colors.background,
  },
});
```

### Hooks
- カスタムフックは `src/hooks/` に配置
- フック名は `use` プレフィックス
- 依存配列は正確に指定

```typescript
// src/hooks/useItems.ts
export const useItems = () => {
  const [items, setItems] = useState<Item[]>([]);
  // ...
  return { items, loading, error };
};
```

## 状態管理

### Zustand（グローバル状態）
- ストアは `src/store/` に配置
- 1ストア1ファイル
- アクションはストア内に定義

```typescript
// src/store/themeStore.ts
interface ThemeStore {
  isDarkMode: boolean;
  toggleTheme: () => void;
}

export const useThemeStore = create<ThemeStore>((set) => ({
  isDarkMode: false,
  toggleTheme: () => set((state) => ({ isDarkMode: !state.isDarkMode })),
}));
```

### ローカル状態
- コンポーネント固有の状態は `useState`
- 複雑な状態ロジックは `useReducer`
- フォーム状態は React Hook Form（必要に応じて）

## 非同期処理

### エラーハンドリング
```typescript
// OK: try/catch で適切にハンドリング
const fetchItem = async (id: number): Promise<Item | null> => {
  try {
    const response = await api.getItem(id);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch item:', error);
    return null;
  }
};
```

### Loading状態
```typescript
const [loading, setLoading] = useState(false);
const [error, setError] = useState<string | null>(null);

const fetchData = async () => {
  setLoading(true);
  setError(null);
  try {
    // ...
  } catch (e) {
    setError('データの取得に失敗しました');
  } finally {
    setLoading(false);
  }
};
```

## ファイル構成

### 命名規則
| 対象 | 規則 | 例 |
|------|------|-----|
| コンポーネント | PascalCase | `ItemCard.tsx` |
| フック | camelCase + use | `useItems.ts` |
| ユーティリティ | camelCase | `calculator.ts` |
| 定数 | UPPER_SNAKE_CASE | `MAX_COUNT` |
| 型/インターフェース | PascalCase | `Item`, `User` |

### ディレクトリ
- 1ファイル1エクスポートを原則
- 各ディレクトリに `index.ts` で再エクスポート

```typescript
// src/components/index.ts
export { ItemCard } from './ItemCard';
export { UserProfile } from './UserProfile';
```

## コメント

### 必要なコメント
- 複雑なビジネスロジック
- 非自明な実装の理由
- TODO/FIXME

```typescript
// NOTE: APIのレート制限を考慮して遅延を入れている
await delay(100);

// TODO: キャッシュ機能を実装予定
// FIXME: オフライン時にクラッシュする可能性あり
```

### 不要なコメント
- 自明なコード（`// カウントを増やす`）
- 古くなった情報
- コメントアウトされたコード

## Git コミット

```
<type>: <subject>

Type:
- feat: 新機能
- fix: バグ修正
- docs: ドキュメント
- style: フォーマット
- refactor: リファクタリング
- test: テスト
- chore: ビルド、設定

例:
feat: 検索機能を実装
fix: スコア計算のバグを修正
```
