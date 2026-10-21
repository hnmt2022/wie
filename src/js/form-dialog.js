// data-form-open="<dialog の id>" のボタンを押すと、その dialog（中の iframe にフォーム）を開く。
// フォームは最初に開いたときだけ読み込む。
(function () {
  document.querySelectorAll("[data-form-open]").forEach(function (btn) {
    var dialog = document.getElementById(btn.dataset.formOpen);
    if (!dialog || typeof dialog.showModal !== "function") return;
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      var frame = dialog.querySelector("iframe");
      if (!frame.getAttribute("src")) frame.setAttribute("src", dialog.dataset.src);
      dialog.showModal();
      dialog._opener = btn;
    });
  });
  document.querySelectorAll("dialog.form-dialog").forEach(function (dialog) {
    dialog.querySelector("[data-close]").addEventListener("click", function () { dialog.close(); });
    dialog.addEventListener("click", function (e) { if (e.target === dialog) dialog.close(); });
    dialog.addEventListener("close", function () { if (dialog._opener) dialog._opener.focus(); });
  });
})();
