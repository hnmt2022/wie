// お知らせページ: タグで絞り込む（?tag=〇〇 にも対応。JSが動かない環境では全件表示のまま）
(function () {
  var filter = document.querySelector(".news-filter");
  var cards = document.querySelectorAll("#news-cards [data-tags]");
  var empty = document.getElementById("news-filter-empty");
  if (!filter || !cards.length) return;
  var buttons = filter.querySelectorAll(".news-filter__btn");

  function apply(tag, push) {
    var shown = 0;
    cards.forEach(function (card) {
      var match = !tag || card.dataset.tags.split("|").indexOf(tag) !== -1;
      card.hidden = !match;
      if (match) shown++;
    });
    buttons.forEach(function (b) {
      b.setAttribute("aria-pressed", b.dataset.tag === tag ? "true" : "false");
    });
    if (empty) empty.hidden = shown > 0;
    if (push) {
      var url = new URL(location.href);
      if (tag) url.searchParams.set("tag", tag); else url.searchParams.delete("tag");
      history.replaceState(null, "", url);
    }
  }

  buttons.forEach(function (b) {
    b.addEventListener("click", function () { apply(b.dataset.tag, true); });
  });
  filter.hidden = false;
  apply(new URLSearchParams(location.search).get("tag") || "", false);
})();
