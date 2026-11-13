"""Tính số trang của từng tiêu đề từ PDF (Word xuất) -> JSON {tiêu đề: trang}."""
import sys, json, re, fitz
hs = json.load(open(sys.argv[1], encoding="utf-8"))
doc = fitz.open(sys.argv[2])
norm = lambda s: re.sub(r"\s+", " ", s.replace("\u200b", "")).strip()
pages = [norm(p.get_text()) for p in doc]
res = {}
start = 2  # bỏ bìa (trang 1) và trang mục lục (trang 2) -> chỉ tìm từ trang 3
for lv, t in hs:
    key = norm(t)[:38]
    found = None
    for i in range(start, len(pages)):
        if key in pages[i]:
            found = i + 1
            break
    res[t] = found
    if found: start = max(start, found - 1)
missing = [t for t, v in res.items() if not v]
print("missing:", missing)
json.dump(res, open(sys.argv[3], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
