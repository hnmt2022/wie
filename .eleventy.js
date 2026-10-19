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
