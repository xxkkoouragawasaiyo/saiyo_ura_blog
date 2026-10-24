#!/usr/bin/env python3
"""Google Search Console の「検索パフォーマンス」エクスポート(zip)を取り込む。

GSC 画面の「エクスポート > CSV ダウンロード」で得られる zip を、
期間ごとに英語カラム・数値型へ正規化した CSV として data/gsc/ 配下に保存する。

使い方:
    python3 scripts/gsc_import.py path/to/*.zip [--snapshot 2026-10-10]

出力:
    data/gsc/raw/<snapshot>/<period>.zip           元ファイル（再現用）
    data/gsc/<snapshot>/<period>/{daily,queries,pages,countries,devices}.csv
    data/gsc/<snapshot>/manifest.json               期間・行数・合計値
"""
import argparse
import csv
import io
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "gsc"

# GSC の日本語ファイル名 → 正規化後の名前と先頭カラム名
FILES = {
    "平均読み込み時間のチャート.csv": ("daily", "date"),
    "クエリ.csv": ("queries", "query"),
    "ページ.csv": ("pages", "page"),
    "国.csv": ("countries", "country"),
    "デバイス.csv": ("devices", "device"),
    "検索での見え方.csv": ("appearance", "appearance"),
}
METRICS = ["clicks", "impressions", "ctr", "position"]

# フィルタ.csv の「日付」値 → 期間キー
PERIODS = {
    "過去 7 日間": "last7d",
    "過去 28 日間": "last28d",
    "過去 3 か月間": "last3m",
    "過去 6 か月間": "last6m",
    "過去 12 か月間": "last12m",
    "過去 16 か月間": "last16m",
}


def read_csv(zf: zipfile.ZipFile, name: str) -> list[list[str]]:
    text = zf.read(name).decode("utf-8-sig")
    return [row for row in csv.reader(io.StringIO(text)) if row]


def period_key(label: str) -> str:
    if label in PERIODS:
        return PERIODS[label]
    # カスタム期間（例: "2026-07-01 - 2026-09-30"）はそのまま slug 化
    return "custom_" + re.sub(r"[^0-9A-Za-z]+", "_", label).strip("_")


def to_number(value: str, metric: str):
    value = value.strip()
    if metric == "ctr":
        return round(float(value.rstrip("%")) / 100, 6) if value else 0.0
    if metric == "position":
        return float(value) if value else None
    return int(value.replace(",", "")) if value else 0


def import_zip(path: Path, snapshot: str | None) -> dict:
    with zipfile.ZipFile(path) as zf:
        names = set(zf.namelist())
        filters = dict(read_csv(zf, "フィルタ.csv")[1:])
        period = period_key(filters.get("日付", "unknown"))

        tables = {}
        for jp_name, (key, dim) in FILES.items():
            if jp_name not in names:
                continue
            rows = read_csv(zf, jp_name)[1:]
            tables[key] = [
                {dim: r[0].strip(), **{m: to_number(v, m) for m, v in zip(METRICS, r[1:5])}}
                for r in rows
            ]

    daily = tables.get("daily", [])
    if snapshot is None:
        # GSC のファイル名の日付（エクスポート日）を優先し、なければ最終データ日
        m = re.search(r"(\d{4}-\d{2}-\d{2})", path.name)
        snapshot = m.group(1) if m else daily[-1]["date"]

    out_dir = DATA_DIR / snapshot / period
    out_dir.mkdir(parents=True, exist_ok=True)
    for key, rows in tables.items():
        dim = next(d for k, d in FILES.values() if k == key)
        with open(out_dir / f"{key}.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[dim, *METRICS])
            writer.writeheader()
            writer.writerows(rows)

    raw_dir = DATA_DIR / "raw" / snapshot
    raw_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, raw_dir / f"{period}.zip")

    return {
        "snapshot": snapshot,
        "period": period,
        "period_label": filters.get("日付"),
        "search_type": filters.get("検索タイプ"),
        # ページで絞り込んだエクスポートは --snapshot <日付>_<記事スラッグ> で別フォルダに取り込む
        "page_filter": filters.get("ページ"),
        "date_from": daily[0]["date"] if daily else None,
        "date_to": daily[-1]["date"] if daily else None,
        # 日別（グラフ）の合計を全体の合計とする。ページ絞り込み時はデバイス別・クエリ別・国別から
        # 匿名化クエリ分が欠けるため使わない（サイト全体のエクスポートでは日別とデバイス別は一致する）
        "total_clicks": sum(d["clicks"] for d in daily),
        "total_impressions": sum(d["impressions"] for d in daily),
        "rows": {k: len(v) for k, v in tables.items()},
        "source": path.name,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("zips", nargs="+", type=Path)
    parser.add_argument("--snapshot", help="保存先の日付フォルダ名（省略時はファイル名の日付）")
    args = parser.parse_args()

    entries = [import_zip(p, args.snapshot) for p in args.zips]
    for snapshot in sorted({e["snapshot"] for e in entries}):
        manifest_path = DATA_DIR / snapshot / "manifest.json"
        manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
        for e in entries:
            if e["snapshot"] == snapshot:
                manifest[e["period"]] = e
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n")

    for e in entries:
        print(f"{e['snapshot']}/{e['period']}: {e['date_from']}〜{e['date_to']} "
              f"clicks={e['total_clicks']:,} imp={e['total_impressions']:,} rows={e['rows']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
