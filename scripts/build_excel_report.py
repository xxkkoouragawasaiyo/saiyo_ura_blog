#!/usr/bin/env python3
"""GSC・ASPデータと分析所見から、ブログ改善レポート（Excel）を作成する。

使い方:
    python3 scripts/build_excel_report.py [--snapshot 2026-10-10]

入力:
    data/gsc/<snapshot>/                  scripts/gsc_import.py で取り込んだGSCデータ
    data/affiliate/<snapshot>/            ASPレポート（UTF-8）
    data/articles/article_master.csv      記事マスタ（テーマ・競合グループ・推奨案件・関連クエリのパターン）
    scripts/report_notes_2026_10_10.py    所見（記事別の修正点・競合グループの判定など）
出力:
    reports/excel/saiyo-ura_改善レポート_<snapshot>.xlsx
"""
import argparse
import warnings
import re
import sys
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
warnings.filterwarnings("ignore", message="This pattern is interpreted as a regular expression")
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import report_notes_2026_10_10 as notes  # noqa: E402

SITE = "https://saiyo-ura.com"
FONT = "Meiryo UI"
NAVY, LIGHT, ZEBRA = "1F3864", "D9E1F2", "F2F2F2"
RANK_FILL = {"S": "F8CBAD", "A": "FFE699", "B": "E2EFDA", "C": "DDEBF7", "D": "F2F2F2"}
RANK_TIMING = {"S": "今週〜2週間", "A": "今月中", "B": "来月", "C": "3か月以内（統合・整理）", "D": "様子見・対応不要"}
THEME_WEIGHT = {
    "口コミサイト活用": 1.0, "転職サービス評判": 1.0, "IT企業研究": 0.8, "求人票・ブラック企業": 0.6,
    "選考対策": 0.6, "SIer・SES業界研究": 0.5, "キャリア・働き方": 0.4, "IPA試験・IT資格": 0.35, "サイト基本ページ": 0.0,
}
CLUSTER_BONUS = {"強": 30, "中": 10}
# 目標CTR（平均掲載順位別）。サイト内で表示300回以上の記事の実績（3か月）を基に、上位水準として設定した想定値。
TARGET_CTR = [(1, 0.30), (2, 0.20), (3, 0.14), (4, 0.10), (5, 0.08), (6, 0.06), (7, 0.05), (8, 0.045), (9, 0.04), (10, 0.035)] + \
             [(i, 0.025) for i in range(11, 16)] + [(i, 0.012) for i in range(16, 21)]

thin = Side(style="thin", color="BFBFBF")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)


# ---------------------------------------------------------------- データ準備
def load(snapshot: str):
    g = ROOT / "data" / "gsc" / snapshot
    a = ROOT / "data" / "affiliate" / snapshot
    d = {}
    for period in ("last3m", "last28d", "last7d"):
        for name in ("pages", "queries", "daily", "devices"):
            d[f"{name}_{period}"] = pd.read_csv(g / period / f"{name}.csv")
    d["master"] = pd.read_csv(ROOT / "data" / "articles" / "article_master.csv")
    d["a8_monthly"] = pd.read_csv(a / "a8_monthly_202601-202610.csv")
    d["a8_programs"] = pd.read_csv(a / "a8_programs_202601-202610.csv")
    d["vc_adv"] = pd.read_csv(a / "valuecommerce_advertisers_260910-261010.csv")
    d["vc_daily"] = pd.read_csv(a / "valuecommerce_daily_260910-261010.csv")
    d["moshimo"] = pd.read_csv(a / "moshimo_site_kpi.csv")
    return d


def classify_url(url: str) -> str:
    path = re.sub(r"^https?://[^/]+", "", url)
    if not url.startswith(SITE + "/"):
        return "ホスト不一致（www付き）"
    if "#" in path or "?" in path:
        return "目次アンカー付き"
    if path.startswith("/saiyo-ura.com/"):
        return "壊れたURL（https抜けのリンク）"
    if re.match(r"^/(tag|category|author)/", path):
        return "タグ/カテゴリ"
    if path == "/":
        return "トップ"
    if not path.endswith("/") or "]" in path:
        return "不正な形式（末尾スラッシュ欠落・記号混入）"
    return "記事"


def target_ctr(pos: float) -> float:
    if pd.isna(pos):
        return 0.0
    return dict(TARGET_CTR)[int(min(20, max(1, round(pos))))]


def build_articles(d) -> pd.DataFrame:
    days = {"last3m": len(d["daily_last3m"]), "last28d": len(d["daily_last28d"]), "last7d": len(d["daily_last7d"])}
    frames = {}
    for period in days:
        p = d[f"pages_{period}"]
        p = p[p.page.map(classify_url) == "記事"].copy()
        p["slug"] = p.page.str.replace(SITE, "", regex=False)
        frames[period] = p.set_index("slug")[["clicks", "impressions", "ctr", "position"]]
    df = d["master"].set_index("slug")
    for period, f in frames.items():
        df = df.join(f.add_suffix("_" + period.replace("last", "")))
    for c in df.columns:
        if c.startswith(("clicks_", "impressions_")):
            df[c] = df[c].fillna(0).astype(int)
    prior_days = days["last3m"] - days["last28d"]
    df["cpd_prior"] = (df.clicks_3m - df.clicks_28d).clip(lower=0) / prior_days
    df["cpd_28d"] = df.clicks_28d / days["last28d"]
    df["ipd_prior"] = (df.impressions_3m - df.impressions_28d).clip(lower=0) / prior_days
    df["ipd_28d"] = df.impressions_28d / days["last28d"]
    df["ctr_28d_calc"] = (df.clicks_28d / df.impressions_28d.where(df.impressions_28d > 0)).fillna(0.0)
    df["monthly_clicks"] = df.cpd_28d * 30
    df["potential"] = [
        max(0.0, ipd * 30 * (target_ctr(pos) - ctr)) if not pd.isna(pos) else 0.0
        for ipd, pos, ctr in zip(df.ipd_28d, df.position_28d, df.ctr_28d_calc)
    ]

    # 関連クエリ（推定）: クエリの空白を除いて記事ごとのパターンで照合
    q = d["queries_last3m"].copy()
    q["norm"] = q["query"].str.lower().str.replace(r"\s+", "", regex=True)
    related, lost, matched = {}, {}, {}
    for slug, row in df.iterrows():
        hit = q[q.norm.str.contains(row.query_pattern, regex=True, na=False)] if row.query_pattern != "^$" else q.iloc[0:0]
        matched[slug] = hit.index
        related[slug] = " / ".join(f"{r.query}（{r.impressions:,}表示・{r.position:.1f}位・CTR{r.ctr:.1%}）"
                                   for r in hit.nlargest(3, "impressions").itertuples())
        cand = hit[hit.position.between(4, 30)].assign(gap=lambda x: x.impressions * (0.072 - x.ctr)).nlargest(1, "gap")
        lost[slug] = "" if cand.empty else f"{cand.iloc[0]['query']}（{cand.iloc[0].impressions:,}表示・{cand.iloc[0].position:.1f}位）"
    df["related"] = pd.Series(related)
    df["lost_query"] = pd.Series(lost)
    d["query_matches"] = matched

    # 傾向
    def trend(r):
        if r.impressions_3m < 30:
            return "表示ほぼなし"
        if r.impressions_28d == 0 and r.impressions_3m >= 100:
            return "直近28日は表示なし"
        if r.ipd_prior < 1 and r.ipd_28d >= 5:
            return "新規出現"
        if r.cpd_prior >= 0.3 and r.cpd_28d >= r.cpd_prior * 1.5:
            return "急伸"
        if r.cpd_prior >= 0.3 and r.cpd_28d <= r.cpd_prior * 0.7:
            return "下落"
        if r.ipd_prior >= 3 and r.ipd_28d >= r.ipd_prior * 1.8:
            return "表示急伸"
        return "横ばい"
    df["trend"] = df.apply(trend, axis=1)

    # カニバリ判定
    cluster_size = df.groupby("cluster").size()
    def cannibal(r):
        info = notes.CLUSTERS.get(r.cluster)
        others = [s for s in df.index[df.cluster == r.cluster] if s != r.name and df.loc[s, "impressions_3m"] >= 1]
        if r.cluster == "-" or cluster_size.get(r.cluster, 1) <= 1 or not info:
            return "なし", "同じ意図の記事なし"
        lvl = info["level"]
        names = "、".join(others[:5]) + ("ほか" if len(others) > 5 else "")
        return lvl, f"【{r.cluster}】競合相手：{names}" if lvl != "なし" else f"【{r.cluster}】意図は分かれている"
    cv = df.apply(cannibal, axis=1, result_type="expand")
    df["cannibal_level"], df["cannibal_note"] = cv[0], cv[1]

    # 診断（自動）
    def diag(r):
        imp, pos, ctr = r.impressions_3m, r.position_3m, (r.clicks_3m / r.impressions_3m if r.impressions_3m else 0)
        if r.theme == "サイト基本ページ":
            return "サイト基本ページ（集客対象外）"
        if imp < 50:
            return f"3か月の表示{imp}回でほぼ評価されていない。検索需要が小さいか、同テーマの他記事に評価を取られている。"
        parts = []
        if pos > 20:
            parts.append(f"平均{pos:.1f}位で2ページ目以降。検索意図とのズレか、内容不足。")
        elif pos > 10:
            parts.append(f"平均{pos:.1f}位で1ページ目の手前（あと一歩）。")
        else:
            t = target_ctr(pos)
            if ctr < t * 0.6 and imp >= 300:
                parts.append(f"{pos:.1f}位でCTR{ctr:.1%}（同順位の目標{t:.0%}を大きく下回る）。タイトル・説明文が検索意図に合っていない可能性。")
            else:
                parts.append(f"{pos:.1f}位・CTR{ctr:.1%}で水準並み以上。")
        if r.trend in ("急伸", "表示急伸", "新規出現"):
            parts.append(f"直近28日で{r.trend}（クリック/日 {r.cpd_prior:.1f}→{r.cpd_28d:.1f}、表示/日 {r.ipd_prior:.0f}→{r.ipd_28d:.0f}）。")
        elif r.trend == "直近28日は表示なし":
            parts.append("直近28日は検索結果に表示されていない（評価が他記事に移った可能性）。")
        elif r.trend == "下落":
            parts.append(f"クリックが下落（クリック/日 {r.cpd_prior:.1f}→{r.cpd_28d:.1f}）。")
        if r.lost_query:
            parts.append(f"取りこぼしクエリ：{r.lost_query}。")
        return "".join(parts)

    def key_query(r):
        if r.lost_query:
            return r.lost_query.split("（")[0]
        if r.related:
            return r.related.split("（")[0]
        return ""

    def seo_auto(r):
        imp, pos = r.impressions_3m, r.position_3m
        main = cluster_main.get(r.cluster)
        info = notes.CLUSTERS.get(r.cluster, {})
        q = key_query(r)
        qtxt = f"「{q}」" if q else "記事の主要キーワード（GSCで記事URLを絞り込んで表示クエリを確認）"
        if r.theme == "サイト基本ページ":
            return "対応不要（noindexにはしない）。"
        prefix = ""
        role, role_note = notes.ROLES.get(r.name, ("", ""))
        main = next((k for k, v in notes.ROLES.items() if v[0] == "main" and k in df.index and df.loc[k, "cluster"] == r.cluster), main)
        if role == "merge":
            return (f"【統合対象】{main}へ統合し、本記事のURLは301リダイレクト。統合前に、本記事だけにある情報（数字・事例・人事の本音）を親記事へ移す。"
                    f"（グループ方針：{info.get('action', '')}）")
        if role == "main":
            prefix = f"【親記事（統合先）】担当：{role_note}。統合する子記事の固有情報を取り込み、同グループの記事から内部リンクを集める。\n"
        elif role == "keep":
            prefix = f"【差別化して残す】担当：{role_note}。親記事（{main}）と重複する説明は3行要約＋リンクに置き換える。\n"
        if imp < 50:
            return prefix + "表示がほぼないため、①需要がない→内部リンク用として残す、②同テーマの記事に評価を取られている→統合、のどちらかを判断。追記は後回し。"
        if pos > 20:
            return prefix + f"2ページ目以降。上位記事の見出し構成と比べ、{qtxt}への答えを冒頭に追加。網羅性を補っても上がらなければ統合を検討。"
        if pos > 10:
            return prefix + f"1ページ目の手前。{qtxt}を含む見出しを追加して網羅性を補強し、同テーマの上位記事から内部リンクを追加して1ページ目入りを狙う。"
        if q:
            return prefix + f"順位は1ページ目。本文は大きく変えず、{qtxt}向けの見出し追加と導線の設置に留める。"
        return prefix + "順位は1ページ目。本文は大きく変えず、導線の設置を優先。"

    def title_auto(r):
        if notes.ROLES.get(r.name, ("",))[0] == "merge":
            return "-（統合するため不要）"
        if r.theme == "サイト基本ページ" or r.impressions_3m < 50:
            return "-"
        ctr = r.clicks_3m / r.impressions_3m if r.impressions_3m else 0
        q = r.related.split("（")[0] if r.related else ""
        if r.position_3m > 10:
            return f"順位の改善が先。タイトルは「{q}」を含む形に整える程度に。" if q else "順位の改善が先。タイトルの変更は後回し。"
        if ctr < target_ctr(r.position_3m) * 0.6:
            return (f"CTRが低い。タイトル先頭に「{q}」を入れ、疑問形のクエリには説明文の冒頭で答えを言い切る。「現役IT人事」の要素は残す。"
                    if q else "CTRが低い。GSCで表示クエリを確認し、タイトルで検索意図に即答する形に変更。")
        return f"大きな変更は不要。タイトルに「{q}」が入っていなければ追加。" if q else "大きな変更は不要。"

    def cta_auto(r):
        offer = str(r.offer).split("/")[0]
        t = r.theme
        if t == "サイト基本ページ":
            return "アフィリエイトは置かない。"
        base = {
            "口コミサイト活用": "口コミの読み方・見分け方の見出しの末尾に、人事の本音ボックス「1サイトだけだと偏るので2サイトで裏取りを」→転職会議ボタン。",
            "IT企業研究": f"年収・難易度の表の直下に「中途の条件は応募経路と交渉で変わる。エージェント経由なら面接傾向と年収レンジを事前に聞ける」→{offer}。記事末に「入社後のギャップは口コミで確認」→転職会議。",
            "SIer・SES業界研究": f"一覧表・ランキングの直後に「自分の経験でどのTierに入れるかはスカウトを受けると分かる」→{offer}。",
            "IPA試験・IT資格": ("転職意欲が低い読者のためソフト導線のみ。「資格は採用でどう評価されるか」の見出しに「経験の評価はスカウト型に職務経歴を登録すると分かる」→レバテックダイレクト。" if "neo" not in offer else f"若手・未経験の読者が中心。記事末に「資格より先に、未経験でも応募できる求人を知っておくと勉強の優先順位が決まる」→{offer}（ソフト導線）。"),
            "転職サービス評判": "冒頭の結論ボックスに当該サービスのボタン（提携済みの場合）。「向いていない人」に代わりのサービスを提示。提携していない場合は提携申請か、提携済みの代替案件へ。",
            "選考対策": f"「自分で直すのが難しい人へ」の見出しで、エージェントの無料書類添削・面接対策を紹介→{offer}。",
            "求人票・ブラック企業": "「応募前の確認方法」の見出しで「求人票に書かれない実態は口コミで確認」→転職会議。記事末に「内部情報はエージェント経由で聞ける」→リクルートエージェント。",
            "キャリア・働き方": f"記事末に「まず自分の市場価値を確認」として{offer}を紹介。本文中の広告は控える。",
        }.get(t, "記事末に関連する案件を1つ。")
        if r.impressions_3m < 50:
            base = "表示がほぼないため導線の設置は後回し（統合・リライト後に設置）。"
        if notes.ROLES.get(r.name, ("",))[0] == "merge":
            base = "統合するため設置しない（統合先の記事で設置）。"
        return base

    cluster_main = df.sort_values("impressions_3m", ascending=False).groupby("cluster").head(1).reset_index().set_index("cluster")["slug"].to_dict()
    df["diag"] = df.apply(diag, axis=1)
    df["seo"] = df.apply(seo_auto, axis=1)
    df["title_fix"] = df.apply(title_auto, axis=1)
    df["cta"] = df.apply(cta_auto, axis=1)
    df["effort"] = df.apply(lambda r: "小" if r.impressions_3m < 300 or notes.ROLES.get(r.name, ("",))[0] == "merge" else "中", axis=1)
    df["boost"] = 0
    df["fixed_rank"] = pd.NA
    for slug, n in notes.ARTICLES.items():
        for k, col in (("diag", "diag"), ("seo", "seo"), ("title", "title_fix"), ("cta", "cta"), ("effort", "effort"), ("boost", "boost")):
            if k in n:
                df.loc[slug, col] = n[k]
        if "rank" in n:
            df.loc[slug, "fixed_rank"] = n["rank"]
    df["manual"] = df.index.isin(list(notes.ARTICLES))

    # 優先スコア = (月間クリック + 取りこぼし見込み) × テーマの収益重み × 提携状況 + 競合ボーナス + 個別加点
    w = df.theme.map(THEME_WEIGHT).fillna(0.3) * df.offer.map(lambda o: 0.5 if "要提携" in str(o) else 1.0)
    df["score"] = (df.monthly_clicks + df.potential) * w + df.cannibal_level.map(CLUSTER_BONUS).fillna(0) * (df.impressions_3m >= 100) + df.boost
    df.loc[df.theme == "サイト基本ページ", "score"] = df.boost
    fixed = df[df.fixed_rank.notna()].sort_values("fixed_rank")
    rest = df[df.fixed_rank.isna()].sort_values("score", ascending=False)
    df = pd.concat([fixed, rest])
    df["rank"] = range(1, len(df) + 1)
    df["tier"] = pd.cut(df["rank"], [0, 9, 30, 60, 100, 10_000], labels=list("SABCD")).astype(str)
    df.loc[(df.impressions_3m < 30) & (df.tier.isin(["A", "B"])) & ~df.manual, "tier"] = "C"
    # カニバリ「強」のグループに属する記事は統合作業の対象なので、D（対応不要）にはしない
    df.loc[(df.cannibal_level == "強") & (df.tier == "D"), "tier"] = "C"
    df.loc[df.index.map(lambda x: notes.ROLES.get(x, ("",))[0] == "merge") & (df.tier == "D"), "tier"] = "C"
    return df


# ---------------------------------------------------------------- 書式ヘルパー
def style_header(ws, row, ncol, col0=1):
    for c in range(col0, col0 + ncol):
        cell = ws.cell(row=row, column=c)
        cell.font = Font(name=FONT, bold=True, color="FFFFFF", size=10)
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER


def title(ws, text, sub=None):
    ws["A1"] = text
    ws["A1"].font = Font(name=FONT, bold=True, size=14, color=NAVY)
    if sub:
        ws["A2"] = sub
        ws["A2"].font = Font(name=FONT, size=9, color="595959")
    ws.sheet_view.showGridLines = False


def section(ws, row, text):
    ws.cell(row=row, column=1, value=text).font = Font(name=FONT, bold=True, size=12, color=NAVY)
    return row + 1


def write_table(ws, row, headers, rows, widths=None, fmts=None, wrap_cols=(), col0=1, zebra=True):
    """表を書き込み、次の空き行を返す。rows の要素は値または '=' で始まる式。"""
    for j, h in enumerate(headers):
        ws.cell(row=row, column=col0 + j, value=h)
    style_header(ws, row, len(headers), col0)
    for i, r in enumerate(rows, start=1):
        for j, v in enumerate(r):
            if isinstance(v, float) and pd.isna(v):
                v = None
            cell = ws.cell(row=row + i, column=col0 + j, value=v)
            cell.font = Font(name=FONT, size=10)
            cell.border = BORDER
            cell.alignment = Alignment(vertical="top", wrap_text=(headers[j] in wrap_cols))
            if fmts and headers[j] in fmts:
                cell.number_format = fmts[headers[j]]
            if zebra and i % 2 == 0:
                cell.fill = PatternFill("solid", fgColor=ZEBRA)
    if widths:
        for j, wdt in enumerate(widths):
            ws.column_dimensions[get_column_letter(col0 + j)].width = wdt
    return row + len(rows) + 2


def set_widths(ws, widths):
    for j, wdt in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(j)].width = wdt


# ---------------------------------------------------------------- シート
def sheet_guide(wb, d, snapshot, df):
    ws = wb.active
    ws.title = "目次・前提"
    title(ws, "採用のウラ側 ブログ改善レポート", f"作成日：{snapshot}　対象：{SITE}/　作成：GSC・ASPデータ分析")
    set_widths(ws, [26, 70, 16, 16])
    r = section(ws, 4, "シート一覧")
    sheets = [
        ("サマリー", "結論・主要指標・仮説の検証結果・最優先の対応"),
        ("良い点・悪い点", "現状のブログの強みと弱み（根拠データと対策つき）"),
        ("今後の方向性", "ポジショニング・注力テーマ・やめること・新規記事案・ロードマップ・KPI"),
        ("全記事_修正点", "全139記事の修正点を優先順に一覧化（診断・カニバリ・SEO・タイトル・導線・推奨案件）"),
        ("重点9記事_詳細", "最優先9記事のアクションプラン（分析・カニバリ・タイトル案・導線の位置とマイクロコピー）"),
        ("カニバリ分析", "記事グループごとの競合判定・根拠・解消案、複数記事に該当するクエリ"),
        ("URL・技術課題", "壊れたURL・不要なインデックスの詳細と修正手順"),
        ("GSC主要発見", "前回報告の発見1〜5の詳細"),
        ("クエリ機会", "あと一歩のクエリ・急伸クエリ・クリック0のクエリ"),
        ("推移・デバイス", "週次推移・期間別・デバイス別の数値"),
        ("アフィリエイト実績", "A8.net・バリューコマース・もしもアフィリエイトの実績と診断"),
    ]
    for name, desc in sheets:
        c = ws.cell(row=r, column=1, value=name)
        c.hyperlink = f"#'{name}'!A1"
        c.font = Font(name=FONT, size=10, color="0563C1", underline="single")
        ws.cell(row=r, column=2, value=desc).font = Font(name=FONT, size=10)
        r += 1

    r = section(ws, r + 1, "使用データ")
    g = d["daily_last3m"]
    rows = [
        ("Googleサーチコンソール", f"検索パフォーマンス（ウェブ）過去3か月 {g.date.iloc[0]}〜{g.date.iloc[-1]}／過去28日／過去7日。クエリ・ページは画面エクスポートの上位1,000行"),
        ("A8.net", "月次レポート・プログラム別（2026年1月〜10月）"),
        ("バリューコマース", "広告主別・日別（2026/09/10〜10/10）"),
        ("もしもアフィリエイト", "サイト別KPI（期間はエクスポート時の設定）"),
    ]
    r = write_table(ws, r, ["データ", "内容"], rows, wrap_cols=("内容",))

    r = section(ws, r, "前提・制約（必ずお読みください）")
    caveats = [
        "分析環境からサイトに接続できなかったため、記事本文と現在のアフィリエイトリンクの配置は確認していません。現在のタイトルは検索結果で確認できたものだけ記載しています。",
        "カニバリゼーションは推定です。GSCの画面エクスポートには「どのクエリでどの記事が表示されたか」の組み合わせが含まれないため、クエリの文言と記事のテーマから判定しました。確定には「カニバリ分析」シートの手順でGSCを確認してください。",
        "「関連クエリ（推定）」は、記事マスタ（data/articles/article_master.csv）のパターンでクエリを記事に割り当てたものです。1つのクエリが複数の記事に割り当たることがあります。",
        "クエリ表は上位1,000行で、匿名化されたクエリは含みません。クエリの合計はサイト全体の合計より小さくなります。サイト全体の合計はデバイス別の値を使っています。",
        "マイクロコピー中のサービス仕様（無料で口コミを見られる条件、年収の目安など）は公式情報で確認していません。掲載前に必ず公式サイトとASPの規約を確認してください。",
        "優先順位は「（月間クリック＋取りこぼし見込み）× テーマの収益性 ＋ カニバリの深刻度」のスコアに、人の判断（重点9記事の固定など）を加えて決めています。",
    ]
    for t in caveats:
        c = ws.cell(row=r, column=1, value="・" + t)
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
        c.font = Font(name=FONT, size=10)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[r].height = 42
        r += 1

    r = section(ws, r + 1, "目標CTR（平均掲載順位別）※「全記事_修正点」の取りこぼし見込みの計算に使用。数値を変えると再計算されます")
    ws.cell(row=r, column=1, value="想定値の根拠：サイト内で3か月の表示300回以上の記事の実績（6〜9位の中央値は約3.5%、5位は約10%）を基に、上位水準として設定。").font = Font(name=FONT, size=9, color="595959")
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
    r += 1
    start = r
    write_table(ws, r, ["平均掲載順位", "目標CTR"], [(p, c) for p, c in TARGET_CTR], fmts={"目標CTR": "0.0%"}, zebra=False)
    for i in range(len(TARGET_CTR)):
        ws.cell(row=start + 1 + i, column=2).font = Font(name=FONT, size=10, color="0000FF")
        ws.cell(row=start + 1 + i, column=2).fill = PatternFill("solid", fgColor="FFF2CC")
    d["ctr_range"] = f"'目次・前提'!$B${start + 1}:$B${start + len(TARGET_CTR)}"
    r = start + len(TARGET_CTR) + 2

    r = section(ws, r, "用語")
    terms = [
        ("CTR", "検索結果に表示された回数のうち、クリックされた割合"),
        ("平均掲載順位", "検索結果での平均順位。記事単位の値は、その記事が表示された全クエリの平均"),
        ("カニバリ（カニバリゼーション）", "サイト内の複数の記事が同じ検索意図を取り合い、評価が分散して順位が伸びない状態"),
        ("導線", "記事内でアフィリエイトリンク（ボタン・テキストリンク）へ読者を誘導する流れ"),
        ("取りこぼし見込み", "直近28日の表示回数 × （目標CTR − 現在のCTR）を月換算した、追加で取れる可能性のあるクリック数"),
        ("301リダイレクト", "統合した記事の古いURLを新しいURLへ恒久的に転送する設定。評価を引き継げる"),
    ]
    write_table(ws, r, ["用語", "意味"], terms, wrap_cols=("意味",))


def sheet_summary(wb, d, df):
    ws = wb.create_sheet("サマリー")
    title(ws, "サマリー：結論と主要指標")
    set_widths(ws, [34, 12, 12, 12, 14, 46, 14])
    r = section(ws, 3, "結論（3行）")
    concl = [
        "① 集客は立ち上がっている（クリック/日 119→157→202）。一方で収益導線が主要記事にほぼ無く、アフィリエイトのクリックは流入の約0.5%。収益0円の最大の原因は「配置の良し悪し」以前に「主要記事に導線がない」こと。",
        "② 最初の収益源は転職会議（バリューコマース・無料会員登録）。9/12に1件・330円が実際に発生（未承認）しており、OpenWork・企業研究・ブラック求人の読者と最も相性が良い。",
        "③ カニバリは全体の順位低下の原因ではない（平均順位8.9→7.1に改善）。ただし転職会議・リクルートエージェント・AI履歴書・書類選考・SIer一覧など一部のグループでは評価の分散が起きている。",
    ]
    for t in concl:
        c = ws.cell(row=r, column=1, value=t)
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=7)
        c.font = Font(name=FONT, size=10)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[r].height = 36
        r += 1

    r = section(ws, r + 1, "検索パフォーマンス（期間別）")
    rows = []
    for period, label in (("last3m", "過去3か月"), ("last28d", "過去28日"), ("last7d", "過去7日")):
        dev = d[f"devices_{period}"]
        n = len(d[f"daily_{period}"])
        rr = r + 1 + len(rows)
        rows.append((label, n, int(dev.clicks.sum()), int(dev.impressions.sum()),
                     f"=C{rr}/D{rr}", f"=C{rr}/B{rr}", round((dev.position * dev.impressions).sum() / dev.impressions.sum(), 2)))
    r = write_table(ws, r, ["期間", "日数", "クリック", "表示回数", "CTR", "クリック/日", "平均掲載順位"], rows,
                    fmts={"クリック": "#,##0", "表示回数": "#,##0", "CTR": "0.0%", "クリック/日": "#,##0.0", "平均掲載順位": "0.00"})

    r = section(ws, r, "収益の現状（アフィリエイト）")
    vc = d["vc_adv"]
    a8 = d["a8_monthly"]
    rows = [
        ("バリューコマース（9/10〜10/10）", int(vc["表示"].sum()), int(vc["クリック"].sum()), int(vc["注文数"].sum()), int(vc["報酬合計"].sum()), "転職会議で1件・330円発生（未承認）。じゃらん・一休は無関係な広告"),
        ("A8.net（10月・途中）", int(a8.iloc[0]["imp数"]), int(a8.iloc[0]["click数"]), int(a8.iloc[0]["発生件数"]), int(a8.iloc[0]["発生金額"]), "表示が7月324→10月51と減少（流入増と逆行）"),
        ("もしもアフィリエイト", int(d["moshimo"].iloc[0]["インプレッション数"]), int(d["moshimo"].iloc[0]["クリック数"]), int(d["moshimo"].iloc[0]["発生成果数"]), 0, "期間はエクスポート時の設定"),
    ]
    rr0 = r + 1
    rows.append(("合計", f"=SUM(B{rr0}:B{rr0 + 2})", f"=SUM(C{rr0}:C{rr0 + 2})", f"=SUM(D{rr0}:D{rr0 + 2})", f"=SUM(E{rr0}:E{rr0 + 2})", ""))
    r = write_table(ws, r, ["ASP", "表示", "クリック", "発生件数", "発生金額（円）", "メモ"], rows,
                    fmts={"表示": "#,##0", "クリック": "#,##0", "発生金額（円）": "#,##0"}, wrap_cols=("メモ",))
    ws.cell(row=r - 1, column=1, value="検索流入（28日・月換算）に対するアフィリエイトクリック率（VC＋A8の直近月）").font = Font(name=FONT, size=10)
    total_clicks_28d = int(d["devices_last28d"].clicks.sum())
    ws.cell(row=r - 1, column=6, value=f"=(C{rr0}+C{rr0 + 1})/({total_clicks_28d}/28*30)").number_format = "0.0%"
    ws.cell(row=r - 1, column=6).font = Font(name=FONT, size=10, bold=True)
    r += 1

    r = section(ws, r, "仮説の検証結果")
    hyp = [
        ("カニバリで順位が低下している", "一部のみ正しい", "サイト全体の平均順位は8.9→7.1に改善しており、全体の主因ではない。ただし転職会議・リクルートエージェント・AI履歴書・書類選考・SIer一覧・応募経路などのグループで評価の分散が強く疑われ、AI履歴書記事は7.5→8.6位に実際に低下。"),
        ("アフィリエイト導線・配置が悪い", "正しい（配置以前の問題）", "検索流入 月約4,700に対し、ASPの表示は流入の1〜2割程度と推定。A8の表示は流入が倍増したのに7月324→10月51へ減少。主要記事にそもそも導線がない可能性が高い。"),
        ("CTRをさらに伸ばす必要がある", "記事によって正しい", "OpenWorkグラフ記事（18.6%）や富士通記事（7.2%）は十分高い。転職会議系（1.0〜1.9%）、IPA改編（2.5%）、AI履歴書（0.7%）、アットホーム（1.0%）、「社名変更 やばい」（2位でCTR2%）は明確に低い。"),
    ]
    r = write_table(ws, r, ["仮説", "判定", "根拠"], hyp, wrap_cols=("根拠",))
    for i in range(-1, 3):
        ws.merge_cells(start_row=r - 4 + i, start_column=3, end_row=r - 4 + i, end_column=7)
    for i in range(3):
        ws.row_dimensions[r - 4 + i].height = 48

    r = section(ws, r, "最優先の対応（今週〜2週間）")
    todo = [
        ("1", "無関係な広告の撤去", "バリューコマースのじゃらんnet・一休.comの表示元（自動広告・ウィジェット等）を特定して撤去"),
        ("2", "壊れたURLの修正", "「URL・技術課題」シートの手順で、https抜けリンク・末尾「]」・www付きを修正"),
        ("3", "A8広告の棚卸し", "流入増に反して表示が減っている原因（バナーの削除・設置記事の偏り）を確認"),
    ]
    for _, row in df[df.tier == "S"].iterrows():
        todo.append((str(len(todo) + 1), f"重点記事（優先{row['rank']}）", f"{row.name}：導線の設置 → 2週間後にタイトル変更（詳細は「重点9記事_詳細」）"))
    r = write_table(ws, r, ["No", "対応", "内容"], todo, wrap_cols=("内容",))
    for i in range(len(todo)):
        ws.merge_cells(start_row=r - 1 - len(todo) + i, start_column=3, end_row=r - 1 - len(todo) + i, end_column=7)


def sheet_good_bad(wb):
    ws = wb.create_sheet("良い点・悪い点")
    title(ws, "現状のブログの良い点・悪い点", "根拠データと、それぞれの活かし方・対策")
    r = write_table(ws, 3, ["区分", "分類", "内容", "根拠データ", "活かし方・対策"], notes.GOOD_BAD,
                    widths=[10, 12, 36, 60, 50], wrap_cols=("内容", "根拠データ", "活かし方・対策"), zebra=False)
    for i, row in enumerate(notes.GOOD_BAD, start=4):
        fill = "E2EFDA" if row[0] == "良い点" else "FCE4D6"
        ws.cell(row=i, column=1).fill = PatternFill("solid", fgColor=fill)
        ws.cell(row=i, column=1).font = Font(name=FONT, size=10, bold=True)
    ws.freeze_panes = "A4"


def sheet_direction(wb, df):
    ws = wb.create_sheet("今後の方向性")
    title(ws, "今後のブログの方向性", "データから見た「勝てる領域」と「収益につながる領域」の重なりに集中する")
    set_widths(ws, [24, 22, 16, 16, 16, 60, 40])
    D = notes.DIRECTION
    r = section(ws, 3, "1. ポジショニング")
    r = write_table(ws, r, ["項目", "内容"], D["positioning"], wrap_cols=("内容",))
    for i in range(len(D["positioning"])):
        ws.merge_cells(start_row=r - 1 - len(D["positioning"]) + i, start_column=2, end_row=r - 1 - len(D["positioning"]) + i, end_column=7)
        ws.row_dimensions[r - 1 - len(D["positioning"]) + i].height = 36

    r = section(ws, r, "2. 注力テーマ（6本柱）と現状の数値")
    stats = df.groupby("theme").agg(n=("impressions_3m", "size"), cpd=("cpd_28d", "sum"), prior=("cpd_prior", "sum"), imp=("impressions_3m", "sum"))
    rows = []
    for theme, role, policy, offer in D["pillars"]:
        s = stats.loc[theme]
        rr = r + 1 + len(rows)
        rows.append((theme, role, int(s.n), round(s.cpd * 30), f"=IFERROR({s.cpd:.3f}/{s.prior:.3f},0)", policy, offer))
    r = write_table(ws, r, ["テーマ", "役割", "記事数", "月間クリック（28日換算）", "伸び率（直近28日／それ以前）", "方針", "主な案件"], rows,
                    fmts={"月間クリック（28日換算）": "#,##0", "伸び率（直近28日／それ以前）": "0.00\"倍\""}, wrap_cols=("方針", "主な案件", "役割"))
    other = stats.drop([p[0] for p in D["pillars"]], errors="ignore")
    ws.cell(row=r - 1, column=1, value=f"上記以外（キャリア・働き方／SIer・SES業界研究／サイト基本ページ）：{int(other.n.sum())}記事・月間約{other.cpd.sum() * 30:,.0f}クリック").font = Font(name=FONT, size=9, color="595959")
    r += 1

    r = section(ws, r, "3. やめること・減らすこと")
    r = write_table(ws, r, ["項目", "理由"], D["stop"], wrap_cols=("理由",))
    for i in range(len(D["stop"])):
        ws.merge_cells(start_row=r - 1 - len(D["stop"]) + i, start_column=2, end_row=r - 1 - len(D["stop"]) + i, end_column=7)
        ws.row_dimensions[r - 1 - len(D["stop"]) + i].height = 30

    r = section(ws, r, "4. 新規記事・追記の候補")
    r = write_table(ws, r, ["仮URL・記事", "狙うクエリ", "根拠", "優先度"], [(a, b, c, e) for a, b, c, e in D["new_articles"]],
                    wrap_cols=("仮URL・記事", "狙うクエリ", "根拠", "優先度"))

    r = section(ws, r, "5. ロードマップ")
    r = write_table(ws, r, ["期間", "施策", "完了の目安"], D["roadmap"], wrap_cols=("施策", "完了の目安"))

    r = section(ws, r, "6. KPI（目標値は目安。2〜4週間ごとに見直し）")
    kpi = [
        ("アフィリエイトクリック／月（全ASP）", 25, 100, 250, "VC・A8・もしもの管理画面"),
        ("流入に対するアフィリエイトクリック率", 0.005, 0.02, 0.04, "上記÷GSCクリック"),
        ("発生成果（件）", 1, 3, 10, "ASP管理画面"),
        ("転職会議系のCTR", 0.019, 0.04, 0.06, "GSC（クエリに「転職会議」を含む）"),
        ("IPA改編＋応用情報新記事のCTR", 0.025, 0.04, 0.05, "GSC（ページ）"),
        ("検索クリック／月", round(df.cpd_28d.sum() * 30), 6000, 8000, "GSC"),
    ]
    r0 = r
    r = write_table(ws, r, ["KPI", "現状", "1か月後", "3か月後", "計測方法"], kpi, wrap_cols=("KPI", "計測方法"))
    for i, k in enumerate(kpi):
        fmt = "0.0%" if isinstance(k[1], float) and k[1] < 1 else "#,##0"
        for c in (2, 3, 4):
            ws.cell(row=r0 + 1 + i, column=c).number_format = fmt
            if c > 2:
                ws.cell(row=r0 + 1 + i, column=c).font = Font(name=FONT, size=10, color="0000FF")
    ws.cell(row=r - 1, column=1, value="※青字は目標値（入力値）。KPIの現状値は2026/10/10時点のデータ。").font = Font(name=FONT, size=9, color="595959")


def sheet_all_articles(wb, d, df):
    ws = wb.create_sheet("全記事_修正点")
    title(ws, "全記事の修正点（優先順）", "優先度 S：今週〜2週間／A：今月中／B：来月／C：3か月以内（統合・整理）／D：様子見。灰色の列は数値、白い列が修正内容")
    headers = ["優先順位", "優先度", "対応時期", "記事URL", "テーマ", "競合グループ", "3か月表示", "3か月クリック", "3か月CTR",
               "平均順位（3か月）", "平均順位（28日）", "クリック/日（以前）", "クリック/日（28日）", "傾向", "月間クリック（換算）",
               "表示/日（28日）", "CTR（28日）", "目標CTR", "取りこぼし見込み（クリック/月）",
               "関連クエリ（推定・表示上位3）", "診断（課題）", "カニバリ判定", "カニバリの詳細", "SEO・コンテンツの修正点",
               "タイトル・説明文の修正点", "アフィリエイト導線の修正点", "推奨案件（ASP）", "工数", "所見"]
    widths = [8, 7, 14, 40, 16, 16, 10, 10, 9, 9, 9, 10, 10, 9, 10, 10, 9, 9, 12, 60, 60, 9, 40, 60, 60, 70, 26, 6, 9]
    hr = 4
    rows = []
    for i, (slug, x) in enumerate(df.iterrows()):
        rr = hr + 1 + i
        rows.append([
            int(x["rank"]), x.tier, RANK_TIMING[x.tier], slug, x.theme, x.cluster,
            int(x.impressions_3m), int(x.clicks_3m), f"=IFERROR(H{rr}/G{rr},0)",
            None if pd.isna(x.position_3m) else round(x.position_3m, 1), None if pd.isna(x.position_28d) else round(x.position_28d, 1),
            round(x.cpd_prior, 2), round(x.cpd_28d, 2), x.trend, f"=M{rr}*30",
            round(x.ipd_28d, 1), round(x.ctr_28d_calc, 4),
            f"=IF(K{rr}=\"\",0,INDEX({d['ctr_range']},MIN(20,MAX(1,ROUND(K{rr},0)))))",
            f"=MAX(0,P{rr}*30*(R{rr}-Q{rr}))",
            x.related or "（上位1,000件のクエリに該当なし）", x.diag, x.cannibal_level, x.cannibal_note, x.seo, x.title_fix, x.cta,
            x.offer, x.effort, "個別に判断" if x.manual else "自動診断",
        ])
    write_table(ws, hr, headers, rows, widths=widths,
                fmts={"3か月表示": "#,##0", "3か月クリック": "#,##0", "3か月CTR": "0.0%", "平均順位（3か月）": "0.0", "平均順位（28日）": "0.0",
                      "クリック/日（以前）": "0.0", "クリック/日（28日）": "0.0", "月間クリック（換算）": "#,##0", "表示/日（28日）": "#,##0.0",
                      "CTR（28日）": "0.0%", "目標CTR": "0.0%", "取りこぼし見込み（クリック/月）": "#,##0"},
                wrap_cols=("記事URL", "関連クエリ（推定・表示上位3）", "診断（課題）", "カニバリの詳細", "SEO・コンテンツの修正点",
                           "タイトル・説明文の修正点", "アフィリエイト導線の修正点", "推奨案件（ASP）", "対応時期", "テーマ", "競合グループ"),
                zebra=False)
    last = hr + len(rows)
    for i in range(len(rows)):
        rr = hr + 1 + i
        tier = rows[i][1]
        for c in (1, 2, 3):
            ws.cell(row=rr, column=c).fill = PatternFill("solid", fgColor=RANK_FILL[tier])
        for c in range(7, 20):
            if ws.cell(row=rr, column=c).fill.fgColor.rgb in (None, "00000000"):
                ws.cell(row=rr, column=c).fill = PatternFill("solid", fgColor="F7F7F7")
        ws.cell(row=rr, column=2).alignment = Alignment(horizontal="center", vertical="top")
        ws.row_dimensions[rr].height = 150 if rows[i][-1] == "個別に判断" else 90
    ws.freeze_panes = ws.cell(row=hr + 1, column=5)
    ws.auto_filter.ref = f"A{hr}:{get_column_letter(len(headers))}{last}"
    red = PatternFill("solid", fgColor="F8CBAD")
    amber = PatternFill("solid", fgColor="FFE699")
    ws.conditional_formatting.add(f"V{hr + 1}:V{last}", CellIsRule(operator="equal", formula=['"強"'], fill=red))
    ws.conditional_formatting.add(f"V{hr + 1}:V{last}", CellIsRule(operator="equal", formula=['"中"'], fill=amber))
    ws.cell(row=3, column=1, value="凡例：取りこぼし見込み＝表示/日（28日）×30×（目標CTR−CTR（28日））。目標CTRは「目次・前提」シートの表を参照（変更すると再計算）。「所見」が「個別に判断」の行は人が個別に書いた修正案、「自動診断」の行はデータから自動生成した修正案。").font = Font(name=FONT, size=9, color="595959")
    ws.row_dimensions[hr].height = 42


def sheet_focus(wb, df):
    ws = wb.create_sheet("重点9記事_詳細")
    title(ws, "重点9記事のアクションプラン", "記事ごとに「データ分析 → カニバリ → タイトル・説明文 → アフィリエイト導線」の順で記載")
    set_widths(ws, [22, 120])
    r = 4
    for slug, x in df[df.tier == "S"].iterrows():
        c = ws.cell(row=r, column=1, value=f"優先{int(x['rank'])}　{slug}")
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
        c.font = Font(name=FONT, bold=True, size=12, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=NAVY)
        r += 1
        ctr3 = x.clicks_3m / x.impressions_3m if x.impressions_3m else 0
        items = [
            ("対象URL", f"{SITE}{slug}"),
            ("主要指標", f"3か月：表示{x.impressions_3m:,}・クリック{x.clicks_3m:,}・CTR{ctr3:.1%}・平均{x.position_3m:.1f}位／直近28日：クリック/日{x.cpd_28d:.1f}（以前{x.cpd_prior:.1f}）・平均{x.position_28d:.1f}位"),
            ("現在のデータからの分析", x.diag),
            ("カニバリの有無と解消案", f"判定：{x.cannibal_level}　{x.cannibal_note}\n{notes.CLUSTERS.get(x.cluster, {}).get('action', '')}\n" + x.seo),
            ("SEO（CTR）改善案：タイトル・説明文", x.title_fix),
            ("アフィリエイト導線の改善案", x.cta),
            ("推奨案件（ASP）", x.offer),
            ("関連クエリ（推定）", x.related),
        ]
        for k, v in items:
            a = ws.cell(row=r, column=1, value=k)
            b = ws.cell(row=r, column=2, value=v)
            a.font = Font(name=FONT, bold=True, size=10)
            a.fill = PatternFill("solid", fgColor=LIGHT)
            b.font = Font(name=FONT, size=10)
            for cell in (a, b):
                cell.alignment = Alignment(wrap_text=True, vertical="top")
                cell.border = BORDER
            lines = str(v).count("\n") + 1 + len(str(v)) // 95
            ws.row_dimensions[r].height = max(18, 15 * lines)
            r += 1
        r += 1


def sheet_cannibal(wb, d, df):
    ws = wb.create_sheet("カニバリ分析")
    title(ws, "カニバリゼーション（記事同士の競合）分析", "推定。確定は下の「GSCでの確認手順」で行ってください")
    rows = []
    for cluster, info in sorted(notes.CLUSTERS.items(), key=lambda kv: ["強", "中", "小", "なし"].index(kv[1]["level"])):
        members = df[df.cluster == cluster].sort_values("impressions_3m", ascending=False)
        if members.empty:
            continue
        mtxt = "\n".join(f"{s}（{m.impressions_3m:,}表示・{m.position_3m:.1f}位）" if not pd.isna(m.position_3m) else f"{s}（表示なし）"
                         for s, m in members.iterrows())
        rows.append((cluster, info["level"], len(members), int(members.impressions_3m.sum()), mtxt, info["evidence"], info["action"], info["check"]))
    r = write_table(ws, 3, ["競合グループ", "判定", "記事数", "3か月表示（合計）", "記事（表示・平均順位）", "根拠", "解消案（統合・差別化）", "GSCで確認すべきクエリ"],
                    rows, widths=[18, 7, 7, 12, 52, 60, 70, 36],
                    fmts={"3か月表示（合計）": "#,##0"}, wrap_cols=("記事（表示・平均順位）", "根拠", "解消案（統合・差別化）", "GSCで確認すべきクエリ"), zebra=False)
    fills = {"強": "F8CBAD", "中": "FFE699", "小": "E2EFDA", "なし": "F2F2F2"}
    for i, row in enumerate(rows, start=4):
        ws.cell(row=i, column=2).fill = PatternFill("solid", fgColor=fills[row[1]])
        ws.row_dimensions[i].height = max(60, 15 * (row[4].count("\n") + 1))
    ws.freeze_panes = "B4"

    r = section(ws, r, "GSCでの確認手順（5分）")
    steps = [
        "1. Search Console > 検索パフォーマンス > 「＋新規」>「検索キーワード」>「次と完全一致するキーワード」に上表のクエリを入力",
        "2. 「ページ」タブを開き、2つ以上のURLに表示回数があればカニバリ確定",
        "3. 期間を「過去3か月」にして比較をオンにすると、日によって表示URLが入れ替わっているかも分かる",
        "4. 恒久的には GSC API で「クエリ×ページ」データを取得し、自動で判定する仕組みを作る（次の段階で対応可能）",
    ]
    for t in steps:
        c = ws.cell(row=r, column=1, value=t)
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
        c.font = Font(name=FONT, size=10)
        r += 1

    r = section(ws, r + 1, "参考：複数の記事の意図に該当するクエリ（表示上位40件・推定）")
    q = d["queries_last3m"]
    owners = {}
    for slug, idx in d["query_matches"].items():
        for i in idx:
            owners.setdefault(i, []).append(slug)
    multi = [(q.loc[i, "query"], int(q.loc[i, "impressions"]), int(q.loc[i, "clicks"]), float(q.loc[i, "position"]), "\n".join(s)) for i, s in owners.items() if len(s) > 1]
    multi = sorted(multi, key=lambda x: -x[1])[:40]
    rows = []
    for k, (qq, imp, clk, pos, owners_txt) in enumerate(multi):
        rr = r + 1 + k
        rows.append((qq, imp, clk, f"=IFERROR(C{rr}/B{rr},0)", round(pos, 1), owners_txt))
    write_table(ws, r, ["クエリ", "表示", "クリック", "CTR", "平均順位", "該当する記事"], rows,
                fmts={"表示": "#,##0", "CTR": "0.0%", "平均順位": "0.0"}, wrap_cols=("該当する記事", "クエリ"))


def sheet_url(wb, d):
    ws = wb.create_sheet("URL・技術課題")
    title(ws, "壊れたURL・不要なインデックスの詳細", "過去3か月にGoogleの検索結果に表示されたURLのうち、本来インデックスされるべきでないもの")
    p3, p28, p7 = (d[f"pages_{p}"] for p in ("last3m", "last28d", "last7d"))
    p3 = p3.assign(kind=p3.page.map(classify_url))
    bad = p3[~p3.kind.isin(["記事", "トップ", "目次アンカー付き"])].copy()
    cause = {
        "壊れたURL（https抜けのリンク）": ("記事本文・ウィジェット等のリンクが「https://」なしの「saiyo-ura.com/〜」や「/saiyo-ura.com/〜」で書かれ、サイト内の相対パスとして解釈されている",
                                    "①WordPressの管理画面（または Search Regex 等のプラグイン）で本文中の「saiyo-ura.com/」のうち「https://」が付いていないリンクを検索して修正\n②念のため、壊れたURL→正しい記事URLへ301リダイレクトを設定（Redirection等のプラグイン）",
                                    "URL検査ツールで「参照元ページ」を確認すると、どの記事のリンクが原因か分かる場合がある", "高"),
        "不正な形式（末尾スラッシュ欠落・記号混入）": ("末尾に「]」が付いたURLは、Markdown形式のリンク（[文字](URL)）の貼り間違いが原因とみられる。末尾スラッシュなしは外部・内部の不完全なリンク",
                                        "①本文中の該当リンクを修正\n②URL検査ツールで、スラッシュなしURLが正規URLへ301されているか確認（WordPressの標準動作では301される）",
                                        "URL検査ツールで「Googleが選択した正規URL」を確認", "中"),
        "ホスト不一致（www付き）": ("www付きでアクセスされたURLがインデックスされている",
                          "www付き→wwwなしへの301リダイレクトとcanonical（正規URL）の設定を確認（サーバーまたはWordPressの設定）",
                          "ブラウザで https://www.saiyo-ura.com/ を開き、wwwなしへ転送されるか確認", "中"),
        "タグ/カテゴリ": ("タグ・カテゴリの一覧ページがインデックスされている（表示はほぼない）",
                     "SEOプラグイン（Yoast・SEO SIMPLE PACK等）でタグ・カテゴリページをnoindexに設定。カテゴリを集客に使う予定がなければnoindex推奨",
                     "設定後、URL検査で「noindexによって除外」になるか確認", "低"),
    }
    rows = []
    for _, x in bad.sort_values("kind").iterrows():
        c = cause.get(x.kind, ("", "", "", ""))
        i28 = int(p28.loc[p28.page == x.page, "impressions"].sum())
        i7 = int(p7.loc[p7.page == x.page, "impressions"].sum())
        rows.append((x.page, x.kind, int(x.impressions), int(x.clicks), round(x.position, 1), i28, i7, c[0], c[1], c[2], c[3]))
    r = write_table(ws, 3, ["URL", "種別", "3か月表示", "3か月クリック", "平均順位", "28日表示", "7日表示", "推定原因", "対処方法", "確認方法", "優先度"],
                    rows, widths=[48, 22, 9, 9, 8, 8, 8, 50, 60, 40, 7],
                    fmts={"3か月表示": "#,##0"}, wrap_cols=("URL", "種別", "推定原因", "対処方法", "確認方法"), zebra=False)
    for i in range(len(rows)):
        ws.row_dimensions[4 + i].height = 90

    r = section(ws, r, "参考：目次アンカー付きURL（#index_id）について")
    anc = p3[p3.kind == "目次アンカー付き"]
    anc_pages = anc.page.str.replace(r"#.*$", "", regex=True).value_counts()
    txt = (f"検索結果で記事内の目次が「ジャンプリンク」として表示された時のURLです（{len(anc)}件・{anc_pages.size}記事）。問題ではなく、むしろ良い兆候です。"
           "記事単位の集計からは除外しています。目次の見出しを検索語と同じ言葉にすると、ジャンプリンク経由のクリックが増えます。")
    c = ws.cell(row=r, column=1, value=txt)
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=11)
    c.font = Font(name=FONT, size=10)
    c.alignment = Alignment(wrap_text=True)
    ws.row_dimensions[r].height = 36
    r += 2
    rows = [(SITE + u.replace(SITE, ""), int(n)) for u, n in anc_pages.head(15).items()]
    write_table(ws, r, ["ジャンプリンクが表示された記事（上位15）", "アンカーURL数"], rows)


def sheet_findings(wb, d, df):
    ws = wb.create_sheet("GSC主要発見")
    title(ws, "GSC分析の主要発見（1〜5）", "前回報告の5つの発見の詳細")
    top10 = df.nlargest(10, "clicks_3m").clicks_3m.sum() / df.clicks_3m.sum()
    rows = [
        ("1", "伸びてはいるが、少数の記事頼み",
         f"クリック/日：3か月平均119→直近28日157→直近7日202。平均順位8.9→7.1。上位10記事でクリックの{top10:.0%}、OpenWorkグラフ記事1本で約17%。伸びの中心は富士通（クリック/日4.2→22.8）・IPA改編（3.7→9.6）・リクルートエージェント評判（0.4→6.2）",
         "ニュースや試験制度の話題による一時的な需要の可能性があり、サイトの地力が上がったとはまだ言えない。主力記事の順位が落ちるとサイト全体が大きく落ちる",
         "第2・第3の柱（企業研究・IPA）を育てて依存を分散。好調記事は大幅リライトせず導線の追加に留める", "推移・デバイス／全記事_修正点"),
        ("2", "最大の取りこぼしは「応用情報技術者試験 なくなる」",
         "「応用情報技術者試験 なくなる」2,424表示・9.9位・CTR0.9%。直近7日は1日約150表示。関連（いつまで・2027・最後）を含めると計4,000表示超",
         "今いちばん需要が伸びているテーマなのに、総合記事で10位前後に留まりほぼクリックを取れていない。応用情報の単独記事がない（受け皿不足）",
         "応用情報の単独記事を新設（/ouyou-jouhou-haishi/ 仮）。総合記事はハブ化", "全記事_修正点（優先6）／今後の方向性"),
        ("3", "転職会議の記事はOpenWorkの記事に大きく負けている",
         "直近7日のCTR：OpenWork系13.9%、転職会議系2.6%。「転職会議」1,646表示9.6位CTR0.5%、「転職会議 危ない」581表示クリック0",
         "同じ読者層なのに勝てていない。しかも転職会議は成果が出ている唯一の案件で、ここが最も収益に近い",
         "OpenWork記事で勝っている型（具体的な見方・画面解説）を転職会議記事に横展開。4記事の役割分担", "全記事_修正点（優先1）／カニバリ分析"),
        ("4", "技術的な問題（壊れたURL等）",
         "https抜けのリンクが原因とみられる「/saiyo-ura.com/記事名/」形式のURLが4件、末尾に「]」やスラッシュなしのURL、www付きURL、タグ・カテゴリページがインデックス",
         "表示は少ないが、クロールの無駄と内部リンクの評価漏れにつながる。壊れたリンクは読者にとっても404",
         "リンク修正＋301リダイレクト、タグ・カテゴリのnoindex", "URL・技術課題"),
        ("5", "順位に対してCTRが低い記事・CTRが落ちた記事",
         "AI履歴書記事：7.5位でCTR0.7%（同順位帯の標準は約3.5%）。内定即出し記事：順位6.4→6.0なのにCTR3.9%→2.3%でクリック半減。「社名変更 やばい」は2位でCTR2%",
         "タイトルが検索意図に即答していない、または検索結果の見え方（競合・AIの概要表示）が変化",
         "タイトル・説明文で答えを言い切る。CTRが落ちた記事は検索結果を目視確認", "全記事_修正点（優先7・8）"),
    ]
    write_table(ws, 3, ["No", "発見", "数値の根拠", "意味すること", "打ち手", "関連シート"], rows,
                widths=[5, 30, 70, 50, 50, 24], wrap_cols=("発見", "数値の根拠", "意味すること", "打ち手", "関連シート"), zebra=False)
    for i in range(len(rows)):
        ws.row_dimensions[4 + i].height = 110


def sheet_queries(wb, d):
    ws = wb.create_sheet("クエリ機会")
    title(ws, "クエリ別の機会", "担当記事（推定）は記事マスタのパターンで割り当て。複数ある場合は改行で併記")
    q3 = d["queries_last3m"]
    owners = {}
    for slug, idx in d["query_matches"].items():
        for i in idx:
            owners.setdefault(i, []).append(slug)
    r = section(ws, 3, "1. あと一歩のクエリ（過去3か月・平均4〜20位・表示100回以上、3位相当のCTR 7.2%に届いた場合の追加クリック順）")
    s = q3[q3.position.between(4, 20) & (q3.impressions >= 100)].copy()
    s["gain"] = (s.impressions * (0.072 - s.ctr)).clip(lower=0)
    s = s.sort_values("gain", ascending=False).head(40)
    rows = []
    for k, (i, x) in enumerate(s.iterrows()):
        rr = r + 1 + k
        rows.append((x["query"], int(x.impressions), int(x.clicks), f"=IFERROR(C{rr}/B{rr},0)", round(x.position, 1), f"=MAX(0,B{rr}*(0.072-D{rr}))", "\n".join(owners.get(i, ["（該当なし）"]))))
    r = write_table(ws, r, ["クエリ", "表示", "クリック", "CTR", "平均順位", "見込み増（クリック/3か月）", "担当記事（推定）"], rows,
                    widths=[34, 9, 9, 8, 9, 12, 48], fmts={"表示": "#,##0", "CTR": "0.0%", "平均順位": "0.0", "見込み増（クリック/3か月）": "#,##0"},
                    wrap_cols=("担当記事（推定）",))

    days = {p: len(d[f"daily_{p}"]) for p in ("last3m", "last28d", "last7d")}
    m = q3.set_index("query")[["impressions"]].rename(columns={"impressions": "i3"}) \
        .join(d["queries_last28d"].set_index("query")[["impressions", "clicks", "position"]].rename(columns={"impressions": "i28", "clicks": "c28", "position": "p28"}), how="outer") \
        .join(d["queries_last7d"].set_index("query")[["impressions"]].rename(columns={"impressions": "i7"}), how="outer").fillna(0)
    m["prior"] = (m.i3 - m.i28).clip(lower=0) / (days["last3m"] - days["last28d"])
    m["d28"] = m.i28 / days["last28d"]
    m["d7"] = m.i7 / days["last7d"]
    m = m[m.i28 >= 50]
    m["growth"] = (m.d28 + 1) / (m.prior + 1)
    m = m.sort_values("growth", ascending=False).head(30)
    r = section(ws, r, "2. 直近28日で急伸・新規出現したクエリ（需要の変化。表示/日で比較）")
    rows = [(qq, round(x.prior, 1), round(x.d28, 1), round(x.d7, 1), int(x.c28), round(x.p28, 1) if x.p28 else None) for qq, x in m.iterrows()]
    r = write_table(ws, r, ["クエリ", "表示/日（以前）", "表示/日（28日）", "表示/日（7日）", "クリック（28日）", "平均順位（28日）"], rows,
                    fmts={"表示/日（以前）": "0.0", "表示/日（28日）": "0.0", "表示/日（7日）": "0.0", "平均順位（28日）": "0.0"})

    r = section(ws, r, "3. 表示されているがクリック0のクエリ（過去3か月・表示上位30。検索意図とのズレを確認）")
    z = q3[q3.clicks == 0].nlargest(30, "impressions")
    rows = [(x["query"], int(x.impressions), round(x.position, 1), "\n".join(owners.get(i, ["（該当なし）"]))) for i, x in z.iterrows()]
    write_table(ws, r, ["クエリ", "表示", "平均順位", "担当記事（推定）"], rows, fmts={"表示": "#,##0", "平均順位": "0.0"}, wrap_cols=("担当記事（推定）",))


def sheet_trend(wb, d):
    ws = wb.create_sheet("推移・デバイス")
    title(ws, "週次推移・デバイス別")
    daily = d["daily_last3m"].copy()
    daily["date"] = pd.to_datetime(daily.date)
    daily["week"] = daily.date.dt.to_period("W-MON").map(lambda p: p.start_time.strftime("%Y/%m/%d"))
    daily["wp"] = daily.position * daily.impressions
    w = daily.groupby("week", sort=False).agg(days=("date", "count"), clicks=("clicks", "sum"), imp=("impressions", "sum"), wp=("wp", "sum")).reset_index()
    r = section(ws, 3, "週次推移（月曜始まり。最終週は日数が少ない）")
    rows = []
    for k, x in enumerate(w.itertuples()):
        rr = r + 1 + k
        rows.append((x.week, x.days, int(x.clicks), int(x.imp), f"=IFERROR(C{rr}/D{rr},0)", round(x.wp / x.imp, 2), f"=C{rr}/B{rr}"))
    r = write_table(ws, r, ["週の開始日", "日数", "クリック", "表示回数", "CTR", "平均掲載順位", "クリック/日"], rows,
                    widths=[14, 8, 12, 12, 9, 12, 12, 4, 14, 12, 12, 9, 12],
                    fmts={"クリック": "#,##0", "表示回数": "#,##0", "CTR": "0.0%", "平均掲載順位": "0.00", "クリック/日": "#,##0.0"})

    r = section(ws, r, "デバイス別")
    for period, label in (("last28d", "過去28日"), ("last3m", "過去3か月")):
        dev = d[f"devices_{period}"]
        rows = []
        for k, x in enumerate(dev.itertuples()):
            rr = r + 1 + k
            rows.append((f"{label}・{x.device}", int(x.clicks), int(x.impressions), f"=IFERROR(B{rr}/C{rr},0)", x.position))
        r = write_table(ws, r, ["期間・デバイス", "クリック", "表示回数", "CTR", "平均掲載順位"], rows,
                        fmts={"クリック": "#,##0", "表示回数": "#,##0", "CTR": "0.0%", "平均掲載順位": "0.00"})

    r = section(ws, r, "日別（過去3か月）")
    rows = []
    for k, x in enumerate(d["daily_last3m"].itertuples()):
        rr = r + 1 + k
        rows.append((x.date, int(x.clicks), int(x.impressions), f"=IFERROR(B{rr}/C{rr},0)", x.position))
    write_table(ws, r, ["日付", "クリック", "表示回数", "CTR", "平均掲載順位"], rows,
                fmts={"クリック": "#,##0", "表示回数": "#,##0", "CTR": "0.0%", "平均掲載順位": "0.0"})


def sheet_affiliate(wb, d):
    ws = wb.create_sheet("アフィリエイト実績")
    title(ws, "アフィリエイト実績（A8.net・バリューコマース・もしも）")
    set_widths(ws, [40, 12, 12, 10, 12, 12, 50])
    r = section(ws, 3, "診断")
    diag = [
        "・成果：バリューコマースの転職会議で1件・330円が発生（9/12・未承認）。それ以外は全ASPで0件。",
        "・表示：A8の表示は7月324→8月193→9月97→10月51と減少。同じ期間に検索流入は約2倍に増えており、流入の多い記事に広告が置かれていない、または既存のバナーが外れている可能性が高い。",
        "・クリック：VCは30日で646表示・22クリック。検索流入（月約4,700）に対し、アフィリエイトのクリックは全ASP合計で月約25（約0.5%）。",
        "・無関係な広告：じゃらんnet・一休.comが各34表示。読者（転職検討者）と無関係なので撤去。",
        "・リクナビNEXTは12表示に対して13クリック（テキストリンク経由とみられる）。テキストリンクでもクリックされる案件。",
        "・レバテックダイレクト（A8）は431表示・15クリック（3.5%）でA8の中で最も実績がある。IT系記事のスカウト導線に使う。",
    ]
    for t in diag:
        c = ws.cell(row=r, column=1, value=t)
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=7)
        c.font = Font(name=FONT, size=10)
        c.alignment = Alignment(wrap_text=True)
        ws.row_dimensions[r].height = 30
        r += 1

    r = section(ws, r + 1, "A8.net 月次（2026年）")
    a8 = d["a8_monthly"].iloc[::-1].reset_index(drop=True)
    rows = []
    for k, x in a8.iterrows():
        rr = r + 1 + k
        rows.append((x["年月"], int(x["imp数"]), int(x["click数"]), f"=IFERROR(C{rr}/B{rr},0)", int(x["発生件数"]), int(x["発生金額"])))
    r = write_table(ws, r, ["年月", "表示", "クリック", "CTR", "発生件数", "発生金額（円）"], rows,
                    fmts={"表示": "#,##0", "CTR": "0.0%", "発生金額（円）": "#,##0"})

    r = section(ws, r, "A8.net プログラム別（2026年1月〜10月）")
    rows = []
    for k, x in d["a8_programs"].iterrows():
        rr = r + 1 + k
        rows.append((x["プログラム名"].strip(), int(x["imp数"]), int(x["click数"]), f"=IFERROR(C{rr}/B{rr},0)", int(x["発生件数"]), int(x["発生金額"])))
    r = write_table(ws, r, ["プログラム", "表示", "クリック", "CTR", "発生件数", "発生金額（円）"], rows,
                    fmts={"表示": "#,##0", "CTR": "0.0%", "発生金額（円）": "#,##0"}, wrap_cols=("プログラム",))

    r = section(ws, r, "バリューコマース 広告主別（2026/09/10〜10/10）")
    rows = []
    for k, x in d["vc_adv"].iterrows():
        rr = r + 1 + k
        rows.append((x["広告主"], int(x["表示"]), int(x["クリック"]), f"=IFERROR(C{rr}/B{rr},0)", int(x["注文数"]), int(x["報酬合計"]),
                     "無関係な広告。撤去" if x["広告主"] in ("じゃらんnet", "一休.com") else ""))
    r = write_table(ws, r, ["広告主", "表示", "クリック", "CTR", "発生件数", "報酬（円・未承認含む）", "メモ"], rows,
                    fmts={"表示": "#,##0", "CTR": "0.0%", "報酬（円・未承認含む）": "#,##0"}, wrap_cols=("広告主",))

    r = section(ws, r, "もしもアフィリエイト（サイト別KPI）")
    x = d["moshimo"].iloc[0]
    rr = r + 1
    r = write_table(ws, r, ["サイト", "表示", "クリック", "CTR", "発生件数", "発生金額（円）"],
                    [(x["サイト名"], int(x["インプレッション数"]), int(x["クリック数"]), f"=IFERROR(C{rr}/B{rr},0)", int(x["発生成果数"]), 0)],
                    fmts={"表示": "#,##0", "CTR": "0.0%"})

    r = section(ws, r, "バリューコマース 日別（2026/09/10〜10/10）")
    vd = d["vc_daily"].iloc[::-1].reset_index(drop=True)
    rows = []
    for k, x in vd.iterrows():
        rr = r + 1 + k
        rows.append((x["日付"], int(x["表示"]), int(x["クリック"]), f"=IFERROR(C{rr}/B{rr},0)", int(x["注文数"]), int(x["報酬合計"])))
    n = len(rows)
    rows.append(("合計", f"=SUM(B{r + 1}:B{r + n})", f"=SUM(C{r + 1}:C{r + n})", f"=IFERROR(C{r + n + 1}/B{r + n + 1},0)", f"=SUM(E{r + 1}:E{r + n})", f"=SUM(F{r + 1}:F{r + n})"))
    write_table(ws, r, ["日付", "表示", "クリック", "CTR", "発生件数", "報酬（円）"], rows, fmts={"表示": "#,##0", "CTR": "0.0%"})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", default="2026-10-10")
    args = parser.parse_args()
    d = load(args.snapshot)
    df = build_articles(d)
    wb = Workbook()
    sheet_guide(wb, d, args.snapshot, df)
    sheet_summary(wb, d, df)
    sheet_good_bad(wb)
    sheet_direction(wb, df)
    sheet_all_articles(wb, d, df)
    sheet_focus(wb, df)
    sheet_cannibal(wb, d, df)
    sheet_url(wb, d)
    sheet_findings(wb, d, df)
    sheet_queries(wb, d)
    sheet_trend(wb, d)
    sheet_affiliate(wb, d)
    for ws in wb.worksheets:
        ws.page_setup.orientation = "landscape"
        ws.page_setup.paperSize = ws.PAPERSIZE_A4
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        if ws.title == "全記事_修正点":
            ws.page_setup.paperSize = ws.PAPERSIZE_A3
            ws.page_setup.fitToWidth = 2
            ws.print_title_rows = "4:4"
        ws.sheet_properties.tabColor = NAVY if ws.title in ("サマリー", "全記事_修正点", "重点9記事_詳細") else "8EA9DB"
    out = ROOT / "reports" / "excel" / f"saiyo-ura_改善レポート_{args.snapshot}.xlsx"
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)
    df.drop(columns=["query_pattern"]).to_csv(out.with_suffix(".articles.csv"), encoding="utf-8-sig")
    print(f"wrote {out.relative_to(ROOT)}")
    print(df.groupby("tier").size().to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
