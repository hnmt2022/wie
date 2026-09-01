# Wie 公式サイト

市民活動団体「Wie」の公式サイトです。[Eleventy](https://www.11ty.dev/)（11ty）を使った静的サイトで、GitHub Pages + GitHub Actionsで公開する想定です。

## 技術構成

- 静的サイトジェネレーター: Eleventy 2系（Nunjucksテンプレート）
- 外部UIライブラリなし（プレーンCSS / 最小限のバニラJS）
- ページごとに実HTMLファイルを出力するため、下層ページを直接開いたり再読み込みしても404になりません（SPAのクライアントサイドルーティングに依存しません）
- コンテンツ（活動実績・お知らせ・外部リンク等）は `src/_data/*.json` で管理

## セットアップ

```bash
npm install
npm run dev     # http://localhost:8080 でプレビュー
npm run build   # _site/ に本番ビルドを出力
```

## サイト構成（初期版）

| URL | テンプレート | 役割 |
| --- | --- | --- |
| `/` | `src/index.njk` | トップ。概要・現在の活動・参加への入口 |
| `/about/` | `src/about.njk` | 理念・背景・目指す社会・団体概要 |
| `/activities/` | `src/activities.njk` | 現在行っている活動と実績一覧 |
| `/projects/` | `src/projects.njk` | 進行中のプロジェクトと外部LPへの導線 |
| `/future/` | `src/future.njk` | 少し先に取り組みたいテーマ（検討中・準備中を明記） |
| `/join/` | `src/join.njk` | 参加・協力・連携への入口 |
| `/news/` | `src/news.njk` | お知らせ一覧 |
| `/contact/` | `src/contact.njk` | 目的別の問い合わせ先 |
| `/privacy/` | `src/privacy.njk` | プライバシーポリシー |
| `/404.html` | `src/404.njk` | GitHub Pages用の404ページ |

複雑な下層階層は作らず、初期版はこの構成のみです。

## コンテンツの編集

すべて `src/_data/` 配下のJSONファイルを編集するだけで反映されます（テンプレートの変更は不要）。

| ファイル | 内容 |
| --- | --- |
| `src/_data/site.json` | サイト名・タグライン・ロゴ・SNS・問い合わせ先など全体設定 |
| `src/_data/links.json` | 外部リンク3種（後述） |
| `src/_data/pillars.json` | トップ/活動内容ページの「現在の活動」4カード |
| `src/_data/activities.json` | 「最近の活動・実績」の一覧（日付・人数は未確定のため項目自体を持たせていません） |
| `src/_data/projects.json` | 「進行中のプロジェクト」ページの内容 |
| `src/_data/future.json` | 「これからの取り組み」3テーマ |
| `src/_data/news.json` | お知らせ一覧。空配列 `[]` の間は「現在、お知らせは準備中です」と表示されます |
| `src/_data/contactCategories.json` | お問い合わせページの目的別カテゴリ |

### 活動実績を追加する

`src/_data/activities.json` に項目を追加します。

```json
{ "id": "kesai-example", "title": "○○に関する学習会", "category": "税金", "image": null }
```

写真がある場合は `public/images/activities/` にファイルを置き、`"image"` をそのファイル名に変更してください。

### お知らせを追加する

`src/_data/news.json` に項目を追加します（`url` は任意）。

```json
{ "date": "2026-09-01", "title": "○○を開催しました", "url": null }
```

架空の日付・件数は入れないでください。確定した情報のみ追加します。

## 外部LP・noteのURLを設定する

`src/_data/links.json` の3つの値を編集してください。

```json
{
  "NOTE_URL": "https://note.com/xxxx",
  "MONEY_CONSULTATION_LP_URL": "https://xxxx",
  "MONITORING_SERVICE_LP_URL": "https://xxxx"
}
```

値が `null` の間は、該当ボタンが自動的に「準備中」の非活性表示になります（架空のURLへは遷移しません）。外部リンクは新しいタブで開き、スクリーンリーダー向けに「外部サイトへ移動します」の案内を付与しています。

## 画像の運用

3種類の画像を役割に応じて使い分けます。**現時点ではいずれも未配置のため、レイアウトを崩さないプレースホルダーが表示されます。**

| フォルダ | 用途 | 詳細 |
| --- | --- | --- |
| `public/images/activities/` | 実際の活動写真 | [docs/images/activities.md](docs/images/activities.md) |
| `public/images/character/` | Wieちゃん（キャラクター） | [docs/images/character.md](docs/images/character.md) |
| `public/images/generated/` | 抽象イラスト（生成画像） | [docs/images/generated.md](docs/images/generated.md) |

画像生成には `scripts/generate_official_images.py` を使います（「Wie for Life」LP用スクリプトとは別ファイルとして分離しています）。

- 認証情報（プロジェクトID・リージョン・サービスアカウントキー）は `.env`（Git管理対象外）にのみ置いてください。`env.example` をコピーして使用します。
- 認証情報が未設定の場合、スクリプトは生成を実行せず、必要な設定を案内して終了します。
- `call_image_api()` は雛形（未実装）です。実際に使用するVertex AI / Gemini画像生成SDKに合わせて実装してください。
- ビルドやデプロイのたびに自動生成はしません。手動で少数だけ生成し、採用したものだけを `public/images/generated/` に保存してください。
- 実行するたびに、モデル名・プロンプト・出力ファイル名を `scripts/generation_log/` にJSONで記録します。

## GitHub Pagesへの公開手順

1. このリポジトリをGitHubに作成し、push します。
2. GitHubリポジトリの **Settings > Pages** で、Source を **GitHub Actions** に設定します。
3. `main` ブランチにpushすると `.github/workflows/deploy.yml` が自動的にビルド・公開します（`workflow_dispatch` で手動実行も可能）。
4. 公開URLは以下のいずれかになります。
   - プロジェクトページ: `https://<owner>.github.io/<repo>/`
   - ユーザー/組織ページ（リポジトリ名が `<owner>.github.io` の場合）: `https://<owner>.github.io/`

ワークフロー内で `PATH_PREFIX` を自動判定しており、内部リンクはすべて `url` フィルタ経由で組み立てているため、どちらのURL形式でもリンク切れは発生しません。

## 独自ドメインを後から接続する方法

1. `public/CNAME` ファイルを作成し、1行だけ独自ドメイン（例: `www.example.jp`）を記載します。
2. GitHubリポジトリの **Settings > Pages** で、Custom domainに同じドメインを設定します。
3. ワークフローは `public/CNAME` の有無を見て、独自ドメイン利用時は自動的に `PATH_PREFIX` を `/` にします（手動での変更は不要です）。
4. DNS側でGitHub Pages向けのレコード（CNAME等）を設定してください。

## 実装後の確認結果

- `npm run build` がエラーなく完了することを確認済みです。
- 全ページ（`/`, `/about/`, `/activities/`, `/projects/`, `/future/`, `/join/`, `/news/`, `/contact/`, `/privacy/`, `/404.html`）が出力されることを確認済みです。
- 内部リンクはすべてEleventyの `url` フィルタ経由のため、`PATH_PREFIX` を変えてもリンク切れが起きません。
- 外部リンク（note / 相談LP / 見守りLP）は未設定の間、架空URLへ遷移せず「準備中」表示になることを確認済みです。

## 現時点でプレースホルダーになっている情報（要確認事項）

- 団体の正式名称・法人格・所在地・電話番号・メールアドレス（`src/_data/site.json` の `contactEmail` / `contactFormUrl` / `orgType` / `address` / `phone`）
- お問い合わせの受付方法（メール or フォーム）
- 活動写真（`public/images/activities/`）
- Wieちゃんの正式画像（`public/images/character/`）
- 抽象イラスト（`public/images/generated/`）
- 外部LP・noteの実URL（`src/_data/links.json`）
- お知らせ（`src/_data/news.json` は空配列）
- ロゴ画像（`src/_data/site.json` の `logoPath`。未設定時はテキストロゴ「Wie」を表示）
- OGP画像（`src/_data/site.json` の `ogpImagePath`。未設定時は `og:image` タグ自体を出力しません）
- `src/_data/activities.json` の各項目について、講師が個人として行う専門業務（税理士業務など）とWieの団体活動としての開催が、それぞれ明確に区別できているかの確認（区別が曖昧なまま公開ページに注意書きを出すより、掲載前にこのファイル側で確認する運用にしています）

これらは会員登録・人材データベース・マッチング・案件管理・顧客管理などのシステムと同様、今回のスコープには含めていません。
