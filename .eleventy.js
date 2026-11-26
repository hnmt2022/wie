module.exports = function (eleventyConfig) {
  // 静的アセットはそのままコピー
  eleventyConfig.addPassthroughCopy("src/css");
  eleventyConfig.addPassthroughCopy("src/js");
  eleventyConfig.addPassthroughCopy({ "public/images": "images" });
  // 独自ドメイン接続時: public/CNAME を作成すると _site/CNAME としてコピーされます
  eleventyConfig.addPassthroughCopy({ "public/CNAME": "CNAME" });

  eleventyConfig.addFilter("year", () => new Date().getFullYear());
  // ファイルがあるか（相談員の写真など、届く前は「準備中」を出すため）
  eleventyConfig.addFilter("fileExists", (p) => require("fs").existsSync(p));
  // CSS などの中身から短い番号をつくる。URL に ?v= で付けて、更新後に古いファイルがキャッシュで使われないようにする
  eleventyConfig.addFilter("fileHash", (p) =>
    require("crypto").createHash("md5").update(require("fs").readFileSync(p)).digest("hex").slice(0, 8)
  );

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
  // 連続講座など、開催日時の欄に日付が複数あるときは全部（例: 「12/9、12/16、1/13」）。タイトルからは最初の1つだけ
  const eventDates = (n) => {
    const posted = String(n.date || "").match(/(\d{4})\D(\d{1,2})\D(\d{1,2})/);
    const py = posted ? +posted[1] : new Date().getFullYear();
    const pd = posted ? new Date(py, posted[2] - 1, +posted[3]) : null;
    const guessYear = (m, d) => {
      const x = new Date(py, m - 1, d);
      return pd && x < new Date(pd.getTime() - 31 * 86400000) ? new Date(py + 1, m - 1, d) : x;
    };
    const re = /(\d{4})\s*[.\/年-]\s*(\d{1,2})\s*[.\/月-]\s*(\d{1,2})|(\d{1,2})\s*(?:月|\/)\s*(\d{1,2})/g;
    const toDate = (m) => (m[1] ? new Date(+m[1], m[2] - 1, +m[3]) : guessYear(+m[4], +m[5]));
    if (n.when) {
      const all = [...String(n.when).matchAll(re)].map(toDate);
      if (all.length) return [...new Map(all.map((d) => [d.getTime(), d])).values()].sort((a, b) => a - b);
    }
    const m = String(n.title || "").match(/(\d{4})\s*[.\/年-]\s*(\d{1,2})\s*[.\/月-]\s*(\d{1,2})|(\d{1,2})月(\d{1,2})日/);
    return m ? [toDate(m)] : [];
  };
  // 終了の判定・並び順は最後の開催日（連続講座は最終回が終わるまで「開催予定」）
  const eventDate = (n) => eventDates(n).slice(-1)[0] || null;
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
  // イベントカレンダー（お知らせページ）。先月〜最後のイベントの月までを月ごとに。
  // 各月 = { label, key, isCurrent, weeks: [[{day, isToday, isPast, events}|null ×7]…], events: [{day, wd, title, href, ended}] }
  eleventyConfig.addFilter("eventCalendar", (items) => {
    const today = todayJST();
    const wdNames = ["日", "月", "火", "水", "木", "金", "土"];
    const byDay = new Map(); // "2026-12-3" → [イベント]
    let last = new Date(today.getFullYear(), today.getMonth(), 1);
    for (const n of items || []) {
      const dates = eventDates(n);
      dates.forEach((d, i) => {
        const key = `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()}`;
        // タイトル先頭の「12月3日（木）」「2027年1月26日（火）」は日付と重なるので外す
        // カレンダーでは短く: 「12月から全4回！」や、末尾の「を開催します」「が始まります」なども外す
        let title = String(n.title || "")
          .replace(/^\s*(\d{4}年)?\d{1,2}月\d{1,2}日\s*[（(][^）)]*[）)]\s*/, "")
          .replace(/^\s*\d{1,2}月から全\d+回\s*[！!]?\s*/, "")
          .replace(/\s*[をが]?\s*(開催します|実施します|行います|始まります|スタートします)\s*[！!。]?\s*$/, "")
          .trim() || String(n.title || "");
        if (dates.length > 1) title += `（${i + 1}/${dates.length}回）`;
        const ev = { title, href: n.id ? `/news/${n.id}/` : n.url || "", ended: d < today, tags: n.tags || [] };
        byDay.set(key, [...(byDay.get(key) || []), ev]);
        if (d > last) last = d;
      });
    }
    if (!byDay.size) return [];
    const months = [];
    for (let m = new Date(today.getFullYear(), today.getMonth() - 1, 1); m <= last; m = new Date(m.getFullYear(), m.getMonth() + 1, 1)) {
      const y = m.getFullYear(), mo = m.getMonth();
      const days = new Date(y, mo + 1, 0).getDate();
      const cells = Array(m.getDay()).fill(null);
      const events = [];
      for (let d = 1; d <= days; d++) {
        const date = new Date(y, mo, d);
        const evs = byDay.get(`${y}-${mo + 1}-${d}`) || [];
        cells.push({ day: d, wd: date.getDay(), isToday: +date === +today, isPast: date < today, events: evs });
        evs.forEach((e) => events.push({ ...e, day: d, wd: wdNames[date.getDay()] }));
      }
      while (cells.length % 7) cells.push(null);
      const weeks = [];
      for (let i = 0; i < cells.length; i += 7) weeks.push(cells.slice(i, i + 7));
      months.push({ label: `${y}年${mo + 1}月`, key: `${y}-${String(mo + 1).padStart(2, "0")}`, isCurrent: y === today.getFullYear() && mo === today.getMonth(), weeks, events });
    }
    return months;
  });
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
