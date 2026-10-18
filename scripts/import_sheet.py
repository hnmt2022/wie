"""
Wieサイト更新シート（Googleスプレッドシート）の内容を、サイトのデータに取り込む。

使い方（リポジトリのルートで実行）:
    python scripts/import_sheet.py            # 確認だけ（ファイルは変更しない）
    python scripts/import_sheet.py --apply    # 取り込んでファイルを書き換える

読み込み先は scripts/sheet-config.json に、タブごとの CSV の URL を書く。
  - 「ウェブに公開」した場合: .../pub?gid=<gid>&single=true&output=csv
  - 「リンクを知っている全員」で共有した場合: https://docs.google.com/spreadsheets/d/<id>/export?format=csv&gid=<gid>
URL が null のタブは読み込まない（今のデータをそのまま残す）。
写真は「写真」欄にファイル名を書けば、photoFolder（共有した写真フォルダの URL）から探す。ドライブのリンクでも可。

取り込み先:
  お知らせ       → src/_data/news.json（シートの「公開 = ○」の行で丸ごと置き換え）
  写真           → src/_data/pillars.json / services.json の "photo"（掲載許可 = 未 の行は除く）
  サービス料金   → src/_data/services.json の "prices"（シートにあるサービスだけ置き換え）
  リンク         → src/_data/links.json / site.json の "sns"
写真は Google ドライブから取得し、長辺 1600px の WebP にして public/images/activities/ に保存する。
"""
import csv
import io
import json
import re
import sys
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "src" / "_data"
PHOTO_DIR = ROOT / "public" / "images" / "activities"
CONFIG = ROOT / "scripts" / "sheet-config.json"
MAX_SIDE = 1600

warnings = []


def warn(msg):
    warnings.append(msg)


def load_json(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def save_json(name, data):
    (DATA / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "wie-sheet-import"})
    with urllib.request.urlopen(req, timeout=60) as res:
        return res.read(), res.headers.get("Content-Type", "")


def read_tab(url):
    """CSV を読み、見出し行をキーにした dict のリストを返す（空行は除く）"""
    body, ctype = fetch(url)
    if "text/html" in ctype:
        raise SystemExit(f"CSV ではなく HTML が返りました。共有／ウェブに公開の設定を確認してください: {url}")
    rows = list(csv.reader(io.StringIO(body.decode("utf-8-sig"))))
    if not rows:
        return []
    head = [h.strip() for h in rows[0]]
    out = []
    for i, r in enumerate(rows[1:], start=2):
        r = [c.strip() for c in r] + [""] * (len(head) - len(r))
        if not any(r):
            continue
        row = dict(zip(head, r))
        row["_line"] = i
        out.append(row)
    return out


def col(row, *names):
    """見出しの表記ゆれに対応して値を取る（「メモ（サイトには出ません）」→「メモ」でも可）"""
    for n in names:
        for k, v in row.items():
            if k == n or k.startswith(n):
                return v
    return ""


def is_yes(v):
    return v.strip() in ("○", "〇", "◯", "o", "O", "yes", "はい", "済")


def norm_date(v, line):
    m = re.match(r"^\s*(\d{4})\D+(\d{1,2})\D+(\d{1,2})", v)
    if not m:
        warn(f"お知らせ {line}行目: 日付「{v}」が読めないので飛ばしました（2026.10.15 の形で）")
        return None
    y, mo, d = m.groups()
    return f"{y}.{int(mo):02d}.{int(d):02d}"


def drive_id(link):
    m = re.search(r"/d/([A-Za-z0-9_-]{20,})", link) or re.search(r"[?&]id=([A-Za-z0-9_-]{20,})", link)
    return m.group(1) if m else None


_folder_files = None


def folder_files():
    """写真フォルダ（sheet-config.json の photoFolder）のファイル名 → ファイルID。
    「リンクを知っている全員」で共有したフォルダの一覧ページから読む"""
    global _folder_files
    if _folder_files is None:
        _folder_files = {}
        url = json.loads(CONFIG.read_text(encoding="utf-8")).get("photoFolder")
        fid = drive_id(url or "") or (re.search(r"folders/([A-Za-z0-9_-]{20,})", url or "") or [None, None])[1]
        if not fid:
            warn("写真フォルダの URL（scripts/sheet-config.json の photoFolder）が未設定です")
            return _folder_files
        body, _ = fetch(f"https://drive.google.com/embeddedfolderview?id={fid}")
        html = body.decode("utf-8", "replace")
        for m in re.finditer(r'id="entry-([A-Za-z0-9_-]{20,})".*?class="flip-entry-title">([^<]+)<', html, re.S):
            name = m.group(2).strip().replace("&amp;", "&")
            _folder_files[name] = m.group(1)
        if not _folder_files:
            warn("写真フォルダの中身を読めませんでした。フォルダの共有が「リンクを知っている全員」になっているか確認してください")
    return _folder_files


def resolve_photo(value):
    """「写真」欄の値（ドライブのリンク、またはフォルダ内のファイル名）からファイルIDを返す"""
    fid = drive_id(value)
    if fid:
        return fid
    files = folder_files()
    if value in files:
        return files[value]
    # 拡張子の有無・大文字小文字の違いは許す
    key = value.lower().rsplit(".", 1)[0]
    for name, i in files.items():
        if name.lower().rsplit(".", 1)[0] == key:
            return i
    return None


def download_photo(link, filename, label, apply):
    """写真フォルダ（ファイル名）またはドライブのリンクの写真を WebP に変換して保存し、ファイル名を返す。失敗したら None"""
    fid = resolve_photo(link)
    if not fid:
        warn(f"{label}: 写真「{link}」が写真フォルダに見つかりませんでした（ファイル名を確認してください）")
        return None
    if not apply:
        return filename
    from PIL import Image, ImageOps
    body, ctype = fetch(f"https://drive.google.com/uc?export=download&id={fid}")
    if ctype.startswith("application/pdf"):
        warn(f"{label}: PDF は使えません。JPEG か PNG の画像にしてフォルダに入れてください")
        return None
    if not ctype.startswith("image/"):
        warn(f"{label}: 写真を取得できませんでした。共有が「リンクを知っている全員」になっているか確認してください")
        return None
    try:
        img = Image.open(io.BytesIO(body))
    except Exception:
        warn(f"{label}: 写真を開けませんでした（PDF・HEIC は使えません。JPEG か PNG で入れてください）")
        return None
    img = ImageOps.exif_transpose(img).convert("RGB")
    img.thumbnail((MAX_SIDE, MAX_SIDE))
    PHOTO_DIR.mkdir(parents=True, exist_ok=True)
    img.save(PHOTO_DIR / filename, "WEBP", quality=82)
    return filename


def import_news(rows, apply):
    old = load_json("news.json")
    items = []
    for r in rows:
        if not is_yes(col(r, "公開")):
            continue
        line = r["_line"]
        date = norm_date(col(r, "日付"), line)
        title = col(r, "タイトル")
        if not date:
            continue
        if not title:
            warn(f"お知らせ {line}行目: タイトルが空なので飛ばしました")
            continue
        tags = [t.strip() for t in re.split(r"[、,，]", col(r, "タグ")) if t.strip()]
        item = {"date": date, "tags": tags, "title": title, "summary": col(r, "説明")}
        url = col(r, "リンク")
        if url:
            if url.startswith(("https://", "http://")):
                item["url"] = url
            else:
                warn(f"お知らせ {line}行目: リンク「{url}」は https:// で始まらないので外しました")
        photo = col(r, "写真")
        if photo:
            fn = download_photo(photo, f"news-{date.replace('.', '')}-{line}.webp", f"お知らせ {line}行目", apply)
            if fn:
                item["photo"] = fn
        items.append(item)
    items.sort(key=lambda x: x["date"])
    if not items:
        print("■ お知らせ: シートに「公開 = ○」の行がないので、今のお知らせをそのまま残します")
        return
    print(f"■ お知らせ: {len(old)}件 → {len(items)}件（シートの「公開 = ○」の行）")
    for it in items:
        print(f"   {it['date']}  {it['title']}  {'#' + ' #'.join(it['tags']) if it['tags'] else ''}{'  [写真]' if it.get('photo') else ''}")
    if any(o.get("sample") for o in old):
        print("   ※ 今のサンプルのお知らせは、すべて置き換わります")
    if apply:
        save_json("news.json", items)


def import_photos(rows, apply):
    pillars = load_json("pillars.json")
    services = load_json("services.json")
    by_title = {p["title"]: p for p in pillars}
    svc_by_name = {s["name"]: s for s in services}
    changed = []
    for r in rows:
        place, link, line = col(r, "載せる場所"), col(r, "写真"), r["_line"]
        if not link:
            continue
        if place not in by_title:
            warn(f"写真 {line}行目: 載せる場所「{place}」が候補にありません")
            continue
        if col(r, "掲載許可") == "未":
            warn(f"写真 {line}行目（{place}）: 掲載許可が「未」なので使いませんでした")
            continue
        p = by_title[place]
        fn = download_photo(link, f"activity-{p['id']}.webp", f"写真 {line}行目（{place}）", apply)
        if not fn:
            continue
        p["photo"] = fn
        if place in svc_by_name:
            svc_by_name[place]["photo"] = fn
        changed.append(place)
    print(f"■ 写真: {len(changed)}件 {'／'.join(changed)}")
    if apply and changed:
        save_json("pillars.json", pillars)
        save_json("services.json", services)


def import_prices(rows, apply):
    services = load_json("services.json")
    by_name = {s["name"]: s for s in services}
    groups = {}
    for r in rows:
        name, line = col(r, "サービス"), r["_line"]
        if name not in by_name:
            warn(f"サービス料金 {line}行目: サービス名「{name}」がサイトにありません（{'／'.join(by_name)}）")
            continue
        if not col(r, "内容") or not col(r, "料金"):
            warn(f"サービス料金 {line}行目: 内容か料金が空なので飛ばしました")
            continue
        groups.setdefault(name, []).append(r)
    print("■ サービス料金:")
    for name, rs in groups.items():
        s = by_name[name]
        s["prices"] = [{"item": col(r, "内容"), "price": col(r, "料金"), "note": col(r, "備考")} for r in rs]
        s["sample"] = not all(is_yes(col(r, "確定")) for r in rs)
        print(f"   {name}: {len(rs)}行{'（サンプル表示のまま）' if s['sample'] else '（確定・サンプル表示を外す）'}")
    if apply and groups:
        save_json("services.json", services)


def import_links(rows, apply):
    links = load_json("links.json")
    site = load_json("site.json")
    keys = {"note": "NOTE_URL", "ラジオ": "RADIO_URL"}
    print("■ リンク:")
    for r in rows:
        name, url, line = col(r, "名前"), col(r, "URL"), r["_line"]
        if url and not url.startswith("https://"):
            warn(f"リンク {line}行目: 「{url}」は https:// で始まらないので飛ばしました")
            continue
        if name in keys:
            if links.get(keys[name]) != (url or None):
                print(f"   {name}: {links.get(keys[name])} → {url or '（空・準備中表示）'}")
            links[keys[name]] = url or None
        elif any(s["label"] == name for s in site["sns"]):
            for s in site["sns"]:
                if s["label"] == name and url and s["url"] != url:
                    print(f"   {name}: {s['url']} → {url}")
                    s["url"] = url
        else:
            warn(f"リンク {line}行目: 名前「{name}」はサイトにない項目です")
    if apply:
        save_json("links.json", links)
        save_json("site.json", site)


def main():
    apply = "--apply" in sys.argv
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    steps = [("news", import_news), ("photos", import_photos), ("prices", import_prices), ("links", import_links)]
    if not any(config.get(k) for k, _ in steps):
        raise SystemExit("scripts/sheet-config.json に CSV の URL がまだありません")
    for key, fn in steps:
        if config.get(key):
            fn(read_tab(config[key]), apply)
        else:
            print(f"■ {key}: URL 未設定のため読み込みませんでした")
    if warnings:
        print("\n▲ 確認が必要なこと")
        for w in warnings:
            print("   - " + w)
    print("\n" + ("ファイルを書き換えました。npm run build で確認してください。" if apply else "（確認のみ。取り込むときは --apply を付けて実行）"))


if __name__ == "__main__":
    main()
