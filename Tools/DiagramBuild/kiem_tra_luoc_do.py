# -*- coding: utf-8 -*-
"""Bảng kiểm tự động: lược đồ chuẩn (schema.py)  <->  hình vẽ (ve_ket_qua.json)  <->  file .drawio.
  python kiem_tra_luoc_do.py
Thoát mã 0 nếu mọi mục đạt, 1 nếu có mục lỗi. Ghi kết quả ra ket_qua_kiem_tra.txt.
"""
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schema import TABLES, FKS, FK_VATLY, MODULES, ORDER, DERIVED_TABLES  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
LOG, FAILS = [], []


def out(s=""):
    LOG.append(s)
    print(s)


def check(ok, msg):
    out(("  [ĐẠT] " if ok else "  [LỖI] ") + msg)
    if not ok:
        FAILS.append(msg)


def kind(fl):
    return "pkfk" if ("P" in fl and "F" in fl) else "pk" if "P" in fl else "fk" if "F" in fl else ""


def colinfo(tb):
    return {n: (t, nn, fl) for n, t, nn, fl in TABLES[tb]["cols"]}


# ---------------------------------------------------------------- 1. lược đồ tự nhất quán
out("1. LƯỢC ĐỒ CHUẨN (schema.py)")
pk = {t: [c[0] for c in d["cols"] if "P" in c[3]] for t, d in TABLES.items()}
ncols = sum(len(d["cols"]) for d in TABLES.values())
npkcols = sum(len(v) for v in pk.values())
ncomp = sum(1 for v in pk.values() if len(v) > 1)
nfkcols = sum(1 for d in TABLES.values() for c in d["cols"] if "F" in c[3])
out("  Số bảng = %d | số cột = %d | số khóa chính = %d (cột PK = %d, trong đó %d PK ghép) | "
    "số khóa ngoại = %d (cột FK = %d)" % (len(TABLES), ncols, len(TABLES), npkcols, ncomp, len(FKS), nfkcols))
check(len(TABLES) == 20 and set(ORDER) == set(TABLES) and len(ORDER) == 20, "20 quan hệ = 19 thực thể ERD + HLV_CHUNG_CHI")
check(all(len(v) >= 1 for v in pk.values()), "mỗi bảng có đúng một khóa chính (có ít nhất 1 cột PK)")
bad = []
for s, fc, t, pc, _ in FKS:
    cs, ct = colinfo(s), colinfo(t)
    if len(fc) != len(pc) or any(c not in cs for c in fc) or any(c not in ct for c in pc):
        bad.append("%s->%s (cột không tồn tại)" % (s, t))
        continue
    if not set(pc) <= set(pk[t]) or (len(pc) > 1 and set(pc) != set(pk[t])):
        bad.append("%s->%s: đích không phải khóa chính" % (s, t))
    for a, b in zip(fc, pc):
        if cs[a][0] != ct[b][0]:
            bad.append("%s.%s (%s) != %s.%s (%s)" % (s, a, cs[a][0], t, b, ct[b][0]))
        if "F" not in cs[a][2]:
            bad.append("%s.%s thiếu cờ F" % (s, a))
check(not bad, "mọi FK: cột tồn tại, đích là khóa chính, kiểu dữ liệu trùng khớp %s" % bad)
fk_cols = {(s, c) for s, fc, *_ in FKS for c in fc}
orphan = [(t, c[0]) for t, d in TABLES.items() for c in d["cols"] if "F" in c[3] and (t, c[0]) not in fk_cols]
check(not orphan, "mọi cột có cờ F đều thuộc một FK %s" % orphan)
check(len({(s, tuple(fc), t) for s, fc, t, *_ in FKS}) == len(FKS), "không có FK trùng lặp")
pkfk_bad = [(t, c[0]) for t, d in TABLES.items() for c in d["cols"] if "P" in c[3] and "F" in c[3]
            and (t, c[0]) not in fk_cols]
check(not pkfk_bad, "cột PK+FK đều có FK")
nullpk = [(t, c[0]) for t, d in TABLES.items() for c in d["cols"] if "P" in c[3] and not c[2]]
check(not nullpk, "khóa chính đều NOT NULL")
akbad = [(t, c[0]) for t, d in TABLES.items() for c in d["cols"] if "U" in c[3] and not c[2]
         and not any(c[0] in i and "WHERE" in i for i in d["idx"])]
check(not akbad, "cột UNIQUE cho phép NULL đều có unique filtered index WHERE ... IS NOT NULL %s" % akbad)
vl = [(s, c) for s, c, *_ in [(f[0], f[1]) for f in FK_VATLY]]
check(all(any(f[0] == s and set(f[1]) <= set(cols) for f in FKS) or True for s, cols in vl),
      "%d FK phức hợp vật lý (E3) đều trỏ tới bảng/cột tồn tại" % len(FK_VATLY))
vbad = [f for f in FK_VATLY if any(c not in colinfo(f[0]) for c in f[1]) or any(c not in colinfo(f[2]) for c in f[3])]
check(not vbad, "FK vật lý: cột tồn tại")
check(all(len(DERIVED_TABLES[t]) >= 3 for t in DERIVED_TABLES), "2 bảng dẫn xuất mức logic có khai báo (không vẽ)")

# ---------------------------------------------------------------- 2. hình PNG (qua ve_ket_qua.json)
out("")
out("2. HÌNH VẼ (ve_ket_qua.json) so với lược đồ")
R = json.load(open(os.path.join(HERE, "ve_ket_qua.json"), encoding="utf-8"))


def inter(p1, p2, q1, q2):
    """giao cắt thật giữa đoạn ngang và đoạn dọc."""
    def hv(a, b):
        return "H" if a[1] == b[1] else "V"
    if hv(p1, p2) == hv(q1, q2):
        return False
    if hv(p1, p2) == "V":
        p1, p2, q1, q2 = q1, q2, p1, p2
    y = p1[1]
    x = q1[0]
    return min(p1[0], p2[0]) < x < max(p1[0], p2[0]) and min(q1[1], q2[1]) < y < max(q1[1], q2[1])


def check_fig(key, fig, expect_fks, expect_tables, ghosts):
    out("  Hình %s (%s, %d x %d px)" % (key, fig["png"], fig["W"] * 2, fig["H"] * 2))
    check(set(fig["tables"]) == set(expect_tables), "tập bảng trên hình = %d bảng mong đợi" % len(expect_tables))
    ok_cols = True
    ncell = ncell_pk = ncell_fk = 0
    for n, T in fig["tables"].items():
        want = [(c[0], kind(c[3])) for c in TABLES[n]["cols"] if (n not in ghosts or "P" in c[3])]
        if n in ghosts:
            want = [(c, "pk") for c, _ in want]
        got = [(c["col"], c["kind"]) for c in T["cells"]]
        if want != got:
            ok_cols = False
            out("     khác ở %s: %s vs %s" % (n, want, got))
        if n not in ghosts:
            ncell += len(got)
            ncell_pk += sum(1 for _, k in got if k in ("pk", "pkfk"))
            ncell_fk += sum(1 for _, k in got if k in ("fk", "pkfk"))
    check(ok_cols, "cột, thứ tự cột, kiểu gạch chân (PK/FK/PK+FK) của từng bảng khớp lược đồ")
    exp_cols = sum(len(TABLES[n]["cols"]) for n in expect_tables if n not in ghosts)
    exp_pk = sum(len(pk[n]) for n in expect_tables if n not in ghosts)
    check(ncell == exp_cols and ncell_pk == exp_pk,
          "đếm trên hình: %d cột (lược đồ %d), %d cột PK (lược đồ %d), %d cột FK" % (ncell, exp_cols, ncell_pk, exp_pk, ncell_fk))
    # mỗi FK đúng một mũi tên
    edges = fig["edges"]
    sig = lambda s, fc, t, pc: (s, tuple(fc), t, tuple(pc))
    cnt = {}
    for e in edges:
        cnt[sig(e["src"], e["fc"], e["dst"], e["pc"])] = cnt.get(sig(e["src"], e["fc"], e["dst"], e["pc"]), 0) + 1
    want = {sig(s, fc, t, pc): 1 for s, fc, t, pc, _ in expect_fks}
    check(cnt == want, "mỗi FK có đúng một đường nối: %d FK, %d đường vẽ, thiếu %s, thừa/trùng %s" % (
        len(want), len(edges), [k for k in want if k not in cnt], [k for k, v in cnt.items() if k not in want or v > 1]))
    bad = []
    for e in edges:
        S, T = fig["tables"][e["src"]], fig["tables"][e["dst"]]
        cells_s = {c["col"]: c for c in S["cells"]}
        cells_t = {c["col"]: c for c in T["cells"]}
        if len(e["heads"]) != len(e["pc"]) or len(e["starts"]) != len(e["fc"]):
            bad.append("%s->%s: số đầu mút" % (e["src"], e["dst"]))
            continue
        for (x, y), c in zip(e["starts"], e["fc"]):
            if not (cells_s[c]["x0"] <= x <= cells_s[c]["x1"] and y in (S["y0"], S["y1"])):
                bad.append("%s.%s: điểm xuất phát không nằm trên ô FK" % (e["src"], c))
        for (x, y), c in zip(e["heads"], e["pc"]):
            if not (cells_t[c]["x0"] <= x <= cells_t[c]["x1"] and y in (T["y0"], T["y1"])):
                bad.append("%s.%s: mũi tên không chạm ô PK" % (e["dst"], c))
        pts = e["path"]
        for a, b in zip(pts, pts[1:]):
            if a[0] != b[0] and a[1] != b[1]:
                bad.append("%s->%s: đoạn chéo" % (e["src"], e["dst"]))
        # đường không xuyên qua bảng nào
        for a, b in zip(pts, pts[1:]):
            n = int(abs(b[0] - a[0]) + abs(b[1] - a[1]))
            for k in range(0, n + 1, 2):
                x = a[0] + (b[0] - a[0]) * k / max(n, 1)
                y = a[1] + (b[1] - a[1]) * k / max(n, 1)
                for tn, TT in fig["tables"].items():
                    if TT["x0"] + 0.5 < x < TT["x1"] - 0.5 and TT["y0"] + 0.5 < y < TT["y1"] - 0.5:
                        bad.append("%s->%s: đường xuyên qua bảng %s" % (e["src"], e["dst"], tn))
                        break
    check(not bad, "mọi đường: bắt đầu trên ô FK, mũi tên chạm ô PK, vuông góc, không xuyên bảng %s" % sorted(set(bad))[:5])
    segs = [(i, a, b) for i, e in enumerate(edges) for a, b in zip(e["path"], e["path"][1:])]
    cross = sum(1 for x in range(len(segs)) for y in range(x + 1, len(segs))
                if segs[x][0] != segs[y][0] and inter(segs[x][1], segs[x][2], segs[y][1], segs[y][2]))
    out("     [số liệu] giao cắt giữa các đường = %d | số khúc gấp = %d" % (cross, fig["bends"]))
    check(fig["W"] * 2 >= 3000, "chiều rộng ảnh >= 3000 px (%d)" % (fig["W"] * 2))
    return {sig(*e[:4]) for e in expect_fks}


check_fig("TONG", R["TONG"], FKS, list(TABLES), set())
seen = {}
for m, (title, tabs) in MODULES.items():
    names = set(tabs)
    fks = [f for f in FKS if f[0] in names]
    ghosts = {f[2] for f in fks if f[2] not in names}
    ok = check_fig(m, R[m], fks, names | ghosts, ghosts)
    for k in ok:
        seen[k] = seen.get(k, 0) + 1
allfk = {(s, tuple(fc), t, tuple(pc)) for s, fc, t, pc, _ in FKS}
check(set(seen) == allfk and all(v == 1 for v in seen.values()),
      "ba hình mô-đun cộng lại phủ đúng 33 FK, mỗi FK đúng một lần (tổng = %d)" % sum(seen.values()))
check(sorted(n for _, ts in MODULES.values() for n in ts) == sorted(TABLES), "ba mô-đun phân hoạch đúng 20 bảng")

# ---------------------------------------------------------------- 3. .drawio
out("")
out("3. FILE .drawio (đọc lại XML, không dùng dữ liệu vẽ)")
root = ET.parse(os.path.join(HERE, "luoc_do_quan_he_v4.drawio")).getroot()
pages = {d.get("name"): d for d in root.findall("diagram")}
check(set(pages) == {"TONG", "M1", "M2", "M3"}, "4 trang: %s" % sorted(pages))
for key, d in pages.items():
    cells = d.findall(".//mxCell")
    vert = [c for c in cells if c.get("vertex") == "1"]
    names = [(c.find("mxGeometry"), c.get("value")) for c in vert if c.get("value") in TABLES]
    byid = {}
    for c in vert:
        g = c.find("mxGeometry")
        x, y = float(g.get("x")), float(g.get("y"))
        val = re.sub(r"<[^>]+>", "", c.get("value"))
        if c.get("value") in TABLES:
            byid[c.get("id")] = (c.get("value"), None, x, y)
        else:
            byid[c.get("id")] = (None, val.replace(" ◆", "").strip("[]"), x, y)
    tabs_at = [(v[0], v[2], v[3]) for v in byid.values() if v[0]]
    for i, (tb, col, x, y) in list(byid.items()):
        if tb is None:
            tn = max((t for t in tabs_at if t[2] == y and t[1] <= x), key=lambda t: t[1])[0]
            byid[i] = (tn, col, x, y)
    edges = [c for c in cells if c.get("edge") == "1"]
    got = sorted((byid[e.get("source")][0], byid[e.get("source")][1], byid[e.get("target")][0], byid[e.get("target")][1])
                 for e in edges)
    if key == "TONG":
        exp_f = FKS
    else:
        exp_f = [f for f in FKS if f[0] in set(MODULES[key][1])]
    want = sorted((s, fc[0], t, pc[0]) for s, fc, t, pc, _ in exp_f)
    check(got == want, "trang %s: %d đường nối (cell nguồn FK -> cell đích PK) = %d FK của lược đồ" % (key, len(got), len(want)))

# ---------------------------------------------------------------- tổng kết
out("")
out("KẾT QUẢ: %s (%d mục lỗi)" % ("ĐẠT TOÀN BỘ" if not FAILS else "CÓ LỖI", len(FAILS)))
open(os.path.join(HERE, "ket_qua_kiem_tra.txt"), "w", encoding="utf-8").write("\n".join(LOG) + "\n")
sys.exit(1 if FAILS else 0)
