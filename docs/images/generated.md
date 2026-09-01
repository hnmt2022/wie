# イラスト（生成画像）

`scripts/generate_official_images.py` で生成し、採用したものだけをここに保存するフォルダです。ビルドやデプロイのたびに自動生成はしません。

プロンプトの本体（画風と場面）は `scripts/image_presets_official.py` にあります。画風を変えたいときはそのファイルの `COMMON_STYLE_GUIDE` と各 `prompt`（SCENE: …）を編集してください。

## 生成方法

```
python scripts/generate_official_images.py --list
python scripts/generate_official_images.py --model gemini-3-pro-image --only hero-connections.webp
# 候補を複数出して選ぶ場合: --count 3（1枚目は素の名前、2枚目以降は name-2.webp …）
```

認証は `.env`（`GEMINI_API_KEY` もしくは Vertex AI 用の `GOOGLE_CLOUD_PROJECT`）。詳細は `env.example`。

## 優先して用意する画像（初期版）

| ファイル名 | 用途 | 比率 |
| --- | --- | --- |
| `hero-connections.webp` | トップのメインビジュアル | 16:9 |
| `activity-learning.webp` | 学び・セミナー カード | 1:1 |
| `activity-dialogue.webp` | 対話・得意の発見 カード | 1:1 |
| `activity-small-step.webp` | 小さな実践 カード | 1:1 |
| `activity-co-creation.webp` | 仕事・活動づくり カード | 1:1 |
| `project-living-money.webp` | 進行中のプロジェクト | 4:3 |
| `ogp-default.webp` | SNS共有時の画像 | 1.91:1 または 16:9 |

## 追加候補

| ファイル名 | 用途 | 比率 |
| --- | --- | --- |
| `about-possibilities.webp` | Wieについてページ | 4:3 |
| `future-collaboration.webp` | これからの取り組み | 4:3 |

## 共通方針（2026-09 改訂）

- 画風は「フラットな編集イラスト」。細く均一な紺色の線＋平塗り。抽象的な色面だけの絵にはしない。
- 淡い黄色・アイボリー・白を基調に、落ち着いた紺色を主アクセント。補助色に淡い青灰・砂色を少量。
- 簡略化された人物・机・スクリーン・ノートなどで「場面」（学習会、相談、対話など）が読み取れるようにする。
- 写実的（写真的）な人物や、特定の実在イベントの記録に見える表現は避ける。顔は最小限（点目・短い口）にし、特定の実在人物に見せない。
- ピンク・花・ハート・握手・パズル・電球・歯車などの定型表現は使わない。
- 画像内に文字・数字・ロゴ・透かしを生成しない（見出しや文章はHTML側で重ねます）。
- 見出しや短文を重ねられる余白を画面内に残す。

## 差し替え方法

1. 画像を生成・選定し、このフォルダに `<name>.webp` として保存します（`--count` で出した候補から選ぶ場合は、採用する1枚を素の名前にリネーム）。
2. 参照箇所はすでに `.webp` を指しています（`src/index.njk` / `src/about.njk` / `src/_data/projects.json` / `src/_data/future.json` / `src/_data/site.json` の `ogpImagePath`）。同名で上書きすれば `npm run build` で反映されます。
