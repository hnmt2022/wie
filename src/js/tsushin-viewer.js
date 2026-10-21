// つながり通信: 表紙を押すと、ページを移動せずに拡大表示（<dialog>）で開く。
// JavaScript が動かないときは、リンク先（1ページ目の画像）がそのまま開く。
(function () {
  var viewer = document.getElementById("tsushin-viewer");
  if (!viewer || typeof viewer.showModal !== "function") return;
  var title = document.getElementById("tsushin-viewer-title");
  var pages = document.getElementById("tsushin-viewer-pages");
  var opener = null;

  document.querySelectorAll(".tsushin-card").forEach(function (card) {
    card.addEventListener("click", function (e) {
      e.preventDefault();
      opener = card;
      title.textContent = card.dataset.title;
      pages.innerHTML = "";
      card.dataset.pages.split("|").forEach(function (src, i, all) {
        var img = document.createElement("img");
        img.src = src;
        img.alt = card.dataset.title + (all.length > 1 ? "（" + (i + 1) + "ページ目）" : "");
        img.addEventListener("click", function () { img.classList.toggle("is-zoomed"); });
        pages.appendChild(img);
      });
      viewer.showModal();
      pages.scrollTop = 0;
    });
  });

  function close() { viewer.close(); }
  viewer.querySelector("[data-close]").addEventListener("click", close);
  // 画像の外側（暗い部分）を押したら閉じる
  viewer.addEventListener("click", function (e) { if (e.target === viewer) close(); });
  viewer.addEventListener("close", function () { if (opener) opener.focus(); });
})();
