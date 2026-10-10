#!/usr/bin/env python3
"""取り込んだ GSC スナップショットを分析し、Markdown レポートと施策候補 CSV を出力する。

使い方:
    python3 scripts/gsc_analyze.py [--snapshot 2026-10-10]

前提: scripts/gsc_import.py で data/gsc/<snapshot>/{last3m,last28d,last7d}/ が作成済み。
出力:
    reports/gsc/<snapshot>/report.md
    reports/gsc/<snapshot>/{pages,ctr_gap,striking_queries,rising_queries,url_issues}.csv
"""
import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "gsc"
REPORT_DIR = ROOT / "reports" / "gsc"
SITE = "https://saiyo-ura.com"

# 記事スラッグ → テーマ（上から順に最初に一致したもの）
THEMES = [
    ("OpenWork・転職会議（口コミサイト）", r"openwork|tenshokukaigi"),
    ("IPA試験・資格", r"haishi|ipa-|exam|itpassport|aws-|linuc|lpic|kihonjoho|skill-exam|ouyou|sap"),
    ("企業研究（年収・難易度）", r"fujitsu|nec-|nttdata|hitachi|ntt|ibm|accenture|sier|nri|canon|toshiba|panasonic"),
    ("求人票・ブラック企業の見抜き方", r"black|kyujin|job-posting|instant-offer|holidays|kanbu|boshu"),
    ("転職エージェント", r"agent|recruit|jac|doda|bizreach|assign"),
    ("選考対策（書類・面接）", r"syorui|rejection|rirekisho|mensetsu|interview|shokumu"),
]


def load(snapshot: str, period: str, name: str) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / snapshot / period / f"{name}.csv")


def classify_url(url: str) -> str:
    path = re.sub(r"^https?://[^/]+", "", url)
    if not url.startswith(SITE + "/"):
        return "ホスト不一致（www等）"
    if "#" in path or "?" in path:
        return "アンカー/パラメータ付き"
    if path.startswith("/saiyo-ura.com/"):
        return "壊れた相対リンク由来"
    if re.match(r"^/(tag|category|author)/", path):
        return "タグ/カテゴリ"
    if re.search(r"/page/\d+", path):
        return "ページ送り"
    if path == "/":
        return "トップ"
    return "記事"


def theme_of(path: str) -> str:
    for name, pattern in THEMES:
        if re.search(pattern, path):
            return name
    return "その他"


def weighted_position(df: pd.DataFrame) -> float:
    return (df.position * df.impressions).sum() / df.impressions.sum()


def site_ctr_curve(queries: pd.DataFrame) -> pd.Series:
    """自サイトのクエリ実績から「順位帯ごとの標準 CTR（中央値）」を作る。"""
    q = queries[queries.impressions >= 20].copy()
    q["bucket"] = q.position.clip(1, 20).round().astype(int)
    curve = q.groupby("bucket").ctr.median()
    # 単調減少に補正（サンプル不足の帯で逆転しないように）
    return curve.reindex(range(1, 21)).ffill().bfill().cummin()


def per_day(df: pd.DataFrame, key: str, days: int, suffix: str) -> pd.DataFrame:
    out = df.set_index(key)[["clicks", "impressions", "position"]].copy()
    out["clicks"] = out.clicks / days
    out["impressions"] = out.impressions / days
    return out.add_suffix(suffix)


def momentum(t3m, t28, t7, key, d3m, d28, d7) -> pd.DataFrame:
    """直近28日 vs それ以前（3か月から28日を引いた期間）の日次平均で伸び率を出す。"""
    m = per_day(t3m, key, d3m, "_3m").join(per_day(t28, key, d28, "_28d"), how="outer") \
        .join(per_day(t7, key, d7, "_7d"), how="outer").fillna({c: 0 for c in
              ["clicks_3m", "clicks_28d", "clicks_7d", "impressions_3m", "impressions_28d", "impressions_7d"]})
    prior_days = d3m - d28
    m["clicks_prior"] = (m.clicks_3m * d3m - m.clicks_28d * d28).clip(lower=0) / prior_days
    m["impressions_prior"] = (m.impressions_3m * d3m - m.impressions_28d * d28).clip(lower=0) / prior_days
    m["imp_growth"] = (m.impressions_28d + 1) / (m.impressions_prior + 1)
    m["click_growth"] = (m.clicks_28d + 0.2) / (m.clicks_prior + 0.2)
    return m


def md_table(df: pd.DataFrame, fmt: dict | None = None) -> str:
    fmt = fmt or {}
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join("---:" if pd.api.types.is_numeric_dtype(df[c]) else "---" for c in cols) + "|"]
    for _, row in df.iterrows():
        cells = []
        for c in cols:
            v = row[c]
            if c in fmt:
                cells.append(fmt[c].format(v))
            elif isinstance(v, float):
                cells.append(f"{v:,.1f}")
            elif isinstance(v, int):
                cells.append(f"{v:,}")
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", help="data/gsc/ 配下の日付フォルダ（省略時は最新）")
    args = parser.parse_args()
    snapshot = args.snapshot or sorted(p.name for p in DATA_DIR.iterdir() if re.match(r"\d{4}-\d{2}-\d{2}$", p.name))[-1]
    manifest = json.loads((DATA_DIR / snapshot / "manifest.json").read_text())
    days = {p: len(load(snapshot, p, "daily")) for p in ("last3m", "last28d", "last7d")}
    out_dir = REPORT_DIR / snapshot
    out_dir.mkdir(parents=True, exist_ok=True)
    pct = "{:.1%}"
    r = []  # レポート本文

    # ---- 1. サマリー ----
    r.append(f"# GSC分析レポート（{snapshot} 取得）\n")
    r.append(f"- 対象: {SITE} / 検索タイプ: ウェブ")
    r.append(f"- データ期間: 3か月 {manifest['last3m']['date_from']}〜{manifest['last3m']['date_to']}"
             f"（クエリ・ページ表は GSC 画面エクスポートのため上位1,000行まで、匿名化クエリは含まれない）\n")
    summary = []
    for period, label in [("last3m", "過去3か月"), ("last28d", "過去28日"), ("last7d", "過去7日")]:
        dev = load(snapshot, period, "devices")
        c, i = dev.clicks.sum(), dev.impressions.sum()
        summary.append({"期間": label, "日数": days[period], "クリック": int(c), "表示回数": int(i),
                        "クリック/日": c / days[period], "表示/日": i / days[period], "CTR": c / i,
                        "平均順位": weighted_position(dev)})
    r.append("## 1. サマリー\n")
    r.append(md_table(pd.DataFrame(summary), {"CTR": pct, "平均順位": "{:.2f}"}))

    daily = load(snapshot, "last3m", "daily")
    daily["date"] = pd.to_datetime(daily.date)
    daily["週"] = daily.date.dt.to_period("W-MON").map(lambda p: p.start_time.strftime("%m/%d") + "〜")
    weekly = daily.groupby("週", sort=False).apply(lambda g: pd.Series({
        "日数": len(g), "クリック": int(g.clicks.sum()), "表示回数": int(g.impressions.sum()),
        "CTR": g.clicks.sum() / g.impressions.sum(), "平均順位": weighted_position(g)}), include_groups=False).reset_index()
    weekly = weekly[weekly.日数 == 7]
    r.append("\n### 週次推移（7日揃っている週のみ）\n")
    r.append(md_table(weekly, {"CTR": pct, "平均順位": "{:.2f}", "日数": "{:.0f}", "クリック": "{:,.0f}", "表示回数": "{:,.0f}"}))

    dev = load(snapshot, "last28d", "devices")
    r.append("\n### デバイス別（過去28日）\n")
    r.append(md_table(dev.rename(columns={"device": "デバイス", "clicks": "クリック", "impressions": "表示回数",
                                          "ctr": "CTR", "position": "平均順位"}), {"CTR": pct, "平均順位": "{:.2f}"}))

    # ---- 2. URL 品質 ----
    pages = {p: load(snapshot, p, "pages") for p in days}
    p3 = pages["last3m"].copy()
    p3["種別"] = p3.page.map(classify_url)
    url_summary = p3.groupby("種別").agg(URL数=("page", "count"), クリック=("clicks", "sum"), 表示回数=("impressions", "sum")).reset_index()
    issues = p3[~p3.種別.isin(["記事", "トップ", "アンカー/パラメータ付き"])]
    issues.to_csv(out_dir / "url_issues.csv", index=False)
    r.append("\n## 2. URLの内訳とインデックス上の問題（過去3か月）\n")
    r.append(md_table(url_summary))
    r.append("\n「アンカー/パラメータ付き」は検索結果に表示された目次ジャンプリンク（`#index_id`）で、"
             "記事単位の集計からは除外しています。以下は本来インデックスされるべきでないURLです。\n")
    r.append(md_table(issues[["page", "種別", "impressions"]].rename(columns={"impressions": "表示回数"})))

    # ---- 3. 記事別 ----
    arts = {p: df[df.page.map(classify_url) == "記事"].assign(page=lambda d: d.page.str.replace(SITE, "", regex=False))
            for p, df in pages.items()}
    pm = momentum(arts["last3m"], arts["last28d"], arts["last7d"], "page", days["last3m"], days["last28d"], days["last7d"])
    pm["theme"] = pm.index.map(theme_of)
    pm["ctr_3m"] = (pm.clicks_3m / pm.impressions_3m.replace(0, pd.NA)).astype(float)
    pm.sort_values("clicks_3m", ascending=False).to_csv(out_dir / "pages.csv", float_format="%.3f")

    n_art = len(arts["last3m"])
    n_click = (arts["last3m"].clicks > 0).sum()
    top10_share = arts["last3m"].nlargest(10, "clicks").clicks.sum() / arts["last3m"].clicks.sum()
    r.append("\n## 3. 記事別パフォーマンス\n")
    r.append(f"- 表示実績のある記事: {n_art}本 / うちクリック発生: {n_click}本 / 上位10記事のクリック集中度: {top10_share:.0%}\n")

    theme = pm.groupby("theme").agg(**{"記事数": ("clicks_3m", "size"), "クリック/日(28日)": ("clicks_28d", "sum"),
                                       "クリック/日(以前)": ("clicks_prior", "sum"), "表示/日(28日)": ("impressions_28d", "sum")})
    theme["伸び率"] = theme["クリック/日(28日)"] / theme["クリック/日(以前)"].replace(0, pd.NA)
    theme = theme.sort_values("クリック/日(28日)", ascending=False).reset_index().rename(columns={"theme": "テーマ"})
    r.append("### テーマ別（日次平均クリック: 直近28日 vs それ以前の64日）\n")
    r.append(md_table(theme, {"伸び率": "{:.2f}x", "記事数": "{:.0f}"}))

    top = pm.sort_values("clicks_28d", ascending=False).head(20).reset_index()
    top = top[["page", "theme", "clicks_28d", "clicks_prior", "clicks_7d", "impressions_28d", "position_28d"]]
    top.columns = ["記事", "テーマ", "クリック/日(28日)", "クリック/日(以前)", "クリック/日(7日)", "表示/日(28日)", "順位(28日)"]
    r.append("\n### 上位20記事（直近28日のクリック順）\n")
    r.append(md_table(top))

    rising = pm[(pm.impressions_28d >= 10)].sort_values("imp_growth", ascending=False).head(10).reset_index()
    rising = rising[["page", "impressions_prior", "impressions_28d", "impressions_7d", "clicks_28d", "position_28d"]]
    rising.columns = ["記事", "表示/日(以前)", "表示/日(28日)", "表示/日(7日)", "クリック/日(28日)", "順位(28日)"]
    r.append("\n### 表示回数が急伸している記事（伸びしろの早期発見）\n")
    r.append(md_table(rising))

    # 直近28日・直近7日の両方で以前を下回っている記事のみ（一時的なブレを除外）
    falling = pm[(pm.clicks_prior >= 1) & (pm.clicks_7d < pm.clicks_prior)].assign(drop=lambda d: d.clicks_28d - d.clicks_prior) \
        .sort_values("drop").head(10).reset_index()
    falling = falling[falling["drop"] < 0][["page", "clicks_prior", "clicks_28d", "clicks_7d", "position_3m", "position_28d"]]
    falling.columns = ["記事", "クリック/日(以前)", "クリック/日(28日)", "クリック/日(7日)", "順位(3か月)", "順位(28日)"]
    r.append("\n### クリックが落ちている記事（リライト優先候補）\n")
    r.append(md_table(falling))

    # ---- 4. CTR ギャップ ----
    q3 = load(snapshot, "last3m", "queries")
    curve = site_ctr_curve(q3)
    a3 = arts["last3m"].copy()
    a3["標準CTR"] = a3.position.clip(1, 20).round().astype(int).map(curve)
    a3["取りこぼしクリック"] = (a3.impressions * (a3.標準CTR - a3.ctr)).round()
    gap = a3[(a3.position <= 15) & (a3.impressions >= 300)].sort_values("取りこぼしクリック", ascending=False)
    gap.to_csv(out_dir / "ctr_gap.csv", index=False)
    r.append("\n## 4. タイトル・ディスクリプション改善候補（CTRギャップ）\n")
    r.append("自サイトのクエリ実績から順位帯ごとのCTR中央値（標準CTR）を算出し、"
             "同じ順位なのにCTRが低い記事を抽出しました（過去3か月・平均順位15位以内・表示300回以上）。\n")
    r.append("標準CTR: " + ", ".join(f"{k}位 {v:.1%}" for k, v in curve.items() if k <= 10) + "\n")
    g = gap.head(15)[["page", "impressions", "clicks", "ctr", "標準CTR", "position", "取りこぼしクリック"]]
    g.columns = ["記事", "表示回数", "クリック", "CTR", "標準CTR", "順位", "取りこぼしクリック"]
    r.append(md_table(g, {"CTR": pct, "標準CTR": pct, "順位": "{:.1f}", "取りこぼしクリック": "{:,.0f}"}))

    # ---- 5. クエリ ----
    qs = {p: load(snapshot, p, "queries") for p in days}
    striking = qs["last3m"][(qs["last3m"].position.between(4, 20)) & (qs["last3m"].impressions >= 100)].copy()
    striking["1位圏到達時の見込み増"] = (striking.impressions * (curve[3] - striking.ctr)).clip(lower=0).round()
    striking = striking.sort_values("1位圏到達時の見込み増", ascending=False)
    striking.to_csv(out_dir / "striking_queries.csv", index=False)
    r.append("\n## 5. クエリ分析\n")
    r.append("### あと一歩クエリ（過去3か月・平均4〜20位・表示100回以上）\n")
    r.append(f"3位相当の標準CTR（{curve[3]:.1%}）まで上がった場合の追加クリック見込み順。\n")
    s = striking.head(25)[["query", "impressions", "clicks", "ctr", "position", "1位圏到達時の見込み増"]]
    s.columns = ["クエリ", "表示回数", "クリック", "CTR", "順位", "見込み増"]
    r.append(md_table(s, {"CTR": pct, "順位": "{:.1f}", "見込み増": "{:,.0f}"}))

    qm = momentum(qs["last3m"], qs["last28d"], qs["last7d"], "query", days["last3m"], days["last28d"], days["last7d"])
    new_q = qm[(qm.impressions_prior == 0) & (qm.impressions_28d * days["last28d"] >= 50)] \
        .sort_values("impressions_28d", ascending=False)
    rq = qm[(qm.impressions_28d * days["last28d"] >= 50)].sort_values("imp_growth", ascending=False)
    rq.to_csv(out_dir / "rising_queries.csv", float_format="%.3f")
    r.append("\n### 直近28日で新たに出現・急伸したクエリ（需要の変化）\n")
    nq = rq.head(20).reset_index()[["query", "impressions_prior", "impressions_28d", "impressions_7d", "clicks_28d", "position_28d"]]
    nq.columns = ["クエリ", "表示/日(以前)", "表示/日(28日)", "表示/日(7日)", "クリック/日(28日)", "順位(28日)"]
    r.append(md_table(nq))
    r.append(f"\n（以前は表示ゼロで、直近28日に50回以上表示された新規クエリ: {len(new_q)}件）")

    zero = qs["last3m"][(qs["last3m"].clicks == 0)].sort_values("impressions", ascending=False).head(15)
    r.append("\n### 表示されているがクリックゼロの上位クエリ（検索意図とのズレ確認用）\n")
    z = zero[["query", "impressions", "position"]]
    z.columns = ["クエリ", "表示回数", "順位"]
    r.append(md_table(z, {"順位": "{:.1f}"}))

    (out_dir / "report.md").write_text("\n".join(r) + "\n", encoding="utf-8")
    print(f"wrote {out_dir.relative_to(ROOT)}/report.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
