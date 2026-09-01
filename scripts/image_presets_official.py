"""
Wie 公式HP用の画像生成プリセット定義。

方針（2026-09 改訂）:
  以前の「抽象的な色面のみ・人物を描かない」方針は、意味の伝わりにくい絵に
  なりがちだったため見直しました。現在は「フラットな編集イラスト」で、
  簡略化された人物・机・スクリーン・ノートなど “場面” が読み取れる絵を作ります。
  ただし写真的な人物や、特定の実在イベントの記録に見える表現は避けます。

  実際の生成呼び出しは generate_official_images.py 側で行います。
  このファイルはプリセット（プロンプトの共通方針とサイズ）だけを持ちます。
"""

# すべてのカットで一字一句同じにして画風を揃える共通スタイル指定。
COMMON_STYLE_GUIDE = (
    "Flat editorial vector illustration for a Japanese civic organization's "
    "website.\n\n"
    "STYLE (keep identical across every image):\n"
    "- Flat vector shapes with thin, even navy (#223350) linework. No sketchy, "
    "wobbly or single-continuous-line style.\n"
    "- Limited palette: pale yellow (#fbf3da), ivory and white as the base; one "
    "calm navy (#223350) as the main accent; small amounts of soft blue-grey "
    "(#d3e3ea) and warm sand (#ece2c8) as support tones only.\n"
    "- Flat fills. No photographic texture, no paper grain, no heavy gradients; "
    "at most one soft shadow shape per object.\n"
    "- Simplified people are welcome: clean geometric bodies, minimal faces "
    "(small dot eyes, a short calm mouth or none). Never photorealistic, never a "
    "recognisable real individual. Show a natural mix of ages, builds and hair; "
    "calm, relaxed postures; people treated as equals.\n"
    "- Medium detail: the scene must read instantly (a learning session, a "
    "conversation, a desk), but keep every shape simple.\n"
    "- Gentle straight-on or slightly elevated three-quarter view. Warm, "
    "trustworthy, adult. Not childish, not glossy-corporate, not a charity-pity "
    "tone, not a pink or floral feminine cliche.\n"
    "- Leave a clearly empty, calm area in the frame where the website can "
    "overlay a heading or a short paragraph.\n\n"
    "COMPOSITION & MEANING:\n"
    "- The name Wie is 'we' with an 'i' inside it: the individual sits within "
    "the collective. Reflect this. When an image has a clear main person, place "
    "them near the centre and show them as part of the scene around them - "
    "everyday society and its activities surrounding them, with a few thin navy "
    "lines linking them in. The message: everyone is already within society, "
    "and good connections let them take an active part - not a lone figure "
    "standing apart.\n"
    "- When a single main person is shown, make her a woman (the organisation's "
    "main focus is women who lack good work opportunities), and still include a "
    "natural mix of other ages and genders in the surrounding scene.\n\n"
    "NEVER:\n"
    "- No text, letters, numbers, logos, watermarks or UI labels anywhere in "
    "the image.\n"
    "- No lightbulbs, gears, puzzle pieces, handshakes, hearts, checkmarks, or "
    "text-filled speech bubbles.\n"
    "- Do not depict a specific real event and do not make it look like a "
    "documentary photo or evidence of a particular activity."
)

# key: 出力ファイル名（public/images/generated/ 配下に保存する想定）
PRESETS = {
    "hero-connections.webp": {
        "kind": "editorial-illustration",
        "aspect_ratio": "16:9",
        "prompt": COMMON_STYLE_GUIDE
        + "\n\nSCENE: a woman standing calmly near the centre of the frame, "
        "shown waist up, relaxed and quietly confident. Loosely arranged around "
        "her (to her left and right, a little above and below) are several "
        "small flat vignettes of everyday community life, each linked to her by "
        "a single thin navy line so she is clearly held within society and "
        "belongs to it. The vignettes MUST include a clear mix of generations: "
        "an older person and a young child looking at a picture book together; "
        "neighbours of different ages chatting over tea; a small learning "
        "circle at a table; someone walking beside an older neighbour; a few "
        "people of mixed ages tending a shared garden. Show children, "
        "parent-age adults and older people. Keep work and office motifs to a "
        "minimum - no laptops, screens or headphones as a focus. The feeling is "
        "belonging and connection across the whole community, not careers. Calm "
        "pale background; keep the upper area fairly open for a headline.",
    },
    "about-possibilities.webp": {
        "kind": "editorial-illustration",
        "aspect_ratio": "4:3",
        "prompt": COMMON_STYLE_GUIDE
        + "\n\nSCENE: a woman with a chin-length bob, in a dark navy top, "
        "standing calmly near the centre of the frame, shown waist up. Around "
        "her - above, to the right and below - three or four small flat "
        "vignettes of ways to take part: a person at a home desk with a laptop, "
        "two people talking across a small table, a small group around a table, "
        "a person helping out in a community space. A single thin navy line "
        "connects each vignette to her. She is within society and linked into "
        "it, able to take an active part. Keep some calm empty space for text.",
    },
    "activity-learning.webp": {
        "kind": "editorial-illustration",
        "aspect_ratio": "1:1",
        "prompt": COMMON_STYLE_GUIDE
        + "\n\nSCENE: one adult at a tidy desk sorting a few loose papers into a "
        "neat stack, next to a small notebook and a simple screen showing a "
        "plain bar shape (no text, no numbers). Suggests turning confusing "
        "information into something clear and calm.",
    },
    "activity-dialogue.webp": {
        "kind": "editorial-illustration",
        "aspect_ratio": "1:1",
        "prompt": COMMON_STYLE_GUIDE
        + "\n\nSCENE: two adults sitting across a small table, leaning slightly "
        "toward each other in relaxed conversation, one open notebook between "
        "them. Equal and friendly, both listening.",
    },
    "activity-small-step.webp": {
        "kind": "editorial-illustration",
        "aspect_ratio": "1:1",
        "prompt": COMMON_STYLE_GUIDE
        + "\n\nSCENE: one adult taking a single calm step along a short dotted "
        "navy path toward a slightly larger, welcoming group of two or three "
        "people. Low pressure and encouraging.",
    },
    "activity-co-creation.webp": {
        "kind": "editorial-illustration",
        "aspect_ratio": "1:1",
        "prompt": COMMON_STYLE_GUIDE
        + "\n\nSCENE: three adults at one table, each doing a different task "
        "(one writing, one on a laptop, one arranging papers). Their work meets "
        "in the middle of the table. Different roles combining into one shared "
        "piece of work.",
    },
    "project-living-money.webp": {
        "kind": "editorial-illustration",
        "aspect_ratio": "4:3",
        "prompt": COMMON_STYLE_GUIDE
        + "\n\nSCENE: an older adult and a younger family member sitting at a "
        "table with a calm facilitator. On the table: a few documents, a small "
        "folder and a simple house shape. Everyone relaxed and equal. This is "
        "organising everyday life and money together, not a sales meeting and "
        "not a somber end-of-life scene. Keep one side of the frame calm and "
        "open for text.",
    },
    "future-collaboration.webp": {
        "kind": "editorial-illustration",
        "aspect_ratio": "4:3",
        "prompt": COMMON_STYLE_GUIDE
        + "\n\nSCENE: people of clearly different generations (a younger adult, "
        "a parent-age adult, an older adult) seated around one shared round "
        "table in easy conversation, a few notebooks on the table. Suggests "
        "dialogue across generations.",
    },
    "future-partnership.webp": {
        "kind": "editorial-illustration",
        "aspect_ratio": "4:3",
        "prompt": COMMON_STYLE_GUIDE
        + "\n\nSCENE: three or four adults from different settings meeting "
        "around one table as equals: one wearing a work apron, one with a "
        "laptop, one with a folder of civic paperwork. A plain board or a "
        "simple blank map shape behind them (no text). Suggests companies, "
        "local government and residents working together.",
    },
    "future-co-work.webp": {
        "kind": "editorial-illustration",
        "aspect_ratio": "4:3",
        "prompt": COMMON_STYLE_GUIDE
        + "\n\nSCENE: a few adults each handling one part of a shared task "
        "(planning notes, writing, a laptop, simple admin). Light plain panels "
        "or simple arrows show the parts joining into one finished piece on the "
        "right side. Small-scale teamwork, roles divided and then combined.",
    },
    "ogp-default.webp": {
        "kind": "ogp",
        "aspect_ratio": "16:9",
        "prompt": COMMON_STYLE_GUIDE
        + "\n\nSCENE: a simple, calm illustration of two or three adults around "
        "a table with notebooks, kept small and low-contrast, with plenty of "
        "empty pale space across the centre and one side so the website can "
        "overlay a title. Subtle enough to work as a small social-share "
        "thumbnail.",
    },
}
