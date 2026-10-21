# A8.net 広告掲載URLの提出対応（2026-10-21）

## 結論

- A8.netは2023年12月7日から、メディア会員に「広告掲載URL」の提出を求めています（ステマ規制への対応で、広告主が掲載ページを確認するための仕組み）。未提出でペナルティになるとする公式文言は確認できていませんが、**高単価のレバテック案件で「どこに載っているか見えないメディア」のままでいるのは不利**です。提携中の全プログラムについて今週中に提出します。
- この作業環境からはサイトに接続できないため、**どの記事に実際にリンクがあるかは未確認**です。下の候補リストは記事マスタ（`data/articles/article_master.csv`）の「推奨案件」から作ったもので、実際の設置状況とは一致しない可能性があります。提出前に、手順1のスクリプトで実際の設置状況を確認してください。

## 先に確認していただきたいこと

1. **画面のプログラムは「レバテックダイレクト」です。「レバテックキャリア」ではありません。** A8のプログラム別レポート（2026/01〜10）で実績があるのは、レバテックダイレクト・Geekly・第二新卒エージェントneoの3つだけです。レバテックキャリアの記事（`/levtech-career-reputation/`）でキャリアのリンクを貼っている場合、そのリンクはA8以外のASP経由か、未提携の可能性があります。【要確認】
2. **リンクの設置が少なすぎる疑いがあります。** レバテックダイレクトの表示（imp）は10か月で431回です。一方、推奨記事の1つである富士通の記事だけで、3か月のクリックが906あります。推奨記事の大半にリンクが無い可能性が高いと見ています（戦略レポートの「A8広告の設置場所を棚卸し」と同じ問題です）。提出作業を、リンク設置漏れの棚卸しも兼ねて進めることをおすすめします。

## 手順

### 1. 実際の設置状況を調べる（手元のPCで実行・数分）

```sh
python3 scripts/a8_link_audit.py
```

- サイトマップから記事を集め、各記事のHTMLに含まれるA8リンクを抽出します。結果は `reports/affiliate/<実行日>/` に出力されます。
- `a8_submit_<プログラムID>.txt` に、提出フォームにそのまま貼れるURL（1行1URL）が入ります。
- 8割以上の記事に出ているプログラムは、サイドバーなどで全ページに表示しているとみなし、トップページのURLだけを出力します。全ページ表示ならトップページのURLで足りるという扱いは解説記事の情報で、A8公式の文面では未確認です。不安であれば、`a8_link_audit.csv` から全記事のURLを出してください。
- バナーはプログラムを自動判定します。テキストリンクだけのものは `a8_unmapped.csv` に出ます。A8管理画面の「広告リンク作成」で表示されるリンクコードの `a8mat=` と照合し、`data/affiliate/a8_link_map.csv` に `a8mat,program_id,memo` の形で追記してから、もう一度実行してください。
- A8のリンク先（px.a8.net）にはアクセスしません。HTMLを読むだけなので、クリック数や表示数には影響しません。

### 2. A8管理画面で提出する

1. 「広告掲載URL管理」でプログラムを選び、「広告掲載URLの提出」タブを開きます。
2. `a8_submit_<プログラムID>.txt` の中身を貼り付けて「提出する」を押します（1回100URLまで。改行区切り）。
3. 提携中のプログラムすべてで同じ作業をします。表示実績が0のプログラムでも、提携中でリンクを貼っているなら提出します。

「CSV一括アップロード」のファイル形式はこちらで確認できていません。使う場合は、画面にあるテンプレートや説明に従ってください。

### 3. 今後の運用

- 記事を公開・リライトして、A8リンクを追加したらその都度提出します（提出済みのURLを再提出すると更新日時が上書きされます）。
- 月1回のASPデータ取り込みのときに `a8_link_audit.py` も実行し、提出漏れと設置漏れを確認します。

## 推奨案件ベースの候補リスト（実際の設置は未確認）

スクリプトを実行できない場合に、手作業で確認するためのリストです。各記事を開いて該当プログラムのリンクがあるか確認し、ある記事だけを提出してください。**リンクが無い記事は提出しません。** GSCクリックが多い記事ほど上にあり、設置漏れの機会損失も大きいので、上から確認してください。

### レバテックダイレクト（s00000011866029）— 候補36記事

| 確認 | URL | GSCクリック（3か月） |
|---|---|---:|
| [ ] | https://saiyo-ura.com/fujitsu-nenshu-hyouka-jinji-me/ | 906 |
| [ ] | https://saiyo-ura.com/it-strategist-haishi/ | 544 |
| [ ] | https://saiyo-ura.com/database-specialist-haishi/ | 542 |
| [ ] | https://saiyo-ura.com/ipa-exam-reform-2027/ | 503 |
| [ ] | https://saiyo-ura.com/network-specialist-haishi/ | 300 |
| [ ] | https://saiyo-ura.com/aws-sap-difficulty-salary/ | 214 |
| [ ] | https://saiyo-ura.com/professional-digital-skill-exam/ | 201 |
| [ ] | https://saiyo-ura.com/system-architect-haishi/ | 186 |
| [ ] | https://saiyo-ura.com/project-manager-exam-reform/ | 166 |
| [ ] | https://saiyo-ura.com/embedded-specialist-haishi/ | 91 |
| [ ] | https://saiyo-ura.com/aws-saa-difficulty/ | 83 |
| [ ] | https://saiyo-ura.com/nec-ai-department-corporate-ai-workforce/ | 72 |
| [ ] | https://saiyo-ura.com/ipa-exam-reform-career-impact/ | 70 |
| [ ] | https://saiyo-ura.com/linuc-lpic-level2-aws-saa-difficulty/ | 48 |
| [ ] | https://saiyo-ura.com/user-sier-tier/ | 27 |
| [ ] | https://saiyo-ura.com/independent-sier-tier/ | 16 |
| [ ] | https://saiyo-ura.com/infra-engineer-qualification-roadmap/ | 15 |
| [ ] | https://saiyo-ura.com/aws-cloud-practitioner-difficulty/ | 13 |
| [ ] | https://saiyo-ura.com/levtech-career-reputation/ | 12 |
| [ ] | https://saiyo-ura.com/data-management-exam/ | 11 |
| [ ] | https://saiyo-ura.com/ses-syoryu-toritekiho-tenshoku/ | 11 |
| [ ] | https://saiyo-ura.com/linuc-lpic-difference/ | 10 |
| [ ] | https://saiyo-ura.com/independent-sier-delisting/ | 8 |
| [ ] | https://saiyo-ura.com/ccna-infrastructure-engineer/ | 7 |
| [ ] | https://saiyo-ura.com/engineer-ai-nakunaru/ | 7 |
| [ ] | https://saiyo-ura.com/independent-sier/ | 7 |
| [ ] | https://saiyo-ura.com/maker-sier-tier/ | 7 |
| [ ] | https://saiyo-ura.com/user-sier-ranking/ | 7 |
| [ ] | https://saiyo-ura.com/seishain-haken-ses-chigai/ | 4 |
| [ ] | https://saiyo-ura.com/ses-kigyou-miwakekata-erabikata/ | 2 |
| [ ] | https://saiyo-ura.com/ai-jidai-engineer-skill/ | 1 |
| [ ] | https://saiyo-ura.com/job-change-scout-meaning-mechanism/ | 1 |
| [ ] | https://saiyo-ura.com/engineer-touta-ikinokoru/ | 0 |
| [ ] | https://saiyo-ura.com/it-tensyoku-agent-osusume/ | 0 |
| [ ] | https://saiyo-ura.com/maker-sier-white-ranking/ | 0 |
| [ ] | https://saiyo-ura.com/sier-ses-docchi/ | 0 |

### Geekly（s00000016183001）— 候補5記事

| 確認 | URL | GSCクリック（3か月） |
|---|---|---:|
| [ ] | https://saiyo-ura.com/geekly-hyouban/ | 7 |
| [ ] | https://saiyo-ura.com/seisei-ai-engineer-nenshu/ | 2 |
| [ ] | https://saiyo-ura.com/seisei-ai-it-tensyoku-guide/ | 2 |
| [ ] | https://saiyo-ura.com/it-tensyoku-syokusyu/ | 0 |
| [ ] | https://saiyo-ura.com/sier-consul-webkei-chigai/ | 0 |

### 第二新卒エージェントneo（s00000018427001）— 候補9記事

| 確認 | URL | GSCクリック（3か月） |
|---|---|---:|
| [ ] | https://saiyo-ura.com/itpassport-kihonjoho-2027-henkou/ | 95 |
| [ ] | https://saiyo-ura.com/it-passport-kihonjoho-ukaranai/ | 18 |
| [ ] | https://saiyo-ura.com/it-passport-iminai/ | 5 |
| [ ] | https://saiyo-ura.com/it-mikeiken-shokumukeirekisho-shorui-senko/ | 4 |
| [ ] | https://saiyo-ura.com/it-passport-kihonjoho-ikashikata/ | 4 |
| [ ] | https://saiyo-ura.com/it-tensyoku-mikeiken-1ji-mensetsu/ | 4 |
| [ ] | https://saiyo-ura.com/20dai-kohan-tenshoku-genjitsu/ | 1 |
| [ ] | https://saiyo-ura.com/mikeiken-it-tensyoku-2026/ | 0 |
| [ ] | https://saiyo-ura.com/uzuz-hyouban-jinji/ | 0 |
