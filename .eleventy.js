module.exports = function (eleventyConfig) {
  // 静的アセットはそのままコピー
  eleventyConfig.addPassthroughCopy("src/css");
  eleventyConfig.addPassthroughCopy("src/js");
  eleventyConfig.addPassthroughCopy({ "public/images": "images" });
  // 独自ドメイン接続時: public/CNAME を作成すると _site/CNAME としてコピーされます
  eleventyConfig.addPassthroughCopy({ "public/CNAME": "CNAME" });

  eleventyConfig.addFilter("year", () => new Date().getFullYear());

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
