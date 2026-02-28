# AGENTS.md

## Project
<!-- プロジェクト名と簡単な説明 -->
PROJECT_NAME - 説明

## Tech Stack
<!-- 使用技術を記載 -->
- Frontend:
- Backend:
- Database:
- API:

## Key Commands
```bash
# よく使うコマンドを記載
npm start          # 開発サーバー起動
npm run build      # ビルド
npm run test       # テスト実行
npm run lint       # リンター実行
```

## Project Structure
```
src/
├── components/    #
├── pages/         #
├── services/      #
├── hooks/         #
├── types/         #
├── utils/         #
└── constants/     #
```

## Important Files
- `docs/PROJECT.md` - プロジェクト詳細・要件
- `docs/ARCHITECTURE.md` - 技術設計・データモデル
- `docs/CONTRIBUTING.md` - コーディング規約・開発フロー

## Domain Terms
<!-- プロジェクト固有の用語を記載 -->
- **Term1**: 説明
- **Term2**: 説明

## Guidelines
- 不明点は確認してから実装
- 既存のコードスタイルを尊重
- **テスト駆動開発（TDD）を採用**

## Development Workflow
各タスクは以下のステップで進める。問題がなければサブエージェントを使用すること。

| ステップ | 内容 | 担当 |
|---------|------|------|
| 1. 探索 | 関連ファイル調査・仕様確認 | **Exploreエージェント** |
| 2. 計画 | 実装方針策定・テスト設計 | **Planエージェント** |
| 3. 実装 | TDDサイクル（テスト→実装） | 直接実行 |
| 4. 検証 | 実装品質の検証 | **独立サブエージェント** |
| 5. PR作成 | 型チェック・テスト・PR作成 | **Bashエージェント** |
| 6. レビュー | ダブルレビュー・指摘対応 | **サブエージェント + Codex** |
| 7. マージ | PRマージ・ブランチ整理 | **Bashエージェント** |

### サブエージェント一覧
- **Plan**: コードベース探索 + 実装計画の設計
- **Explore**: コードベース探索（調査のみの場合）
- **Bash**: git操作、コマンド実行
- **general-purpose**: 複雑なマルチステップタスク
- **test-designer**: テストケースの設計とレビュー
<!-- プロジェクト固有のエージェントを追加 -->
