"""edits.py の修正を 01_draft.html に適用し、02_revised.html を作る。

修正前の文字列が想定どおりの回数だけ見つからない場合は、何も書き出さずに止まる。
  python3 rewrites/network-specialist-haishi/apply_edits.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from edits import EDITS  # noqa: E402

text = (HERE / "01_draft.html").read_text(encoding="utf-8")
errors = []
for e in EDITS:
    want = e.get("count", 1)
    got = text.count(e["before"])
    if got != want:
        errors.append(f'{e["id"]}: 修正前の文字列が{got}件（想定{want}件）')
        continue
    text = text.replace(e["before"], e["after"])

if errors:
    sys.exit("\n".join(errors))
(HERE / "02_revised.html").write_text(text, encoding="utf-8")
print(f"{len(EDITS)}件を適用しました -> 02_revised.html")
