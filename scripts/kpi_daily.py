#!/usr/bin/env python3
"""効果測定の日別表（data/affiliate/kpi_daily.csv）の更新と、指標①〜⑤の計算。

指標の定義は reports/affiliate/2026-10-12/step4_rules_and_kpi.md の「効果測定の基準」。

使い方:
    # GSC の日別（正規化済み daily.csv）と VC の日別レポート（UTF-8変換済み）を取り込む
    python3 scripts/kpi_daily.py merge \
        --gsc data/gsc/2026-10-10/last3m/daily.csv \
        --vc data/affiliate/2026-10-10/valuecommerce_daily_260910-261010.csv \
        --vc data/affiliate/2026-10-14/valuecommerce_daily_260914-261014.csv \
        --until 2026-10-13

    # 期間を指定して①〜⑤を計算する
    python3 scripts/kpi_daily.py calc --from 2026-09-01 --to 2026-10-13

- 同じ日付が複数のファイルにある場合は、後に指定したファイルの値で上書きする（新しいダウンロードを後に書く）。
- ダウンロード当日は途中までの数字なので、--until で前日までに絞る。
- 指標は「分子と分母の両方がそろっている日」だけで計算し、使った日数を表示する。
"""
from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path

KPI_CSV = Path(__file__).resolve().parent.parent / "data" / "affiliate" / "kpi_daily.csv"

DATE = "日付"
GSC = "GSCクリック（サイト全体）"
GSC_TOP10 = "GSCクリック（上位10記事）"
A8_IMP, A8_CLK, A8_CV = "A8表示", "A8クリック", "A8発生"
VC_IMP, VC_CLK, VC_CV = "VC表示", "VCクリック", "VC発生"
MS_IMP, MS_CLK, MS_CV = "もしも表示", "もしもクリック", "もしも発生"
SELF = "自分で見た・押した回数"
MEMO = "メモ"


def load() -> tuple[list[str], dict[str, dict[str, str]]]:
    with KPI_CSV.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        header = list(reader.fieldnames or [])
        rows = {r[DATE]: r for r in reader if r.get(DATE)}
    return header, rows


def save(header: list[str], rows: dict[str, dict[str, str]]) -> None:
    with KPI_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header, lineterminator="\n")
        w.writeheader()
        for d in sorted(rows):
            w.writerow({k: rows[d].get(k, "") for k in header})


def norm_date(value: str) -> str:
    return date.fromisoformat(value.strip().replace("/", "-")).isoformat()


def read_rows(path: str) -> list[dict[str, str]]:
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def put(rows, header, d, values, since, until):
    if (since and d < since) or (until and d > until):
        return
    row = rows.setdefault(d, {k: "" for k in header} | {DATE: d})
    row.update(values)


def cmd_merge(args) -> None:
    header, rows = load()
    for path in args.gsc or []:
        for r in read_rows(path):
            put(rows, header, norm_date(r["date"]), {GSC: r["clicks"]}, args.since, args.until)
    for path in args.vc or []:
        for r in read_rows(path):
            put(rows, header, norm_date(r["日付"]),
                {VC_IMP: r["表示"], VC_CLK: r["クリック"], VC_CV: r["注文数"]},
                args.since, args.until)
    save(header, rows)
    print(f"{KPI_CSV}: {len(rows)}日分")


def num(row, col):
    v = (row.get(col) or "").strip().replace(",", "")
    return float(v) if v else None


def total(days, cols):
    """cols がすべてそろっている日だけで合計する。戻り値: (各列の合計, 日数)"""
    use = [r for r in days if all(num(r, c) is not None for c in cols)]
    return [sum(num(r, c) for r in use) for c in cols], len(use)


def per_1000(days, col, label):
    (n, g), k = total(days, [col, GSC])
    rate = f"{n / g * 1000:.1f}" if g else "―"
    return f"{label}: {rate}（{col} {n:,.0f} ÷ 流入 {g:,.0f} × 1,000、{k}日分）"


def cmd_calc(args) -> None:
    _, rows = load()
    days = [r for d, r in sorted(rows.items()) if args.date_from <= d <= args.date_to]
    print(f"期間 {args.date_from}〜{args.date_to}（表にある日 {len(days)}日）")
    (g,), k = total(days, [GSC])
    print(f"流入（GSC）: {g:,.0f}（{k}日分、1日平均 {g / k:.1f}）" if k else "流入（GSC）: データなし")
    print(per_1000(days, A8_IMP, "① A8表示／流入1,000"))
    print(per_1000(days, A8_CLK, "② A8クリック／流入1,000"))
    (a, v, m, g3), k3 = total(days, [A8_CLK, VC_CLK, MS_CLK, GSC])
    rate = f"{(a + v + m) / g3 * 1000:.1f}" if g3 else "―"
    print(f"③ 全ASPクリック／流入1,000: {rate}（{k3}日分）")
    print("   （参考）" + per_1000(days, VC_IMP, "VC表示／流入1,000"))
    print("   （参考）" + per_1000(days, VC_CLK, "VCクリック／流入1,000"))
    (ai, ac), k4 = total(days, [A8_IMP, A8_CLK])
    print(f"④ A8クリック率: {ac / ai:.1%}（{k4}日分）" if ai else f"④ A8クリック率: ―（{k4}日分）")
    for label, col in (("A8", A8_CV), ("VC", VC_CV), ("もしも", MS_CV)):
        (c,), kc = total(days, [col])
        print(f"⑤ 発生 {label}: {c:,.0f}件（{kc}日分）")
    (s,), ks = total(days, [SELF])
    print(f"自分で見た・押した回数: {s:,.0f}（記録 {ks}日分）")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("merge", help="GSC・VCの日別CSVを kpi_daily.csv に取り込む")
    m.add_argument("--gsc", action="append", help="data/gsc/<取得日>/<期間>/daily.csv")
    m.add_argument("--vc", action="append", help="VC 日別レポート（UTF-8変換済み）")
    m.add_argument("--since", type=norm_date, help="この日以降だけ取り込む（YYYY-MM-DD）")
    m.add_argument("--until", type=norm_date, help="この日までだけ取り込む（YYYY-MM-DD）")
    m.set_defaults(func=cmd_merge)
    c = sub.add_parser("calc", help="期間の①〜⑤を計算する")
    c.add_argument("--from", dest="date_from", type=norm_date, required=True)
    c.add_argument("--to", dest="date_to", type=norm_date, required=True)
    c.set_defaults(func=cmd_calc)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
