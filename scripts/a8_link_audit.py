#!/usr/bin/env python3
"""公開中の記事HTMLからA8.netの広告リンクを棚卸しし、「広告掲載URL管理」への提出リストを作る。

使い方（サイトにアクセスできる手元のPCで実行）:
    python3 scripts/a8_link_audit.py
    python3 scripts/a8_link_audit.py --urls urls.txt          # 調べるURLを指定（1行1URL）
    python3 scripts/a8_link_audit.py --map data/affiliate/a8_link_map.csv

入力:
    サイトマップ（wp-sitemap.xml / sitemap.xml）。取れない場合は data/articles/article_master.csv の記事
    data/affiliate/<最新>/a8_programs_*.csv   プログラムID → プログラム名
    data/affiliate/a8_link_map.csv（任意）    a8mat → プログラムID の対応表（テキストリンク用）
出力（reports/affiliate/<実行日>/）:
    a8_link_audit.csv                  記事 × A8リンクの一覧
    a8_submit_<プログラムID>.txt       提出フォームに貼り付けるURL（1行1URL）
    a8_unmapped.csv                    プログラムを判定できなかった a8mat（対応表に追記する）

注意:
    - px.a8.net のリンク先にはアクセスしない（クリック計測を汚さないため）。HTMLを読むだけ。
    - バナー（画像URLに mid=s000... を含む）はプログラムIDを自動判定する。
      テキストリンクは a8mat しか持たないため、同じ a8mat のバナーが無い場合は対応表で判定する。
"""
import argparse
import csv
import html
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import date
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://saiyo-ura.com"
UA = "Mozilla/5.0 (compatible; saiyo-ura-a8-audit/1.0)"
SUBMIT_LIMIT = 100  # 提出フォームに一度に入力できるURL数
SITEWIDE_RATIO = 0.8  # この割合以上の記事に出ているプログラムは、サイドバー等の全ページ表示とみなす

A8MAT_RE = re.compile(r"a8mat=([0-9A-Z]+(?:\+[0-9A-Z]+)+)")
MID_RE = re.compile(r"mid=(s\d{14})")
ANCHOR_RE = re.compile(r"<a\s[^>]*?href=[\"']([^\"']*a8\.net[^\"']*)[\"'][^>]*>(.*?)</a>", re.S | re.I)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read().decode("utf-8", errors="replace")


def sitemap_urls(site: str) -> list[str]:
    """WordPress標準（wp-sitemap.xml）と一般的な sitemap.xml を順に試し、記事URLを集める。"""
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    for index in (f"{site}/wp-sitemap.xml", f"{site}/sitemap.xml", f"{site}/sitemap_index.xml"):
        try:
            root = ET.fromstring(fetch(index))
        except Exception:
            continue
        locs = [e.text.strip() for e in root.iter(f"{ns}loc") if e.text]
        if root.tag == f"{ns}sitemapindex":
            urls = []
            for sub in locs:
                # タグ・カテゴリ・投稿者のサイトマップは提出対象にならないので読まない
                if re.search(r"(taxonomies|category|post_tag|users|author)", sub):
                    continue
                try:
                    urls += [e.text.strip() for e in ET.fromstring(fetch(sub)).iter(f"{ns}loc") if e.text]
                except Exception as e:
                    print(f"  サイトマップ取得失敗: {sub} ({e})", file=sys.stderr)
            return urls
        return locs
    return []


def master_urls(site: str) -> list[str]:
    with open(ROOT / "data" / "articles" / "article_master.csv", encoding="utf-8") as f:
        return [site + "/"] + [site + r["slug"] for r in csv.DictReader(f)]


def load_programs() -> dict[str, str]:
    files = sorted((ROOT / "data" / "affiliate").glob("*/a8_programs_*.csv"))
    if not files:
        return {}
    with open(files[-1], encoding="utf-8") as f:
        return {r["プログラムID"]: r["プログラム名"].strip() for r in csv.DictReader(f)}


def load_map(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return {r["a8mat"].strip(): r["program_id"].strip() for r in csv.DictReader(f) if r.get("a8mat")}


def extract(page_html: str) -> list[tuple[str, str]]:
    """ページ内のA8リンクを (a8mat, mid) で返す。mid はバナーのときだけ入る。"""
    text = unquote(html.unescape(page_html))
    found = {}
    for href, inner in ANCHOR_RE.findall(text):
        m = A8MAT_RE.search(href)
        if not m:
            continue
        mid = MID_RE.search(inner)
        found[m.group(1)] = found.get(m.group(1)) or (mid.group(1) if mid else "")
    # アンカー外（計測用の0.gif、ショートコード展開の崩れ等）にある a8mat も拾う
    for a8mat in A8MAT_RE.findall(text):
        found.setdefault(a8mat, "")
    return list(found.items())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--site", default=SITE)
    ap.add_argument("--urls", type=Path, help="調べるURLの一覧（1行1URL）。省略時はサイトマップ")
    ap.add_argument("--map", type=Path, default=ROOT / "data" / "affiliate" / "a8_link_map.csv")
    ap.add_argument("--out", type=Path, default=ROOT / "reports" / "affiliate" / date.today().isoformat())
    ap.add_argument("--wait", type=float, default=1.0, help="ページ取得の間隔（秒）")
    args = ap.parse_args()
    site = args.site.rstrip("/")

    if args.urls:
        urls = [u.strip() for u in args.urls.read_text(encoding="utf-8").splitlines() if u.strip()]
    else:
        urls = sitemap_urls(site)
        if not urls:
            print("サイトマップが取れないため、記事マスタのURLを調べます", file=sys.stderr)
            urls = master_urls(site)
    top = site + "/"
    if top not in urls:
        urls.insert(0, top)
    urls = list(dict.fromkeys(urls))

    programs = load_programs()
    a8map = load_map(args.map)
    rows, errors = [], []
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] {url}", file=sys.stderr)
        try:
            links = extract(fetch(url))
        except Exception as e:
            errors.append((url, str(e)))
            continue
        for a8mat, mid in links:
            rows.append({"page": url, "a8mat": a8mat, "mid": mid})
        time.sleep(args.wait)

    # バナーで判明した a8mat → mid を、同じ a8mat のテキストリンクにも当てはめる
    learned = {r["a8mat"]: r["mid"] for r in rows if r["mid"]}
    for r in rows:
        r["program_id"] = r["mid"] or learned.get(r["a8mat"]) or a8map.get(r["a8mat"], "")
        r["program_name"] = programs.get(r["program_id"], "")

    args.out.mkdir(parents=True, exist_ok=True)
    with open(args.out / "a8_link_audit.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["page", "program_id", "program_name", "a8mat", "mid"])
        w.writeheader()
        w.writerows(rows)

    pages_ok = len(urls) - len(errors)
    by_program = defaultdict(set)
    for r in rows:
        if r["program_id"]:
            by_program[r["program_id"]].add(r["page"])
    print(f"\n調べたページ: {pages_ok} / 取得失敗: {len(errors)}")
    for pid, pages in sorted(by_program.items()):
        name = programs.get(pid, "（プログラム名不明）")
        sitewide = pages_ok and len(pages) / pages_ok >= SITEWIDE_RATIO
        submit = [top] if sitewide else sorted(pages, key=lambda u: (u != top, u))
        (args.out / f"a8_submit_{pid}.txt").write_text("\n".join(submit) + "\n", encoding="utf-8")
        note = "全ページ表示の可能性→トップページのみ" if sitewide else f"{len(submit)}件"
        if len(submit) > SUBMIT_LIMIT:
            note += f"（{SUBMIT_LIMIT}件ずつ分けて提出）"
        print(f"  {pid} {name}: {note} → a8_submit_{pid}.txt")

    unmapped = sorted({r["a8mat"] for r in rows if not r["program_id"]})
    if unmapped:
        with open(args.out / "a8_unmapped.csv", "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["a8mat", "program_id", "pages"])
            for a in unmapped:
                w.writerow([a, "", " ".join(sorted({r["page"] for r in rows if r["a8mat"] == a}))])
        print(f"\nプログラム不明の a8mat が {len(unmapped)} 件 → a8_unmapped.csv を確認し、"
              f"{args.map.relative_to(ROOT) if args.map.is_relative_to(ROOT) else args.map} に追記して再実行")
    for url, err in errors:
        print(f"  取得失敗: {url} ({err})", file=sys.stderr)


if __name__ == "__main__":
    main()
