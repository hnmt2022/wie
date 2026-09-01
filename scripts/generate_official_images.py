#!/usr/bin/env python3
"""
Wie 公式HP用の画像生成スクリプト（テンプレート）。

このスクリプトは「Wie for Life」LP用に別途提供されるPython画像生成スクリプトを
上書きしません。公式HP専用の別スクリプトとして分離しています。プリセットは
image_presets_official.py にあります。

安全のための方針:
  - 認証情報が未設定の場合は生成を実行せず、必要な設定を説明して終了します。
  - 1回の実行で生成する枚数はデフォルトで少なくしています（--count で変更可）。
  - 失敗しても自動で大量リトライはしません（1回だけ試行し、失敗はログに残して終了）。
  - 実行したモデル・プロンプト・出力ファイル名を generation_log/ に記録します。
  - ビルドやデプロイのたびに自動実行される想定ではありません。必要なときに
    手動で実行し、採用した画像だけを public/images/generated/ に保存してください。

実際の呼び出し部分（call_image_api）は、利用するVertex AI / Gemini画像生成APIの
バージョンに合わせて実装してください。このテンプレートでは、Google公式の
`google-genai` SDK を使う想定の骨組みだけを用意しています。

使い方の例:
  python scripts/generate_official_images.py --list
  python scripts/generate_official_images.py --only hero-connections.webp --count 1
"""

import argparse
import io
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image
from google import genai
from google.genai import types

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "public" / "images" / "generated"
LOG_DIR = Path(__file__).resolve().parent / "generation_log"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from image_presets_official import PRESETS  # noqa: E402


def load_dotenv_if_present():
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def check_credentials():
    """
    認証情報が未設定なら False を返す。
    次の「どちらか」があれば実行できます（いずれも .env からのみ読み込み、
    ソースコードやリポジトリには絶対に書き込まないでください）。
      A) GEMINI_API_KEY        … Google AI Studio のAPIキー（かんたん）
      B) GOOGLE_CLOUD_PROJECT  … Vertex AI を使う場合（認証は gcloud ADC）
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")

    if api_key or project:
        return True

    print("画像生成に必要な環境変数が未設定のため、生成を実行しません。")
    print("")
    print("設定方法（どちらか一方）:")
    print("  1. env.example を .env にコピーする（.env はGit管理対象外です）")
    print("  【方法A・推奨】")
    print("  2. https://aistudio.google.com/apikey でAPIキーを取得する")
    print("  3. .env に GEMINI_API_KEY=... を設定する")
    print("  【方法B・Vertex AI】")
    print("  2. .env に GOOGLE_CLOUD_PROJECT=... を設定する")
    print("  3. 事前に `gcloud auth application-default login` を実行しておく")
    return False


def create_client() -> genai.Client:
    """APIキー方式（優先）または Vertex AI 方式でクライアントを作成する。"""
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if api_key:
        return genai.Client(api_key=api_key)

    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
    return genai.Client(vertexai=True, project=project, location=location)


# 画像生成モデル（前から順に試す）。画風を揃えるため既定は 3-pro を最優先にし、
# レート制限のときは同じモデルで少し待って再試行してから次に移る。
IMAGE_MODELS = [
    "gemini-3-pro-image",
    "gemini-2.5-flash-image",
]

_RATE_LIMIT_MARKERS = ("RESOURCE_EXHAUSTED", "429")


def _looks_rate_limited(error: Exception) -> bool:
    text = f"{type(error).__name__} {error}"
    return any(marker in text for marker in _RATE_LIMIT_MARKERS)


def _generate_once(client, name: str, prompt: str, aspect_ratio: str, reference=None):
    contents = [prompt, reference] if reference is not None else prompt
    response = client.models.generate_content(
        model=name,
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(aspect_ratio=aspect_ratio),
        ),
    )
    for candidate in response.candidates or []:
        for part in (candidate.content.parts if candidate.content else []) or []:
            if getattr(part, "inline_data", None) is not None:
                return part.inline_data.data
    raise RuntimeError("応答に画像が含まれていませんでした。")


def call_image_api(prompt: str, aspect_ratio: str, model_name: str, reference=None):
    """
    Gemini 画像生成APIを呼び出し、生成画像のバイト列を返す。
    reference を渡すと、その画像を下敷きにした部分修正（画像編集）になる。
    model_name を明示指定した場合はそれを最優先で試す。
    レート制限（429）のときだけ、同じモデルで最大2回まで待って再試行する。
    それ以外の失敗は次のモデルにフォールバックする。
    """
    client = create_client()

    models = list(IMAGE_MODELS)
    if model_name and model_name not in models:
        models.insert(0, model_name)

    last_error = None
    for name in models:
        for attempt in range(1, 4):
            try:
                print(f"  モデル使用: {name}（試行 {attempt}）")
                return _generate_once(client, name, prompt, aspect_ratio, reference)
            except Exception as error:  # noqa: BLE001
                last_error = error
                if _looks_rate_limited(error) and attempt < 3:
                    wait = 25 * attempt
                    print(f"  レート制限。{wait}秒待って同じモデルで再試行します。")
                    time.sleep(wait)
                    continue
                print(f"  失敗: {name} - {type(error).__name__}: {error}")
                break

    raise RuntimeError(f"すべてのモデルで生成できませんでした。最後のエラー: {last_error}")


def write_log(entry: dict):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_path = LOG_DIR / f"{ts}.json"
    log_path.write_text(
        json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--list", action="store_true", help="生成候補の一覧を表示して終了する"
    )
    parser.add_argument(
        "--only",
        action="append",
        help="生成するファイル名を指定する（複数回指定可）。省略時は最初の1件のみ。",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="1画像あたりの生成候補数（デフォルト: 1）。まず低い枚数で方向性を確認してください。",
    )
    parser.add_argument(
        "--model",
        default="",
        help="使用するモデル名を明示指定する（省略時は既定のモデルを順に試す）",
    )
    parser.add_argument(
        "--reference",
        help="下敷きにする既存画像のパス（部分修正モード）。通常は同じプリセットの現行 .webp を指定する。",
    )
    parser.add_argument(
        "--edit",
        help="部分修正モードでの追加指示（例: '左の大きな立ち姿の人物だけを女性にする。他は一切変えない'）。--reference と併用。",
    )
    args = parser.parse_args()

    if args.list:
        for name, preset in PRESETS.items():
            print(f"{name}  [{preset['kind']}, {preset['aspect_ratio']}]")
        return

    load_dotenv_if_present()

    targets = args.only or [next(iter(PRESETS))]
    unknown = [t for t in targets if t not in PRESETS]
    if unknown:
        print(f"未定義のファイル名です: {', '.join(unknown)}")
        print("候補一覧は --list で確認できます。")
        sys.exit(1)

    if not check_credentials():
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    count = max(1, args.count)

    reference_image = None
    if args.reference:
        ref_path = Path(args.reference)
        if not ref_path.is_file():
            print(f"参照画像が見つかりません: {ref_path}")
            sys.exit(1)
        reference_image = Image.open(ref_path)
        print(f"部分修正モード: {ref_path} を下敷きにします。")

    for filename in targets:
        preset = PRESETS[filename]
        base = Path(filename)
        for variant in range(1, count + 1):
            # --count が2以上のときは 1枚目=そのままの名前、2枚目以降= name-2.webp …
            if variant == 1:
                out_path = OUTPUT_DIR / filename
            else:
                out_path = OUTPUT_DIR / f"{base.stem}-{variant}{base.suffix}"

            label = out_path.name
            if reference_image is not None:
                prompt = (
                    preset["prompt"]
                    + "\n\nEDIT MODE: You are given the current illustration as a "
                    "reference. Keep its composition, layout, colours and drawing "
                    "style exactly the same. Change only what the following "
                    "instruction asks, and leave everything else untouched.\n"
                    + "INSTRUCTION: "
                    + (args.edit or "(no extra instruction given)")
                )
            else:
                prompt = preset["prompt"]

            print(f"[生成] {label} ({preset['kind']}, {preset['aspect_ratio']})")
            try:
                image_bytes = call_image_api(
                    prompt=prompt,
                    aspect_ratio=preset["aspect_ratio"],
                    model_name=args.model,
                    reference=reference_image,
                )
            except Exception as e:  # noqa: BLE001
                print(f"  生成に失敗しました: {e}")
                write_log(
                    {
                        "filename": label,
                        "model": args.model or "(auto)",
                        "prompt": preset["prompt"],
                        "status": "error",
                        "error": str(e),
                    }
                )
                continue

            # モデルの出力は通常PNG。拡張子（.webp等）に合わせて変換して保存する。
            image = Image.open(io.BytesIO(image_bytes))
            save_kwargs = (
                {"quality": 90} if out_path.suffix.lower() == ".webp" else {}
            )
            image.save(out_path, **save_kwargs)
            write_log(
                {
                    "filename": label,
                    "model": args.model or "(auto)",
                    "prompt": preset["prompt"],
                    "status": "success",
                    "output": str(out_path.relative_to(ROOT)),
                }
            )
            print(f"  保存しました: {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
