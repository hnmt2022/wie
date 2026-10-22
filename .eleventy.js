module.exports = function (eleventyConfig) {
  // 静的アセットはそのままコピー
  eleventyConfig.addPassthroughCopy("src/css");
  eleventyConfig.addPassthroughCopy("src/js");
  eleventyConfig.addPassthroughCopy({ "public/images": "images" });
  // 独自ドメイン接続時: public/CNAME を作成すると _site/CNAME としてコピーされます
  eleventyConfig.addPassthroughCopy({ "public/CNAME": "CNAME" });

  eleventyConfig.addFilter("year", () => new Date().getFullYear());

  // お知らせのタグ一覧（登場順・重複なし）
  eleventyConfig.addFilter("newsTags", (items) => [...new Set((items || []).flatMap((n) => n.tags || []))]);
  // 配列から id が一致する1件を返す（Nunjucks の selectattr は値の比較ができないため）
  eleventyConfig.addFilter("findById", (items, id) => (items || []).find((x) => x.id === id));
  // 文章を段落（空行区切り）→ 行の二重配列にする。改行をテンプレート側で <br> にするため
  eleventyConfig.addFilter("paragraphs", (text) =>
    String(text || "").split(/\r?\n\s*\r?\n/).map((p) => p.split(/\r?\n/)).filter((p) => p.join("").trim())
  );
  // 文章の中の最初の https:// の URL を返す（申込方法の欄からボタンを作る）
  eleventyConfig.addFilter("firstUrl", (text) => (String(text || "").match(/https:\/\/[^\s　）)]+/) || [""])[0]);
  // お知らせのイベント開催日（Date）。開催日時の欄 → タイトルの「11月9日」の順に探し、なければ null（イベントではない）。
  // 年が書かれていないときは、お知らせの日付の年。お知らせの日付より1か月以上前になるなら翌年とみなす
  const eventDate = (n) => {
    const posted = String(n.date || "").match(/(\d{4})\D(\d{1,2})\D(\d{1,2})/);
    const py = posted ? +posted[1] : new Date().getFullYear();
    const pd = posted ? new Date(py, posted[2] - 1, +posted[3]) : null;
    for (const text of [n.when, n.title]) {
      if (!text) continue;
      const full = String(text).match(/(\d{4})\s*[.\/年-]\s*(\d{1,2})\s*[.\/月-]\s*(\d{1,2})/);
      if (full) return new Date(+full[1], full[2] - 1, +full[3]);
      const md = String(text).match(/(\d{1,2})月(\d{1,2})日/);
      if (md) {
        let d = new Date(py, md[1] - 1, +md[2]);
        if (pd && d < new Date(pd.getTime() - 31 * 86400000)) d = new Date(py + 1, md[1] - 1, +md[2]);
        return d;
      }
    }
    return null;
  };
  // 今日（日本時間）の0時。ビルドした日を基準にする（毎朝自動でビルドし直す: .github/workflows/deploy.yml）
  const todayJST = () => {
    const t = new Date(Date.now() + 9 * 3600000);
    return new Date(t.getUTCFullYear(), t.getUTCMonth(), t.getUTCDate());
  };
  const isEnded = (n) => { const d = eventDate(n); return !!d && d < todayJST(); };
  eleventyConfig.addFilter("isEnded", isEnded);
  // 開催予定・通常のお知らせ（新しい順）
  eleventyConfig.addFilter("currentNews", (items) => (items || []).filter((n) => !isEnded(n)).reverse());
  // 開催終了したイベント（開催日の新しい順）
  eleventyConfig.addFilter("endedNews", (items) =>
    (items || []).filter(isEnded).sort((a, b) => eventDate(b) - eventDate(a))
  );
  // 指定したタグが付いたお知らせだけを返す
  eleventyConfig.addFilter("newsByTag", (items, tag) => (items || []).filter((n) => (n.tags || []).includes(tag)));

  return {
    dir: {
      input: "src",
      includes: "_includes",
      data: "_data",
      output: "_site",
    },
    pathPrefix: process.env.PATH_PREFIX || "/",
    templateFormats: ["njk", "md"],
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk",
  };
};
