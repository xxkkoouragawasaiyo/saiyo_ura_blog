# 採用のウラ側（saiyo-ura.com）データ分析

ブログ改善のためのデータ置き場と分析スクリプト。

## ディレクトリ

```
data/gsc/raw/<取得日>/<期間>.zip        GSCエクスポートの元ファイル
data/gsc/<取得日>/<期間>/*.csv          正規化済みデータ（英語カラム・数値）
data/gsc/<取得日>/manifest.json         期間・合計値・行数
reports/gsc/<取得日>/report.md          自動生成レポート
reports/gsc/<取得日>/insights.md        所見と打ち手（手書き）
reports/gsc/<取得日>/*.csv              施策候補リスト
reports/strategy/                      記事別アクションプラン
data/affiliate/<取得日>/                ASPレポート（A8.net / もしも / バリューコマース、UTF-8変換済み）
scripts/                               取込・分析スクリプト
```

期間キー: `last7d`（過去7日）/ `last28d`（過去28日）/ `last3m`（過去3か月）

正規化CSVのカラム: `<次元>, clicks, impressions, ctr(0〜1), position`
（次元: daily=`date` / queries=`query` / pages=`page` / countries=`country` / devices=`device`）

## 更新手順

1. Search Console > 検索パフォーマンス > 検索タイプ「ウェブ」で、期間を **過去7日・過去28日・過去3か月** の3通りに切り替えてそれぞれ「エクスポート > CSVをダウンロード」
2. 取り込み（取得日フォルダはzipファイル名の日付から自動判定）
   ```sh
   python3 scripts/gsc_import.py ~/Downloads/saiyo-ura.com-Performance-on-Search-*.zip
   ```
3. 分析レポート生成（最新の取得日が対象。`--snapshot 2026-10-10` で指定も可）
   ```sh
   pip install -r requirements.txt
   python3 scripts/gsc_analyze.py
   ```
4. `reports/gsc/<取得日>/report.md` を読み、`insights.md` に所見を書く

## 出力CSV

| ファイル | 内容 |
|---|---|
| `pages.csv` | 記事ごとの日次平均（3か月/28日/7日/以前）とテーマ |
| `ctr_gap.csv` | 同順位の標準CTRに比べてCTRが低い記事（タイトル改善候補） |
| `striking_queries.csv` | 4〜20位で表示の多いクエリ（あと一歩クエリ） |
| `rising_queries.csv` | 直近28日で表示が伸びたクエリ |
| `url_issues.csv` | インデックスされるべきでないURL（タグ・壊れたリンク等） |

## ASPデータ

各ASPの管理画面からダウンロードしたCSVは Shift_JIS のため、UTF-8 に変換して `data/affiliate/<取得日>/` に保存する。
```sh
iconv -f CP932 -t UTF-8 元ファイル.csv > data/affiliate/<取得日>/<asp>_<内容>.csv
```
氏名などの個人情報を含む列は、コミット前に削除すること。

## Excelレポート

```sh
python3 scripts/build_excel_report.py   # reports/excel/saiyo-ura_改善レポート_<取得日>.xlsx を作成
```

- 記事のテーマ・競合グループ・推奨案件・関連クエリの判定パターンは `data/articles/article_master.csv` で管理する（記事を追加したら1行追加）。
- 人が判断した所見（記事別の修正点・競合グループの判定・良い点/悪い点・方向性）は `scripts/report_notes_<日付>.py` に書く。
- 生成後、LibreOffice等で数式を再計算してから開くと、取りこぼし見込みなどの値が表示される（Excelでは開いた時に自動で再計算される）。

## 効果測定（KPI）

```sh
# GSC・VC の日別を data/affiliate/kpi_daily.csv に取り込む（A8・もしもは手で記入）
python3 scripts/kpi_daily.py merge --gsc data/gsc/<取得日>/<期間>/daily.csv --vc data/affiliate/<取得日>/valuecommerce_daily_*.csv --until <前日>
# 期間を指定して指標①〜⑤を計算
python3 scripts/kpi_daily.py calc --from 2026-09-01 --to 2026-10-13
```

指標の定義と成功の基準は `reports/affiliate/2026-10-12/step4_rules_and_kpi.md`。A8・もしもは必ずサイト「採用のウラ側」で絞り込んだレポートを使う。
