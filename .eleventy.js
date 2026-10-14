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
