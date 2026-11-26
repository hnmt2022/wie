// イベントカレンダー: 1か月ずつ表示して「前の月／次の月」で切り替える（JSが動かないときは全部の月を並べたまま）
(function () {
  document.querySelectorAll("[data-event-cal]").forEach(function (cal) {
    if (cal.classList.contains("is-js")) return;
    var months = cal.querySelectorAll("[data-cal-month]");
    var nav = cal.querySelector(".event-cal__nav");
    var label = cal.querySelector("[data-cal-label]");
    var prev = cal.querySelector("[data-cal-prev]");
    var next = cal.querySelector("[data-cal-next]");
    var idx = 0;
    months.forEach(function (m, i) { if (m.hasAttribute("data-cal-current")) idx = i; });

    function show(i) {
      idx = i;
      months.forEach(function (m, j) { m.hidden = j !== i; });
      label.textContent = months[i].querySelector(".event-cal__title").textContent;
      prev.disabled = i === 0;
      next.disabled = i === months.length - 1;
    }
    prev.addEventListener("click", function () { if (idx > 0) show(idx - 1); });
    next.addEventListener("click", function () { if (idx < months.length - 1) show(idx + 1); });
    cal.classList.add("is-js");
    nav.hidden = false;
    show(idx);
  });
})();
