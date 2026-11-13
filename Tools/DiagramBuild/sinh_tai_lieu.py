# -*- coding: utf-8 -*-
"""Sinh các khối tự động của LUOC_DO_CHUAN.md từ schema.py (giữ tài liệu và hình luôn khớp).
  python sinh_tai_lieu.py
Thay nội dung giữa <!--BEGIN:X--> ... <!--END:X--> với X in SCHEMA, FKTABLE, DERIVED, STATS, CHECKLOG.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schema import TABLES, FKS, FK_VATLY, ORDER, DERIVED_TABLES, GROUPS  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(HERE, "LUOC_DO_CHUAN.md")


def col_md(name, typ, nn, fl):
    s = name
    if "D" in fl:
        s = "[%s]" % s
    if "P" in fl and "F" in fl:
        s = "<u><i>%s</i></u>" % s
    elif "P" in fl:
        s = "<u>%s</u>" % s
    elif "F" in fl:
        s = "<i>%s</i>" % s
    return "%s %s %s" % (s, typ, "NOT NULL" if nn else "NULL")


def schema_block():
    L = []
    cur = None
    for t in ORDER:
        d = TABLES[t]
        if d["grp"] != cur:
            cur = d["grp"]
            L.append("")
            L.append("**Phân hệ: %s**" % GROUPS[cur])
            L.append("")
        cols = ", ".join(col_md(*c) for c in d["cols"])
        L.append("- **%s**(%s)" % (t, cols))
        fks = [f for f in FKS if f[0] == t]
        if d["ak"]:
            L.append("  - Khóa thay thế: %s" % "; ".join(d["ak"]))
        for s, fc, dst, pc, rel in fks:
            L.append("  - FK: %s -> %s.%s &nbsp;*(%s)*" % (
                "(%s)" % ", ".join("%s.%s" % (s, c) for c in fc) if len(fc) > 1 else "%s.%s" % (s, fc[0]),
                dst, "(%s)" % ", ".join(pc) if len(pc) > 1 else pc[0], rel))
        for c in d["checks"]:
            L.append("  - CHECK `%s`" % c.replace("|", "\\|"))
        for i in d["idx"]:
            L.append("  - Chỉ mục/UNIQUE `%s`" % i.replace("|", "\\|"))
        for n in d["notes"]:
            L.append("  - Ghi chú: %s" % n)
    return "\n".join(L)


CARD = {
    ("HUAN_LUYEN_VIEN", "MaHLV"): "1 – (0..1): chuyên biệt hóa, FK là PK",
    ("DANH_GIA_PT", "MaLichHen"): "1 – (0..1): FK + UNIQUE",
    ("HLV_CHUNG_CHI", "MaHLV"): "1 – N: đa trị",
    ("CHI_TIET_HOA_DON", "MaHD"): "1 – N: thực thể yếu, FK nằm trong PK",
    ("DIEM_LOYALTY", "MaHV"): "1 – N: thực thể yếu, FK nằm trong PK",
}


def fk_table():
    L = ["| # | Khóa ngoại (bảng.cột) | Tham chiếu | Quan hệ trên ERD | NULL? | Bản số / ghi chú |",
         "|--:|---|---|---|---|---|"]
    for i, (s, fc, t, pc, rel) in enumerate(FKS, 1):
        cols = {c[0]: c for c in TABLES[s]["cols"]}
        nul = "NULL" if all(not cols[c][2] for c in fc) else "NOT NULL"
        note = CARD.get((s, fc[0]), "N – 1")
        if nul == "NULL":
            note = "N – (0..1): phía FK tùy chọn"
        L.append("| %d | %s.%s | %s.%s | %s | %s | %s |" % (
            i, s, "(%s)" % ", ".join(fc) if len(fc) > 1 else fc[0], t,
            "(%s)" % ", ".join(pc) if len(pc) > 1 else pc[0], rel, nul, note))
    L.append("")
    L.append("**FK phức hợp thực thi ở mức vật lý (E3)** – mỗi dòng thay cho FK đơn cùng quan hệ ở bảng trên, "
             "nên không thêm mũi tên nào trên hình:")
    L.append("")
    L.append("| Bảng | FK phức hợp | Tham chiếu (cần UNIQUE ở bảng đích) | Mục đích |")
    L.append("|---|---|---|---|")
    for s, fc, t, pc, why in FK_VATLY:
        L.append("| %s | (%s) | %s(%s) | %s |" % (s, ", ".join(fc), t, ", ".join(pc), why))
    return "\n".join(L)


def derived_block():
    L = []
    for t, cols in DERIVED_TABLES.items():
        L.append("- **%s**(%s)  — FK: %s.MaCN -> CHI_NHANH.MaCN" % (t, ", ".join(col_md(*c) for c in cols), t))
    return "\n".join(L)


def stats_block():
    ncols = sum(len(d["cols"]) for d in TABLES.values())
    pkc = sum(1 for d in TABLES.values() for c in d["cols"] if "P" in c[3])
    comp = [t for t in ORDER if sum(1 for c in TABLES[t]["cols"] if "P" in c[3]) > 1]
    fkc = sum(1 for d in TABLES.values() for c in d["cols"] if "F" in c[3])
    nullable = sum(1 for d in TABLES.values() for c in d["cols"] if not c[2])
    ck = sum(len(d["checks"]) for d in TABLES.values())
    ix = sum(1 for d in TABLES.values() for i in d["idx"] if "UNIQUE" in i)
    ixf = sum(1 for d in TABLES.values() for i in d["idx"] if "UNIQUE" in i and "WHERE" in i)
    return "\n".join([
        "| Chỉ số | Giá trị |", "|---|--:|",
        "| Quan hệ (bảng) | %d |" % len(TABLES),
        "| Cột | %d |" % ncols,
        "| Khóa chính | %d (cột PK: %d; PK ghép: %d – %s) |" % (len(TABLES), pkc, len(comp), ", ".join(comp)),
        "| Khóa ngoại (= số mũi tên trên hình tổng) | %d (cột FK: %d; FK ghép: 1 – DANG_KY_GOI) |" % (len(FKS), fkc),
        "| Cột cho phép NULL | %d |" % nullable,
        "| Ràng buộc CHECK | %d |" % ck,
        "| UNIQUE / unique filtered index khai báo | %d (trong đó filtered: %d) |" % (ix, ixf),
    ])


def checklog_block():
    p = os.path.join(HERE, "ket_qua_kiem_tra.txt")
    body = open(p, encoding="utf-8").read().rstrip() if os.path.exists(p) else "(chưa chạy kiem_tra_luoc_do.py)"
    return "```text\n" + body + "\n```"


def main():
    s = open(MD, encoding="utf-8").read()
    for name, fn in (("SCHEMA", schema_block), ("FKTABLE", fk_table), ("DERIVED", derived_block),
                     ("STATS", stats_block), ("CHECKLOG", checklog_block)):
        pat = re.compile(r"(<!--BEGIN:%s-->)(.*?)(<!--END:%s-->)" % (name, name), re.S)
        if not pat.search(s):
            print("thiếu marker", name)
            continue
        s = pat.sub(lambda m: m.group(1) + "\n" + fn() + "\n" + m.group(3), s)
    open(MD, "w", encoding="utf-8").write(s)
    print("đã cập nhật", MD)


if __name__ == "__main__":
    main()
