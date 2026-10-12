# STEP3：配置の改善案（上位10記事）2026-10-12

根拠：`step3_materials.md`（10記事の見出しとパックの位置）、`program_conditions.md`（案件の掲載条件）、2111・2112 の中身（運営者から受領）。

---

## 0. 2112 の中身から分かったこと（STEP2の訂正を含む）

- 2112 の中には、レバテックダイレクトの0.gif（`www11.a8.net/0.gif?a8mat=4B1ILL+786GWQ+2JK4+4SNX5E`）と、**もしもの表示計測用画像（i.moshimo.com）が両方ある**。
  - STEP2・パック監査の「もしもの計測用画像はパックの中にない」は訂正する。正しくは「比較表（2111）の中にはなく、2112 にある」。
  - A8（10月1〜12日で64表示）ともしもの TechGO（42表示）がどちらも少なく、水準も近いのは、2つの画像が同じ場所（2112）にあるためと考えると説明がつく。仮説2の裏づけが強まった。
- 2112 は `position:absolute; left:-9999px;` で、画面の外に置かれている。SWELL の lazysizes は、画像が画面に入ったときに読み込む仕組み。**左に9999px外れた画像は、縦にスクロールしても画面に入らない**ので、ほとんど読み込まれていない可能性が高い（推定）。2112 のコメントにある「loading="lazy" を削除」は、lazysizes には効かない。
- 結論：計測用画像は**比較表の中、ボタンの直後**に置く（A8の標準の形）。表が画面に入ったときに読み込まれ、「表が表示された回数」が数えられる。2112 は空にする。

## 1. 作業の順番（同じ日に、まとめて行う）

計測の仕組みを変える日を1日にそろえないと、STEP4の効果測定の基準が崩れる。

1. **2112 を空にする**（下のHTML）。呼び出しが残っている記事があっても、二重には数えられない。
2. **2111 を差し替える**（下のHTML。計測用画像を表の中に移す）。
3. 上位10記事の配置を変える（2章）。2111 の呼び出しを22か所から10か所に減らす。
4. **上位10記事以外で 2111 を2か所以上呼んでいる記事**を、Search Regex で確認する。1107 /aws-saa-difficulty/ は3か所（AIの作業メモより）。1か所に減らす（作業メモの削除と同時に）。
5. 作業した日時を記録する（STEP4の基準日）。
6. **確認**：富士通の記事の公開ページのソース（Ctrl+U）で「0.gif」を検索する。
   - 件数が「表の数＋テキストリンクの数」と同じであること（富士通は 表1＋テキストリンク2＝3件の想定）。
   - 0.gif の行が、表のボタンの直後にあること。
   - `data-src` に書き換わっていてもよい（表が画面に入れば読み込まれる）。
   - A8の管理画面で、翌日以降に表示数が増えているかを見る。

## 2. パックの構成（作り直し後）

| パック | ブログパーツ | 中身 | 使う記事 |
|---|---|---|---|
| A（改） | 2111（上書き） | レバテックダイレクト＋テックゴー。計測用画像を表の中へ。対象条件を掲載条件に合わせる | 1462・1449・1143・1479・664・1809＋上位10記事以外の 2111 の呼び出し先 |
| J（新規） | 新しく作る | **JAC＋レバテックダイレクト**（管理・専門職・ハイクラス向け） | 979・1489・1827 |
| N（新規） | 新しく作る | **第二新卒エージェントneo**（20代向け） | 1790 |
| ピクセル | 2112（空にする） | なし | ― |
| 学習系 | 記事ごとの差し込み枠 | 【②-2 の資料を受け取ってから作る】 | 664・1790・1809・1462・1827・1143 |

- **Geekly は今回の10記事では使わない。** 役割がJAC（経験者・職種を問わない）と重なるうえ、成果地点が「60日以内の面談完了」と重い。年齢・未経験の表現の制限も強い。報酬額を見てから、もう一度検討する。
- テックゴーは 2111 に残し、**もしも（14,000円）からA8（18,000円）に切り替える**（2026-10-12 運営者判断）。A8で「採用のウラ側」を選んで発行し直す。835・892 の TechGO（A8・サイト001で発行）は使わない。ただし、パックにある「10,000件以上（2026年7月時点）」「模擬面接の回数に制限なし」「1Day選考会」「ITコンサル・メガベンチャーの求人が豊富」は、掲載条件の資料を受け取っていないので【要確認】（⑥）。

---

## 3. 記事ごとの配置案

表記の決まり
- 【削除】今ある呼び出し・文を消す　【置く】新しく置く　【残す】位置を変えずに残す
- 「一文」は、パックやリンクの直前に入れる段落。運営者の体験談・経歴は書いていない。

### 979 /fujitsu-nenshu-hyouka-jinji-me/（月約680）— 主力をJACに切り替える

| | 位置 | 案件 | 形式 | 添える一文 |
|---|---|---|---|---|
| 【削除】 | 導入の吹き出し「IT転職で失敗したくない方へ…」と [2111]① | ― | ― | ― |
| 【置く】主 | H3「【重要】富士通は中途入社のほうが年収が高い」の採用のウラ側メモの直後 | JAC＋レバテックダイレクト | **パックJ** | 「LevelやSPIRITの確認を、自分から切り出しにくいと感じる方は、エージェントに確認を任せる方法があります。管理・専門職の転職に強いJACと、エンジニアの方なら企業から直接スカウトが届くレバテックダイレクトを比べてみてください。」 |
| 【置く】 | H2「課長・部長は何レベル？」の最後の採用のウラ側メモの直後（今の [2111]② の位置。表は消す） | JAC | テキストリンク（VCで発行） | 「ポジションの等級をエージェント経由で確認したい方は、【JACリクルートメント（VCのテキストリンク）】に相談できます。年収600万円以上の方が中心のサービスです。」 |
| 【置く】 | H2「まとめ」の吹き出し「IT転職を成功させるためには…」を置き換え（[2111]③ は消す） | JAC・レバテックダイレクト | テキストリンク2行 | 「富士通への応募を考えている方は、まずLevelとSPIRITの確認から。オファー面談の前に、外の評価も知っておくと判断しやすくなります。」＋箇条書き「管理・専門職、年収600万円以上の方 → 【JAC】」「エンジニア・クリエイターの実務経験がある方 → 【レバテックダイレクト】」 |
| 【削除】 | [2112] | ― | ― | ― |

- ずれの指摘：読者の半分以上は営業・企画・コーポレート職（本文のOpenWorkのデータで、エンジニア・SEは46%）。レバテックダイレクトは「エンジニア、クリエイター未経験者」を否認するので、今のパックAではその読者が成果にならない。JAC（職種を問わず、年収600万円以上）が主になる。
- JACの年収の表現は「600万〜1500万」「800万〜1500万」の2つ以外は使えない。この記事の本文の年収（Levelのレンジ）は記事の情報であって、JACの訴求ではないので、表やリンクの文には混ぜない。

### 664 /ipa-exam-reform-2027/（月約290）— 学習系を主に、転職は1か所

| | 位置 | 案件 | 形式 | 添える一文 |
|---|---|---|---|---|
| 【置く】主 | H3「『応用情報がなくなるから、今のうちに取るべき』は本当か」の番号付きリスト（対策の材料／免除）の直後 | 学習系【②-2】 | 差し込み枠（テキストリンク＋必要ならバナー） | 「2026年度の試験は、範囲も出題形式も変わりません。今の過去問と参考書で、そのまま準備できます。」 |
| 【置く】 | H3「最後の2回はCBT方式。午前・午後は科目A・科目Bに」の「これまでの過去問や参考書が、そのまま使えます。」の直後 | 学習系【②-2】 | テキストリンク1行 | （リンクの文だけ） |
| 【残す】 | H2「まとめ」の後の [2111] | レバテックダイレクト＋テックゴー | パックA（改） | 直前に「応用情報の合格と今の実務経験が、ほかの会社でどう評価されるかを知りたいエンジニアの方は、企業から届くスカウトで確かめられます。」 |
| 【削除】 | [2112] | ― | ― | ― |

- ずれの指摘：読者には学生・基本情報を勉強中の人が多い。レバテックダイレクトとテックゴーは未経験を対象外にしているので、転職の表はまとめに1か所だけにする。学習系の需要は2027年3月（後期試験）まで続くので、こちらを主にする。

### 1462 /database-specialist-haishi/（月約180）

| | 位置 | 案件 | 形式 | 添える一文 |
|---|---|---|---|---|
| 【削除】 | 囲み「この記事で分かること」の後の [2111]① | ― | ― | ― |
| 【残す】 | H3「新試験『プロフェッショナルデジタルスキル試験』は転職で武器になるか？」の採用のウラ側メモの直後の [2111]② | レバテックダイレクト＋テックゴー | パックA（改） | 「DBの設計やチューニングの経験が、今の職場の外でどう評価されるかは、企業から届くスカウトで確かめられます。」 |
| 【置く】 | H3「2026年度の受験スケジュール」の「今から勉強を始めても十分間に合います。」の直後 | 学習系【②-2】 | 差し込み枠 | 「2026年度のデータベーススペシャリスト試験は、2027年2月頃の実施予定です。」 |
| 【削除】 | 記事の最後の [2111]③・[2112] | ― | ― | ― |

### 1489 /it-strategist-haishi/（月約170）

| | 位置 | 案件 | 形式 | 添える一文 |
|---|---|---|---|---|
| 【削除】 | H3「新試験『マネジメント領域』の合格は、書類でどう見えそうか」の後の誘導文「STの勉強で身につけたことや…確かめられます。」と [2111]① | ― | ― | ― |
| 【置く】 | H3「人事から見た答え｜書類では強い、決め手は経験と取った理由」の採用のウラ側メモの後（今の [2111]② の位置。誘導文を差し替え） | JAC＋レバテックダイレクト | **パックJ** | 「STの出題範囲と重なる仕事（IT企画・ITコンサル・上流工程）の求人を見てみると、合格の使いどころが具体的になります。管理・専門職に強いJACと、エンジニアの実務経験がある方向けのレバテックダイレクトを比べてみてください。」 |
| 【削除】 | よくある質問の後の [2112] | ― | ― | ― |

- ずれの指摘：読者には40代前後・IT企画・部長職が多い。レバテックダイレクトはエンジニア・クリエイターの経験者に限られ、IT企画職が「未経験者」として否認されないかは【要確認】。JACを主にする。
- 学習系は置かない（最後の回の申込締切が10/24。提携の審査を考えると間に合わない）。

### 1449 /network-specialist-haishi/（月約100）

| | 位置 | 案件 | 形式 | 添える一文 |
|---|---|---|---|---|
| 【削除】 | H3「新試験…は転職で武器になるか？」の吹き出し（2026年度中に合格しておくほうが…）の後の [2111]① | ― | ― | ― |
| 【置く】 | H3「ただし『資格名だけ』で評価が上がる時代は終わりつつある」の吹き出しの直後 | レバテックダイレクト＋テックゴー | パックA（改） | 「ネットワークの設計・構築の実務経験がある方は、その経験にどんな企業から声がかかるかを、スカウトで確かめられます。」 |
| 【削除】 | 記事の最後の [2111]②・[2112] | ― | ― | ― |

- 学習系は置かない（申込締切10/24、試験は11/23まで）。

### 1143 /aws-sap-difficulty-salary/（月約90）

| | 位置 | 案件 | 形式 | 添える一文 |
|---|---|---|---|---|
| 【削除】 | H3「『オンプレ経験＋SAP』が転職市場で評価される理由」のdodaの段落の後の [2111]① | ― | ― | ― |
| 【置く】 | H3「SAPが開くキャリアパス（クラウドアーキテクト・SRE・コンサルタント）」の採用のウラ側メモの直後 | レバテックダイレクト＋テックゴー | パックA（改） | 「AWSの設計・構築の経験がある方は、クラウドの経験にどんな企業から声がかかるかを、スカウトで確かめられます。」 |
| 【置く】 | H3「おすすめの教材と学習ステップ」のステップ2（Udemyなどの問題集）の段落の後 | 学習系【②-2。Udemy・参考書を扱える案件があるか要確認】 | テキストリンク | 「問題集で演習するときは、解説を読んで公式ドキュメントで確かめる使い方が効きます。」（本文の内容に沿った一文） |
| 【削除】 | 記事の最後の [2111]②・[2112] | ― | ― | ― |

- ずれの指摘：読者と案件がいちばん合う記事なのに、今の表は「dodaの求人を見ると…」の直後にある。他社を思い浮かべさせた直後に別の会社の表を出す形をやめ、キャリアパスの話の後に移す。

### 1809 /professional-digital-skill-exam/（月約80）— 学習系を主に

| | 位置 | 案件 | 形式 | 添える一文 |
|---|---|---|---|---|
| 【削除】 | 冒頭の ※注記の後の [2111]① | ― | ― | ― |
| 【置く】主 | H3「シラバス案が出た今、できること」の箇条書きの直後 | 学習系【②-2】 | 差し込み枠 | 「受ける領域を決めたら、IPAのシラバス案と並行して、3領域に共通の知識（デジタル戦略・AI基礎・セキュリティ）から固めておくと進めやすくなります。」 |
| 【残す】 | H2「まとめ」の後の [2111]② | レバテックダイレクト＋テックゴー | パックA（改） | 「すでに実務経験があり、受験と並行して転職も考えている方は、今の経験の評価を先に知っておくと、受ける領域も決めやすくなります。」 |
| 【削除】 | [2112] | ― | ― | ― |

### 1827 /project-manager-exam-reform/（月約80）

| | 位置 | 案件 | 形式 | 添える一文 |
|---|---|---|---|---|
| 【削除】 | 囲み「この記事で分かること」の後の [2111]① | ― | ― | ― |
| 【置く】 | H2「転職・キャリアで評価されるのか」の採用のウラ側メモの後（今の [2111]② の位置） | JAC＋レバテックダイレクト | **パックJ** | 「PMとしての経験を活かせる求人は、管理・専門職に強いエージェントに相談すると探しやすくなります。エンジニアとしての実務経験がある方は、企業から直接スカウトを受け取る方法もあります。」 |
| 【削除】 | 同じ位置の [2112] | ― | ― | ― |
| 【置く】 | H2「受験を決めるためのチェックポイント」の「受けると決めたら、次にやること」の番号付きリストの直後 | 学習系【②-2】 | 差し込み枠 | 「2026年度のプロジェクトマネージャ試験は、後期（2027年2〜3月）だけの実施です。論文の対策は早めに始めてください。」（日程は 664 の本文による） |

- 年収の表（PMO・コンサルPM）と同じ章に置くが、JACの訴求文に年収の数字は入れない（JACが認める表現は「600万〜1500万」「800万〜1500万」のみ）。

### 1479 /system-architect-haishi/（月約70）

| | 位置 | 案件 | 形式 | 添える一文 |
|---|---|---|---|---|
| 【残す】 | H3「『アーキテクト』を明示的に置く企業が増えている」の最後の [2111]① | レバテックダイレクト＋テックゴー | パックA（改） | 「要件定義や基本設計の経験がある方は、その経験にどんな企業から声がかかるかを、スカウトで確かめられます。」 |
| 【削除】 | 記事の最後の [2111]②・[2112] | ― | ― | ― |

- 学習系は置かない（申込締切10/24）。
- 別件（急ぎ）：本文に2026年度の日程（申込 10/6〜10/24、科目A 10/17〜10/27、科目B 11/11〜11/23）がなく、「11月頃」としか書いていない。今が検索の山なので、今週中に直すほうがよい。

### 1790 /itpassport-kihonjoho-2027-henkou/（月約60）— 表を全部入れ替える

| | 位置 | 案件 | 形式 | 添える一文 |
|---|---|---|---|---|
| 【削除】 | 冒頭の [2111]① | ― | ― | ― |
| 【削除】 | H3「迷ったら『受験の目的』で決めましょう」の段落「自分だけで判断が難しいときは、IT業界に詳しい転職エージェントに相談してみると…」と [2111]② | ― | ― | ― |
| 【削除】 | まとめの段落「『自分の場合はどう動くのがいいだろう？』と迷ったら、IT業界に強い転職エージェントに相談して…」と [2111]③・[2112] | ― | ― | ― |
| 【置く】 | H3「科目A免除制度は継続される」の箇条書きの直後 | 学習系【②-2。科目A免除の対象講座を扱える案件があれば最適】 | 差し込み枠 | 「科目Aの免除を使うには、対象講座の受講と修了試験の合格が必要です。」（本文の内容に沿った一文） |
| 【置く】 | H3「これからの基本情報対策で押さえたい勉強法」の表の直後 | 学習系【②-2】 | テキストリンク | 「教材は、2023年以降の出題に対応した最新版を選んでください。」 |
| 【置く】 | H3「なかなか受からないときの考え方」の箇条書きの直後（内部リンク 207 の前） | 第二新卒エージェントneo | **パックN** | 「経歴に自信がない20代の方は、書類づくりから一緒に進めてくれるエージェントに相談する方法もあります。新卒での就職を希望する学生の方は対象外です。」 |

- ずれの指摘：今のパックAの2案件は、どちらも読者の大半（学生・未経験・非IT職）が対象外。そのうえ、試験の時期を「転職エージェントに相談」と誘導していて、読者の悩みとつながっていない。neo は「試験の相談」ではなく、本文の「運用・ヘルプデスクなど、現場でITに触れる仕事から始める」という話の後に置く。

### 呼び出しの数（変更前 → 変更後）

| 記事 | 表（変更前） | 表（変更後） | テキストリンク | 学習系の枠 |
|---|---|---|---|---|
| 979 | 3 | 1（J） | 2か所 | ― |
| 664 | 1 | 1（A） | ― | 2 |
| 1462 | 3 | 1（A） | ― | 1 |
| 1489 | 2 | 1（J） | ― | ― |
| 1449 | 2 | 1（A） | ― | ― |
| 1143 | 2 | 1（A） | ― | 1 |
| 1809 | 2 | 1（A） | ― | 1 |
| 1827 | 2 | 1（J） | ― | 1 |
| 1479 | 2 | 1（A） | ― | ― |
| 1790 | 3 | 1（N） | ― | 2 |
| 合計 | **22** | **10** | 2 | 8 |

---

## 4. 貼れる形のHTML

共通の決まり
- 計測用画像の行は、運営者がA8・もしもで発行したものをそのまま使う。レバテックダイレクトとテックゴーの行は、受領した 2112 の中身から写した。
- JAC・neo のコードはまだ受け取っていないので、`【…】` の差し込み枠にしてある。**差し込み枠を埋めずに公開しない**（リンクが壊れる）。
- 3つのパックは同じCSS（`.saiyo-cta`）を使う。中身を同じにしてあるので、1ページに2つ入っても崩れない。パックC・D・E は CSS が少しずつ違うので、後で同じものにそろえる。
- 「人事コメント」は運営者の言葉。新しいパック（J・N）は、運営者の依頼で案を出し、おすすめの案を入れた（2026-10-12）。体験談ではなく、既存記事の考え方に沿った意見・助言の形。
  - パックJ（JAC）：A案「等級や年収の幅は…確認として企業に聞いてもらえます」（979 のメモが元）。別案 B「年収交渉は、根拠を示せる人ほど通ります。外の評価を知っておくことが、いちばんの根拠になります。」／C「提示された金額が高いか低いかは、同じ職種の相場を知らないと判断できません。」
  - パックN（neo）：C案「落ちた回数より、原因をどう直したかを話せるかが見られます…」（1790 のメモが元）。別案 A「経歴に自信がないときほど、書類は第三者に見てもらう価値があります。自分では弱みだと思っていた経験も、伝え方しだいで評価の材料になります。」／B「資格の勉強と就職活動は並行して進められます。書類と面接は、ひとりで抱え込まずに人の手を借りてください。」

### 4-1. 2112（空にする）

```html
<!-- wp:html -->
<!-- 採用のウラ側 / パックA_インプレピクセル id=2112 -->
<!-- 2026-10 計測用画像は比較表（2111）の中、ボタンの直後へ移動。このパーツは空のまま残す（記事に呼び出しが残っていても二重に数えないため）。中身を戻さないこと。 -->
<!-- /wp:html -->
```

### 4-2. 2111（パックA・改。上書き）

変更点：計測用画像（A8の0.gif・もしもの表示計測用画像）をボタンの直後へ／タイトルを記事の種類を選ばない形に／レバテックダイレクトの「面談不要・登録だけで完結」「IT・Web実務経験者」「転職する気が固まっていなくて構いません」「転職を決めていなくても登録できる」を、掲載条件とPR文に合わせて修正。

```html
<!-- wp:html -->
<!-- 採用のウラ側 / パックA_比較表 id=2111（2026-10 計測用画像を表の中へ移動・対象条件を掲載条件に合わせて修正） -->
<style>
.saiyo-cta{background:#f5f5f0;border-radius:12px;padding:20px 16px;font-family:sans-serif;color:#3d3d3d;max-width:100%;box-sizing:border-box;margin:28px 0;}
.saiyo-cta *{box-sizing:border-box}
.saiyo-cta__badge-wrap{text-align:center;margin-bottom:8px;}
.saiyo-cta__badge{display:inline-block;background:#e8b44a;color:#3d3d3d;font-size:13px;font-weight:700;padding:6px 14px;border-radius:20px;}
.saiyo-cta__title{text-align:center;font-size:17px;font-weight:700;margin:8px 0 6px;line-height:1.6;}
.saiyo-cta__lead{text-align:center;font-size:12.5px;color:#77776e;margin:0 0 16px;line-height:1.7;}
.saiyo-cta__panel{background:#fff;border-radius:8px;overflow:hidden;border:1px solid #e0e0d8;}
.saiyo-cta__header-row{display:grid;grid-template-columns:22% 20% 38% 20%;background:#f0f0e8;padding:10px 8px;font-size:12px;font-weight:700;text-align:center;border-bottom:1px solid #e0e0d8;}
.saiyo-cta__row{display:grid;grid-template-columns:22% 20% 38% 20%;padding:18px 8px;border-bottom:1px solid #e0e0d8;align-items:center;position:relative;}
.saiyo-cta__row:last-child{border-bottom:none;}
.saiyo-cta__row--best{background:#fdfaf1;}
.saiyo-cta__rank{position:absolute;top:0;left:0;background:#e8b44a;color:#3d3d3d;font-size:11px;font-weight:700;padding:3px 10px;border-radius:0 0 6px 0;}
.saiyo-cta__name{text-align:center;}
.saiyo-cta__name-link{display:block;color:inherit;text-decoration:none;transition:opacity .2s;}
.saiyo-cta__name-link:hover{opacity:.85;color:inherit;}
.saiyo-cta__logo{display:block;margin:0 auto 6px;max-width:100%;height:auto;border:none;}
.saiyo-cta__logo--text{display:flex;align-items:center;justify-content:center;width:100px;height:60px;margin:0 auto 6px;background:#fff;border:1px solid #ddd8cc;border-bottom:3px solid #c94444;border-radius:4px 4px 2px 2px;font-size:13px;font-weight:700;line-height:1.3;color:#2f2f28;text-align:center;letter-spacing:.01em;}
.saiyo-cta__name-text{font-size:13px;font-weight:700;}
.saiyo-cta__count{text-align:center;color:#c94444;font-weight:700;font-size:14px;line-height:1.4;}
.saiyo-cta__count-sub{font-size:10.5px;color:#888;font-weight:400;display:block;margin-top:4px;line-height:1.5;}
.saiyo-cta__target{display:block;margin-top:6px;font-size:10.5px;color:#66665e;font-weight:400;background:#f0f0e8;border-radius:3px;padding:4px 5px;line-height:1.5;}
.saiyo-cta__point{font-size:12px;padding:0 8px;line-height:1.7;}
.saiyo-cta__point-title{color:#c94444;font-weight:700;margin-bottom:4px;}
.saiyo-cta__hr{background:#f7f4ea;border-left:3px solid #e8b44a;padding:7px 9px;margin:0 0 6px;border-radius:0 3px 3px 0;font-size:12px;line-height:1.65;color:#4a4a42;}
.saiyo-cta__btn-cell{text-align:center;}
.saiyo-cta__btn{display:inline-block;background:#6baa95;color:#fff !important;padding:11px 14px;text-decoration:none;border-radius:4px;font-size:13px;font-weight:700;transition:opacity .2s;line-height:1.35;}
.saiyo-cta__btn:hover{opacity:.85;color:#fff !important;}
.saiyo-cta__btn small{display:block;font-size:10px;font-weight:400;opacity:.92;margin-top:3px;}
.saiyo-cta__footer{text-align:center;font-size:11px;color:#8a8a82;margin:12px 2px 0;line-height:1.7;}
@media (max-width:600px){
.saiyo-cta__header-row{display:none;}
.saiyo-cta__row{grid-template-columns:1fr;gap:12px;padding:26px 14px 18px;text-align:center;}
.saiyo-cta__name-text{font-size:15px;}
.saiyo-cta__logo--text{width:132px;height:70px;font-size:15px;}
.saiyo-cta__point{padding:0;text-align:left;}
.saiyo-cta__btn{padding:14px 20px;font-size:14.5px;width:100%;max-width:320px;}
}
</style>

<div class="saiyo-cta">
  <div class="saiyo-cta__badge-wrap"><span class="saiyo-cta__badge">登録・相談は無料です</span></div>
  <p class="saiyo-cta__title">今の経験が、ほかの会社で<br>どう評価されるかを知っておく</p>
  <p class="saiyo-cta__lead">人事の立場から言うと、比較対象を持たないまま決めている人が一番損をしています。</p>
  <div class="saiyo-cta__panel">
    <div class="saiyo-cta__header-row"><div>サービス名</div><div>特徴・対象</div><div>ポイント</div><div>公式サイト</div></div>
    <div class="saiyo-cta__row saiyo-cta__row--best"><span class="saiyo-cta__rank">迷ったらここ</span>
      <div class="saiyo-cta__name">
        <a class="saiyo-cta__name-link" href="https://px.a8.net/svt/ejp?a8mat=4B1ILL+786GWQ+2JK4+4SNX5E" rel="nofollow sponsored">
          <div class="saiyo-cta__logo--text">レバテック<br>ダイレクト</div>
          <div class="saiyo-cta__name-text">スカウト型</div>
        </a>
      </div>
      <div class="saiyo-cta__count">企業から<br>直接スカウト<span class="saiyo-cta__count-sub">登録は無料</span><span class="saiyo-cta__target">エンジニア・クリエイターの<br>実務経験がある方／50歳未満<br>（未経験の方は対象外）</span></div>
      <div class="saiyo-cta__point">
        <div class="saiyo-cta__hr"><b>人事コメント：</b><b>今の自分にどんな企業がいくらで声をかけるか</b>を知らないまま条件交渉している人が、一番損をしています。</div>
        <div class="saiyo-cta__point-title">【スカウトで市場価値を知る】</div>
        ✓ 経験やスキルに興味を持った企業からスカウトが届く<br>
        ✓ 求人との相性（マッチ率）を数値で確かめられる<br>
        ✓ リモート可否・フレックスなど細かい条件で探せる
      </div>
      <div class="saiyo-cta__btn-cell">
        <a class="saiyo-cta__btn" href="https://px.a8.net/svt/ejp?a8mat=4B1ILL+786GWQ+2JK4+4SNX5E" rel="nofollow sponsored">無料で登録する ›<small>この端末のまま完了を</small></a>
        <img border="0" width="1" height="1" src="https://www11.a8.net/0.gif?a8mat=4B1ILL+786GWQ+2JK4+4SNX5E" alt="">
      </div>
    </div>
    <div class="saiyo-cta__row">
      <div class="saiyo-cta__name">
        <a class="saiyo-cta__name-link" href="【ここを、A8で「採用のウラ側」を選んで発行したTechGoのクリック用URLに置き換える】" rel="nofollow sponsored">
          <div class="saiyo-cta__logo--text">テックゴー<br>（TechGo）</div>
          <div class="saiyo-cta__name-text">エージェント型</div>
        </a>
      </div>
      <div class="saiyo-cta__count">ITエンジニア<br>専門<span class="saiyo-cta__count-sub">高年収の正社員ポジション</span><span class="saiyo-cta__target">実務2年以上のITエンジニア<br>20代後半〜30代の支援が中心<br>（学生の方は対象外）</span></div>
      <div class="saiyo-cta__point">
        <div class="saiyo-cta__hr"><b>人事コメント：</b>模擬面接の回数に制限がありません。<b>実績はあるのに面接で伝えきれない人</b>には、ここが一番効きます。</div>
        <div class="saiyo-cta__point-title">【面接対策を何度でも】</div>
        ✓ 模擬面接の回数に制限がない<br>
        ✓ 土曜1日で面接を終えられる1Day選考会がある（参加には事前の面談と書類選考の通過が必要）<br>
        ✓ ITコンサル・メガベンチャーなど高年収のポジションを扱う
      </div>
      <div class="saiyo-cta__btn-cell">
        <a class="saiyo-cta__btn" href="【ここを、A8で「採用のウラ側」を選んで発行したTechGoのクリック用URLに置き換える】" rel="nofollow sponsored">無料で相談する ›<small>入力は数分で完了</small></a>
        <!-- ここに、A8で発行したTechGoのコードの 0.gif の img の行をそのまま貼る -->
      </div>
    </div>
  </div>
  <p class="saiyo-cta__footer">スマートフォンでご覧の方は、そのままこの端末で登録を完了してください（別の端末やブラウザに移ると正しく処理されない場合があります）。<br>対象条件・求人数は各社公式サイトの表記に基づきます。</p>
</div>
<!-- /wp:html -->
```

テックゴーの行は、**A8版に切り替え済み**（2026-10-12 運営者判断。A8 18,000円＞もしも 14,000円）。
- リンク2か所と計測用画像1行は、A8で「採用のウラ側」を選んで発行したものに置き換える。差し込み枠を埋めないまま公開しない。
- ロゴは、もしもの素材画像（image.moshimo.com）をA8のリンクと組み合わせるわけにいかないので、ほかの行と同じ文字のロゴにした。A8の素材のバナーを使う場合は、発行したコードをそのまま使う。
- もしものリンクと計測用画像（i.moshimo.com）は、このパックから外れる。もしもの TechGO の提携は、ほかに使っている場所がなければそのままでよい。
- 2026-10-12 A8 の TechGo のプログラム詳細と照らし合わせて、文言を直した。
  - 「10,000件以上（2026年7月時点）」：A8のPR文に根拠がないので外し、「ITエンジニア専門／高年収の正社員ポジション」（PR文の記載）にした。公式サイトなどで根拠を確認できれば、時点を付けて戻してよい。
  - 「志望企業の内情まで踏み込む」：PR文に根拠がないので外し、「模擬面接の回数に制限がない」（PR文の記載）にした。
  - 「1Day選考会あり」：PR文に「事前の面談と書類選考の通過が参加条件」とあるので、条件を書き足した。
  - 「ITコンサル・メガベンチャーの求人が豊富」：PR文は「高収入求人が豊富」「ITコンサルやメガベンチャーなどのポジションが人気」。言い方を「ITコンサル・メガベンチャーなど高年収のポジションを扱う」に直した。
  - 「【面談の質に定評】」は「【面接対策を何度でも】」に直した（「定評」の根拠がないため）。
  - 対象に「学生の方は対象外」を足した（否認条件「学生からの申込」）。
  - 人事コメント（運営者の言葉）はPR文と合っているので、そのまま。

### 4-3. パックJ（新規：JAC＋レバテックダイレクト）

SWELL → ブログパーツ → 新規追加 → タイトル「パックJ_比較表（JAC＋レバテックダイレクト）」→ カスタムHTMLブロックに貼る。保存後に表示されるIDを記録する（記事にはそのIDで `[blog_parts id="…"]` を入れる）。

```html
<!-- wp:html -->
<!-- 採用のウラ側 / パックJ_比較表（JAC＋レバテックダイレクト）2026-10 新規。使う記事：979・1489・1827 -->
<style>
/* パックA（2111）と同じCSS。変えるときは全パックを同時に変える */
.saiyo-cta{background:#f5f5f0;border-radius:12px;padding:20px 16px;font-family:sans-serif;color:#3d3d3d;max-width:100%;box-sizing:border-box;margin:28px 0;}
.saiyo-cta *{box-sizing:border-box}
.saiyo-cta__badge-wrap{text-align:center;margin-bottom:8px;}
.saiyo-cta__badge{display:inline-block;background:#e8b44a;color:#3d3d3d;font-size:13px;font-weight:700;padding:6px 14px;border-radius:20px;}
.saiyo-cta__title{text-align:center;font-size:17px;font-weight:700;margin:8px 0 6px;line-height:1.6;}
.saiyo-cta__lead{text-align:center;font-size:12.5px;color:#77776e;margin:0 0 16px;line-height:1.7;}
.saiyo-cta__panel{background:#fff;border-radius:8px;overflow:hidden;border:1px solid #e0e0d8;}
.saiyo-cta__header-row{display:grid;grid-template-columns:22% 20% 38% 20%;background:#f0f0e8;padding:10px 8px;font-size:12px;font-weight:700;text-align:center;border-bottom:1px solid #e0e0d8;}
.saiyo-cta__row{display:grid;grid-template-columns:22% 20% 38% 20%;padding:18px 8px;border-bottom:1px solid #e0e0d8;align-items:center;position:relative;}
.saiyo-cta__row:last-child{border-bottom:none;}
.saiyo-cta__row--best{background:#fdfaf1;}
.saiyo-cta__rank{position:absolute;top:0;left:0;background:#e8b44a;color:#3d3d3d;font-size:11px;font-weight:700;padding:3px 10px;border-radius:0 0 6px 0;}
.saiyo-cta__name{text-align:center;}
.saiyo-cta__name-link{display:block;color:inherit;text-decoration:none;transition:opacity .2s;}
.saiyo-cta__name-link:hover{opacity:.85;color:inherit;}
.saiyo-cta__logo{display:block;margin:0 auto 6px;max-width:100%;height:auto;border:none;}
.saiyo-cta__logo--text{display:flex;align-items:center;justify-content:center;width:100px;height:60px;margin:0 auto 6px;background:#fff;border:1px solid #ddd8cc;border-bottom:3px solid #c94444;border-radius:4px 4px 2px 2px;font-size:13px;font-weight:700;line-height:1.3;color:#2f2f28;text-align:center;letter-spacing:.01em;}
.saiyo-cta__name-text{font-size:13px;font-weight:700;}
.saiyo-cta__count{text-align:center;color:#c94444;font-weight:700;font-size:14px;line-height:1.4;}
.saiyo-cta__count-sub{font-size:10.5px;color:#888;font-weight:400;display:block;margin-top:4px;line-height:1.5;}
.saiyo-cta__target{display:block;margin-top:6px;font-size:10.5px;color:#66665e;font-weight:400;background:#f0f0e8;border-radius:3px;padding:4px 5px;line-height:1.5;}
.saiyo-cta__point{font-size:12px;padding:0 8px;line-height:1.7;}
.saiyo-cta__point-title{color:#c94444;font-weight:700;margin-bottom:4px;}
.saiyo-cta__hr{background:#f7f4ea;border-left:3px solid #e8b44a;padding:7px 9px;margin:0 0 6px;border-radius:0 3px 3px 0;font-size:12px;line-height:1.65;color:#4a4a42;}
.saiyo-cta__btn-cell{text-align:center;}
.saiyo-cta__btn{display:inline-block;background:#6baa95;color:#fff !important;padding:11px 14px;text-decoration:none;border-radius:4px;font-size:13px;font-weight:700;transition:opacity .2s;line-height:1.35;}
.saiyo-cta__btn:hover{opacity:.85;color:#fff !important;}
.saiyo-cta__btn small{display:block;font-size:10px;font-weight:400;opacity:.92;margin-top:3px;}
.saiyo-cta__footer{text-align:center;font-size:11px;color:#8a8a82;margin:12px 2px 0;line-height:1.7;}
@media (max-width:600px){
.saiyo-cta__header-row{display:none;}
.saiyo-cta__row{grid-template-columns:1fr;gap:12px;padding:26px 14px 18px;text-align:center;}
.saiyo-cta__name-text{font-size:15px;}
.saiyo-cta__logo--text{width:132px;height:70px;font-size:15px;}
.saiyo-cta__point{padding:0;text-align:left;}
.saiyo-cta__btn{padding:14px 20px;font-size:14.5px;width:100%;max-width:320px;}
}
</style>

<div class="saiyo-cta">
  <div class="saiyo-cta__badge-wrap"><span class="saiyo-cta__badge">登録・相談は無料です</span></div>
  <p class="saiyo-cta__title">提示された条件が妥当かは<br>外の評価と比べて初めて分かります</p>
  <p class="saiyo-cta__lead">職種と経験に合わせて、相談先を選んでください。</p>
  <div class="saiyo-cta__panel">
    <div class="saiyo-cta__header-row"><div>サービス名</div><div>特徴・対象</div><div>ポイント</div><div>公式サイト</div></div>
    <div class="saiyo-cta__row saiyo-cta__row--best"><span class="saiyo-cta__rank">職種を問わず</span>
      <div class="saiyo-cta__name">
        <a class="saiyo-cta__name-link" href="//ck.jp.ap.valuecommerce.com/servlet/referral?sid=3765202&amp;pid=892724768" rel="nofollow sponsored">
          <div class="saiyo-cta__logo--text">JAC<br>リクルートメント</div>
          <div class="saiyo-cta__name-text">エージェント型</div>
        </a>
      </div>
      <div class="saiyo-cta__count">管理・専門職<span class="saiyo-cta__count-sub">ミドル・ハイクラス向け</span><span class="saiyo-cta__target">年収600万円以上の方が中心<br>営業・管理部門・エンジニアなど</span></div>
      <div class="saiyo-cta__point">
        <div class="saiyo-cta__hr"><b>人事コメント：</b>等級や年収の幅は、候補者本人からは聞きにくい項目です。<b>エージェントを通せば、確認として企業に聞いてもらえます。</b></div>
        <div class="saiyo-cta__point-title">【管理・専門職の転職に特化】</div>
        ✓ 管理部門・営業・エンジニアなど職種を問わず相談できる<br>
        ✓ ミドル・ハイクラス向けの求人を扱う<br>
        ✓ 東京・横浜・名古屋・大阪などに拠点がある
      </div>
      <div class="saiyo-cta__btn-cell">
        <a class="saiyo-cta__btn" href="//ck.jp.ap.valuecommerce.com/servlet/referral?sid=3765202&amp;pid=892724768" rel="nofollow sponsored"><img src="//ad.jp.ap.valuecommerce.com/servlet/gifbanner?sid=3765202&amp;pid=892724768" height="1" width="1" border="0">無料で相談する ›<small>この端末のまま完了を</small></a>
      </div>
    </div>
    <div class="saiyo-cta__row"><span class="saiyo-cta__rank">エンジニアなら</span>
      <div class="saiyo-cta__name">
        <a class="saiyo-cta__name-link" href="https://px.a8.net/svt/ejp?a8mat=4B1ILL+786GWQ+2JK4+4SNX5E" rel="nofollow sponsored">
          <div class="saiyo-cta__logo--text">レバテック<br>ダイレクト</div>
          <div class="saiyo-cta__name-text">スカウト型</div>
        </a>
      </div>
      <div class="saiyo-cta__count">企業から<br>直接スカウト<span class="saiyo-cta__count-sub">登録は無料</span><span class="saiyo-cta__target">エンジニア・クリエイターの<br>実務経験がある方／50歳未満<br>（未経験の方は対象外）</span></div>
      <div class="saiyo-cta__point">
        <div class="saiyo-cta__hr"><b>人事コメント：</b><b>今の自分にどんな企業がいくらで声をかけるか</b>を知らないまま条件交渉している人が、一番損をしています。</div>
        <div class="saiyo-cta__point-title">【スカウトで市場価値を知る】</div>
        ✓ 経験やスキルに興味を持った企業からスカウトが届く<br>
        ✓ 求人との相性（マッチ率）を数値で確かめられる<br>
        ✓ リモート可否・フレックスなど細かい条件で探せる
      </div>
      <div class="saiyo-cta__btn-cell">
        <a class="saiyo-cta__btn" href="https://px.a8.net/svt/ejp?a8mat=4B1ILL+786GWQ+2JK4+4SNX5E" rel="nofollow sponsored">無料で登録する ›<small>この端末のまま完了を</small></a>
        <img border="0" width="1" height="1" src="https://www11.a8.net/0.gif?a8mat=4B1ILL+786GWQ+2JK4+4SNX5E" alt="">
      </div>
    </div>
  </div>
  <p class="saiyo-cta__footer">スマートフォンでご覧の方は、そのままこの端末で登録を完了してください（別の端末やブラウザに移ると正しく処理されない場合があります）。<br>対象条件は各社公式サイトの表記に基づきます。</p>
</div>
<!-- /wp:html -->
```

JAC・neo のコードは 2026-10-12 に運営者が発行したものを入れた（JAC：VC sid=3765202・pid=892724768／neo：A8 a8mat=4B1ILL+72TKGQ+3Y6M+63H8I。72TKGQ はサイト002＝採用のウラ側）。JAC の計測用画像（gifbanner）は、発行コードと同じくリンクの中に置き、ボタンだけに入れた（社名のリンクには入れない。1回の表示で2回数えないため）。

JACの禁止事項に合わせた点：年収の数字は「600万円以上の方が中心」（利用者の特徴の記載）だけで、上限のある年収訴求は入れていない。取引企業のロゴ・メールのキャプチャーは使っていない。社名は文字で表示（ロゴ画像は使わない）。

### 4-4. パックN（新規：第二新卒エージェントneo）

```html
<!-- wp:html -->
<!-- 採用のウラ側 / パックN_20代（第二新卒エージェントneo）2026-10 新規。使う記事：1790 -->
<style>
/* パックA（2111）と同じCSS。変えるときは全パックを同時に変える */
.saiyo-cta{background:#f5f5f0;border-radius:12px;padding:20px 16px;font-family:sans-serif;color:#3d3d3d;max-width:100%;box-sizing:border-box;margin:28px 0;}
.saiyo-cta *{box-sizing:border-box}
.saiyo-cta__badge-wrap{text-align:center;margin-bottom:8px;}
.saiyo-cta__badge{display:inline-block;background:#e8b44a;color:#3d3d3d;font-size:13px;font-weight:700;padding:6px 14px;border-radius:20px;}
.saiyo-cta__title{text-align:center;font-size:17px;font-weight:700;margin:8px 0 6px;line-height:1.6;}
.saiyo-cta__lead{text-align:center;font-size:12.5px;color:#77776e;margin:0 0 16px;line-height:1.7;}
.saiyo-cta__panel{background:#fff;border-radius:8px;overflow:hidden;border:1px solid #e0e0d8;}
.saiyo-cta__header-row{display:grid;grid-template-columns:22% 20% 38% 20%;background:#f0f0e8;padding:10px 8px;font-size:12px;font-weight:700;text-align:center;border-bottom:1px solid #e0e0d8;}
.saiyo-cta__row{display:grid;grid-template-columns:22% 20% 38% 20%;padding:18px 8px;border-bottom:1px solid #e0e0d8;align-items:center;position:relative;}
.saiyo-cta__row:last-child{border-bottom:none;}
.saiyo-cta__row--best{background:#fdfaf1;}
.saiyo-cta__rank{position:absolute;top:0;left:0;background:#e8b44a;color:#3d3d3d;font-size:11px;font-weight:700;padding:3px 10px;border-radius:0 0 6px 0;}
.saiyo-cta__name{text-align:center;}
.saiyo-cta__name-link{display:block;color:inherit;text-decoration:none;transition:opacity .2s;}
.saiyo-cta__name-link:hover{opacity:.85;color:inherit;}
.saiyo-cta__logo{display:block;margin:0 auto 6px;max-width:100%;height:auto;border:none;}
.saiyo-cta__logo--text{display:flex;align-items:center;justify-content:center;width:100px;height:60px;margin:0 auto 6px;background:#fff;border:1px solid #ddd8cc;border-bottom:3px solid #c94444;border-radius:4px 4px 2px 2px;font-size:13px;font-weight:700;line-height:1.3;color:#2f2f28;text-align:center;letter-spacing:.01em;}
.saiyo-cta__name-text{font-size:13px;font-weight:700;}
.saiyo-cta__count{text-align:center;color:#c94444;font-weight:700;font-size:14px;line-height:1.4;}
.saiyo-cta__count-sub{font-size:10.5px;color:#888;font-weight:400;display:block;margin-top:4px;line-height:1.5;}
.saiyo-cta__target{display:block;margin-top:6px;font-size:10.5px;color:#66665e;font-weight:400;background:#f0f0e8;border-radius:3px;padding:4px 5px;line-height:1.5;}
.saiyo-cta__point{font-size:12px;padding:0 8px;line-height:1.7;}
.saiyo-cta__point-title{color:#c94444;font-weight:700;margin-bottom:4px;}
.saiyo-cta__hr{background:#f7f4ea;border-left:3px solid #e8b44a;padding:7px 9px;margin:0 0 6px;border-radius:0 3px 3px 0;font-size:12px;line-height:1.65;color:#4a4a42;}
.saiyo-cta__btn-cell{text-align:center;}
.saiyo-cta__btn{display:inline-block;background:#6baa95;color:#fff !important;padding:11px 14px;text-decoration:none;border-radius:4px;font-size:13px;font-weight:700;transition:opacity .2s;line-height:1.35;}
.saiyo-cta__btn:hover{opacity:.85;color:#fff !important;}
.saiyo-cta__btn small{display:block;font-size:10px;font-weight:400;opacity:.92;margin-top:3px;}
.saiyo-cta__footer{text-align:center;font-size:11px;color:#8a8a82;margin:12px 2px 0;line-height:1.7;}
@media (max-width:600px){
.saiyo-cta__header-row{display:none;}
.saiyo-cta__row{grid-template-columns:1fr;gap:12px;padding:26px 14px 18px;text-align:center;}
.saiyo-cta__name-text{font-size:15px;}
.saiyo-cta__logo--text{width:132px;height:70px;font-size:15px;}
.saiyo-cta__point{padding:0;text-align:left;}
.saiyo-cta__btn{padding:14px 20px;font-size:14.5px;width:100%;max-width:320px;}
}
</style>

<div class="saiyo-cta">
  <div class="saiyo-cta__badge-wrap"><span class="saiyo-cta__badge">相談は無料です</span></div>
  <p class="saiyo-cta__title">ひとりで進めるのが不安な20代の方へ</p>
  <p class="saiyo-cta__lead">書類づくりから面接まで、担当者と一緒に進められるエージェントです。</p>
  <div class="saiyo-cta__panel">
    <div class="saiyo-cta__row saiyo-cta__row--best">
      <div class="saiyo-cta__name">
        <a class="saiyo-cta__name-link" href="https://px.a8.net/svt/ejp?a8mat=4B1ILL+72TKGQ+3Y6M+63H8I" rel="nofollow sponsored">
          <div class="saiyo-cta__logo--text">第二新卒<br>エージェントneo</div>
          <div class="saiyo-cta__name-text">伴走型エージェント</div>
        </a>
      </div>
      <div class="saiyo-cta__count">20代向け<span class="saiyo-cta__count-sub">第二新卒・既卒・フリーター</span><span class="saiyo-cta__target">18歳以下・29歳以上の方、<br>新卒での就職を希望する方は対象外</span></div>
      <div class="saiyo-cta__point">
        <div class="saiyo-cta__hr"><b>人事コメント：</b>落ちた回数より、<b>原因をどう直したかを話せるか</b>が見られます。振り返りを一緒にしてくれる相手がいると、次の応募が変わります。</div>
        <div class="saiyo-cta__point-title">【担当者と一緒に進める】</div>
        ✓ 書類の添削・作成まで一緒に進めてくれる<br>
        ✓ WEB面談ならスマホで自宅から相談できる<br>
        ✓ 東京・大阪・福岡の拠点とWEB面談で全国に対応
      </div>
      <div class="saiyo-cta__btn-cell">
        <a class="saiyo-cta__btn" href="https://px.a8.net/svt/ejp?a8mat=4B1ILL+72TKGQ+3Y6M+63H8I" rel="nofollow sponsored">無料で相談する ›<small>登録後、そのまま面談日を選べます</small></a>
        <img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4B1ILL+72TKGQ+3Y6M+63H8I" alt="">
      </div>
    </div>
  </div>
  <p class="saiyo-cta__footer">スマートフォンでご覧の方は、そのままこの端末で登録を完了してください（別の端末やブラウザに移ると正しく処理されない場合があります）。<br>対象条件は公式サイトの表記に基づきます。</p>
</div>
<!-- /wp:html -->
```

neo は2種類の素材のうち「【公式】第二新卒エージェントneo」（63H8I・www15）を使った。もう一方（63OYA）は「大学中退、中卒、高卒の就職なら」という文言の素材で、1790 の読者（ITパスポート・基本情報の受験者）とは訴求がずれるため。リンクの文字はボタンの文言に変えている。

neo のPR文の数字（書類通過率94.7%、★4.4、平均年収113万円UP など）は時点の記載がないので使っていない。「大手で断られた」という切り口は、JACの禁止事項（「◯◯に断られた」）と同じ種類なので使っていない。

### 4-5. テキストリンク（979用）

レバテックダイレクト（A8の標準の形。0.gifはリンクの直後）：

```html
<a href="https://px.a8.net/svt/ejp?a8mat=4B1ILL+786GWQ+2JK4+4SNX5E" rel="nofollow sponsored">レバテックダイレクト</a><img border="0" width="1" height="1" src="https://www11.a8.net/0.gif?a8mat=4B1ILL+786GWQ+2JK4+4SNX5E" alt="">
```

JAC（VCで発行したコード。「自由テキスト」の部分を「JACリクルートメント」にした。計測用画像 gifbanner はリンクの中のまま）：

```html
<a href="//ck.jp.ap.valuecommerce.com/servlet/referral?sid=3765202&amp;pid=892724768" rel="nofollow sponsored"><img src="//ad.jp.ap.valuecommerce.com/servlet/gifbanner?sid=3765202&amp;pid=892724768" height="1" width="1" border="0">JACリクルートメント</a>
```

979 での使い方（2か所）：
- H2「課長・部長は何レベル？」の最後のメモの直後：
  `<p>ポジションの等級をエージェント経由で確認したい方は、`＋上のJACのリンク＋`に相談できます。年収600万円以上の方が中心のサービスです。</p>`
- H2「まとめ」の箇条書き：
  `<li>管理・専門職、年収600万円以上の方 → `＋JACのリンク＋`</li>`
  `<li>エンジニア・クリエイターの実務経験がある方 → `＋レバテックダイレクトのリンク（上）＋`</li>`
- 段落ブロックに貼るとWordPressが img を消すことがあるので、**カスタムHTMLブロック**で入れる。

### 4-6. 学習系の差し込み枠

②-2 の資料（案件名・ASP・成果条件・素材）を受け取ってから作る。それまでは、上の「添える一文」だけを段落として入れておき、リンクは入れない（2026-10-12 運営者了承）。

---

## 5. 運営者に判断・作業をお願いすること

1. ~~JACをVCで発行する~~（2026-10-12 発行済み。VC の sid=3765202 が「採用のウラ側」であることを運営者が管理画面で確認済み）
2. ~~neo をA8で発行する~~（2026-10-12 発行済み。サイト002を確認済み）
3. ~~パックJ・N の「人事コメント」~~（J＝A案、N＝C案で運営者了承 2026-10-12）
4. ~~Geekly を今回使わない判断でよいか~~（2026-10-12 運営者了承：使わない）
5. 1489 のIT企画職がレバテックダイレクトの対象になるか、A8の問い合わせ窓口で確認するか。
6. 学習系の案件（②-2）。2026-10-12 運営者了承：届くまでは、学習系の箇所に「添える一文」だけを入れる（リンクは入れない）。一文は、それだけで読んで意味が通る文にしてある。
7. A8で TechGo を「採用のウラ側」で発行済み（2026-10-12 運営者）。**コード（リンクURLと0.gifの行）を受け取り、パックAの差し込み枠に入れる**。あわせて、A8のプログラム詳細（成果条件・否認条件・再訪問期間・PR文）を共有してもらい、パックの文言と照らし合わせる。
8. レバテックキャリア（VC・11,000円）は、レバテックダイレクトと同じ会社で、先に登録したほうしか成果にならない。上位10記事では使わない（892 の評判記事など、レバテックキャリアそのものを扱う記事で使う）。
