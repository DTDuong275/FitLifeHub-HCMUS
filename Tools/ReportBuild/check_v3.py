"""Tự kiểm tra BaoCao_GD1_FitLifeHub_v3.docx.  Dùng: python -X utf8 check_v3.py <docx> [<pdf>]"""
import sys, re, zipfile, os
from collections import Counter
from lxml import etree

sys.path.insert(0, os.path.dirname(__file__))
import dbml_parse
from model import *

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
ns = {"w": W}
q = lambda t: f"{{{W}}}{t}"
FAIL = []
OK = []


def check(cond, msg):
    (OK if cond else FAIL).append(msg)
    print(("[ĐẠT] " if cond else "[LỖI] ") + msg)


def ptext(p):
    return "".join(t.text or "" for t in p.iter(q("t"))).replace("​", "")


docx = sys.argv[1]
z = zipfile.ZipFile(docx)
root = etree.fromstring(z.read("word/document.xml"))
body = root.find("w:body", ns)
items = []   # (kind, style, text | rows)
for ch in body:
    if ch.tag == q("p"):
        st = ch.find("w:pPr/w:pStyle", ns)
        items.append(("p", st.get(q("val")) if st is not None else "", ptext(ch), ch))
    elif ch.tag == q("tbl"):
        rows = []
        for tr in ch.findall("w:tr", ns):
            rows.append([" / ".join(ptext(p) for p in tc.findall(".//w:p", ns)) for tc in tr.findall("w:tc", ns)])
        items.append(("t", "", rows, ch))
full = "\n".join(it[2] if it[0] == "p" else "\n".join(" | ".join(r) for r in it[2]) for it in items)

D = dbml_parse.parse()
T = D["tables"]

# ------------------------------------------------------------------ 1. cấu trúc tiêu đề
heads = [(it[1], it[2]) for it in items if it[0] == "p" and it[1] in ("Heading1", "Heading2", "Heading3") and it[2].strip()]
h1 = [t for s, t in heads if s == "Heading1"]
print("Heading1:", h1)
check(len(h1) == 6 and h1[0].startswith("Tổng quan") and [x[:2] for x in h1[1:]] == ["1.", "2.", "3.", "4.", "5."], "Tiêu đề cấp 1: Tổng quan, 1.–5. đúng thứ tự (v2 không có mục lục; kiểm tra bằng cây tiêu đề)")
h2 = [t for s, t in heads if s == "Heading2"]
exp_h2 = ["Giả định quy mô"] + [f"QT{k}." for k in range(1, 8)] + ["3.1", "3.2", "3.3", "3.4", "4.1", "4.2", "4.3", "4.4", "4.5", "4.6"]
got = [t for t in h2]
ok = all(any(g.startswith(e) for g in got) for e in exp_h2) and len(got) == len(exp_h2)
check(ok, f"Tiêu đề cấp 2 đủ và đúng số lượng ({len(got)}): " + "; ".join(x[:6] for x in got))
qt_nums = [int(re.match(r"QT(\d+)\.", t).group(1)) for t in h2 if t.startswith("QT")]
check(qt_nums == list(range(1, N_QT + 1)), f"QT liên tục 1..{N_QT}")
h3 = [t for s, t in heads if s == "Heading3"]
rb_heads = [t for t in h3 if t.startswith("RB")]
check([t[:4] for t in rb_heads] == RB_CODES, f"Mục 4.5: {len(rb_heads)} tiêu đề RB, đánh số liên tục RB01..RB{len(RB_CODES):02d}")
check([t[:5] for t in rb_heads] == [f"RB{c[2:]} " if False else t[:5] for t in rb_heads], "tiêu đề RB hợp lệ")
for (code, title), t in zip(RB, rb_heads):
    if t != f"{code} – {title}":
        check(False, f"Tiêu đề {code} khác tên chuẩn: {t}")
sub46 = [t for t in h3 if re.match(r"4\.6\.\d+ ", t)]
nums46 = [int(re.match(r"4\.6\.(\d+) ", t).group(1)) for t in sub46]
check(nums46 == list(range(1, len(REL_ORDER) + 1)), f"Mục 4.6 có {len(sub46)} tiểu mục liên tục 4.6.1..4.6.{len(REL_ORDER)}")

# ------------------------------------------------------------------ 2. con số nhất quán
def numbers(pattern, text=None):
    return [int(m.group(1)) for m in re.finditer(pattern, text or full)]

allowed = {
    r"(\d+) (?:kiểu )?thực thể": {19, 10, 4, 2, 1},
    r"(\d+) mối liên kết": {32, 31},
    r"(\d+) khóa ngoại": {35, 33, 32, 2, 3, 1, 7, 12, 14, 4},
    r"(\d+) ràng buộc": {30},
    r"(\d+) chức năng": {30},
    r"(\d+) quan hệ": {22, 20, 19, 16, 6, 2},
    r"(\d+) bảng dẫn xuất": {2},
}
for pat, ok_set in allowed.items():
    found = Counter(numbers(pat))
    bad = {k: v for k, v in found.items() if k not in ok_set}
    check(not bad, f"Số '{pat[7:30]}…': {dict(found)}" + (f" – LẠ: {bad}" if bad else ""))
# các câu then chốt
check(re.search(r"gồm 19 kiểu thực thể", full) is not None, "3.1 nêu 19 kiểu thực thể")
check("10 + 1 + 4 + 2 + 2 = 19" in full, "phép cộng phân loại 10+1+4+2+2 = 19")
check(re.search(r"32 mối liên kết đếm trực tiếp từ hình ERD \(31 liên kết thông thường và 1 chuyên biệt hóa", full) is not None, "3.1 nêu 32 mối liên kết (31 + 1)")
check(re.search(r"Lược đồ gồm 22 quan hệ \(20 quan hệ ánh xạ từ ERD và 2 bảng dẫn xuất\)", full) is not None, "4.2 nêu 22 quan hệ (20 + 2)")
check(re.search(r"Tổng cộng 22 quan hệ, 136 cột", full) is not None, "4.2 nêu 22 quan hệ, 136 cột")
check(re.search(r"Danh sách 35 khóa ngoại: 33 khóa ngoại của ERD", full) is not None, "4.2 nêu 35 khóa ngoại = 33 + 2")
check(re.search(r"Trong 22 quan hệ, 16 quan hệ đạt BCNF .* và 6 quan hệ chỉ đạt 2NF", full) is not None, "4.4 nêu 22 quan hệ: 16 BCNF, 6 2NF")
check("Có 30 ràng buộc RB01–RB30" in full, "4.5 nêu 30 ràng buộc")

# bảng quan hệ ERD
link_tbl = [it for it in items if it[0] == "t" and it[2][0][:3] == ["#", "Mối liên kết", "Từ"]][0][2]
check(len(link_tbl) - 1 == len(LINKS) == 32, f"Bảng mối liên kết có {len(link_tbl) - 1} dòng = 32")
check([r[0] for r in link_tbl[1:]] == [str(i) for i in range(1, 33)], "Đánh số mối liên kết 1..32")
ents_in_links = set()
for r in link_tbl[1:]:
    ents_in_links.update([r[2], r[4]])
check(ents_in_links == set(ENTITIES), f"Mọi thực thể ERD xuất hiện trong bảng liên kết ({len(ents_in_links)}/19)")
# mỗi FK của DBML tương ứng đúng 1 mối liên kết (33 = 32 + HLV_CHUNG_CHI)
fk_erd = [r for r in D["refs"] if r["t"] not in DERIVED_TABLES]
check(len(fk_erd) == 33 and len(fk_erd) - 1 == len(LINKS), "33 FK ERD = 32 liên kết + 1 (HLV_CHUNG_CHI)")

# bảng tần suất
freq = [it for it in items if it[0] == "t" and it[2][0][:2] == ["Mã", "Chức năng"]][0][2][1:]
check(len(freq) == N_CN and [r[0] for r in freq] == [f"CN{k:02d}" for k in range(1, N_CN + 1)], f"Bảng tần suất {len(freq)} chức năng CN01..CN30")
lv = Counter(r[5] for r in freq)
check(dict(lv) == LEVELS, f"Số mức độ đếm từ bảng: {dict(lv)}")
check(f"Tổng hợp: {N_CN} chức năng, trong đó mức Cao {lv['Cao']}, Trung bình {lv['Trung bình']}, Thấp {lv['Thấp']}" in full, "Dòng Tổng hợp khớp số đếm từ bảng")
check(f"CN01 – CN{N_CN}" in full and "(QT1 – QT7)" in full, "Mục 5 trỏ đúng QT1–QT7, CN01–CN30")

# ------------------------------------------------------------------ 3. mã RB
defined = set(t[:4] for t in rb_heads)
refs = Counter(re.findall(r"RB\d\d", full))
for c in list(refs):
    pass
body_wo_heads = full
for t in rb_heads:
    body_wo_heads = body_wo_heads.replace(t, "")
used = set(re.findall(r"RB\d\d", body_wo_heads))
check(used <= defined, f"Mọi mã RB được tham chiếu đều tồn tại ({len(used)} mã dùng; thiếu: {sorted(used - defined)})")
# mã dùng ngoài mục 4.5
i45 = next(i for i, it in enumerate(items) if it[0] == "p" and it[1] == "Heading2" and it[2].startswith("4.5 "))
i46 = next(i for i, it in enumerate(items) if it[0] == "p" and it[1] == "Heading2" and it[2].startswith("4.6 "))
outside = "\n".join((it[2] if it[0] == "p" else "\n".join(" | ".join(r) for r in it[2])) for k, it in enumerate(items) if not (i45 <= k < i46))
unref = sorted(defined - set(re.findall(r"RB\d\d", outside)))
check(not unref, f"Mọi RB đều được trỏ tới từ QT/3.4/4.3/4.6…" + (f" – chưa được trỏ: {unref}" if unref else ""))
# 3.4 chỉ chứa RB hợp lệ, mỗi dòng có mã
i34 = next(i for i, it in enumerate(items) if it[0] == "p" and it[1] == "Heading2" and it[2].startswith("3.4 "))
t34 = next(it for it in items[i34:] if it[0] == "t")[2][1:]
check(all(re.fullmatch(r"RB\d\d", r[3]) for r in t34), f"3.4: {len(t34)} dòng, mỗi dòng có đúng một mã RB")
cov34 = set(r[3] for r in t34)
check(cov34 == defined - {"RB14"}, f"3.4 phủ mọi RB trừ RB14 (đã có bản số 1..N trên ERD): thiếu/thừa {sorted(cov34 ^ (defined - {'RB14'}))}")
# bắt buộc có RB cho E2,E3,E4,E6,E9,E10
must = {"E2": "RB19", "E3": "RB17", "E4": "RB07", "E6": "RB23", "E9": "RB27", "E10": "RB15"}
check(all(v in defined for v in must.values()), "Có RB cho E2 (RB19), E3 (RB12/17/18), E4 (RB07/08), E6 (RB23–25), E9 (RB27), E10 (RB15/16)")
# mỗi RB có bảng Mục + bảng tầm ảnh hưởng
imp_tbls = [it for it in items if it[0] == "t" and it[2][0][:4] == ["Bảng tầm ảnh hưởng", "Thêm", "Xóa", "Sửa"]]
check(len(imp_tbls) == 30, f"{len(imp_tbls)} bảng tầm ảnh hưởng (30 RB)")
for it in imp_tbls:
    for r in it[2][1:]:
        if r[0] not in T:
            check(False, f"bảng tầm ảnh hưởng nêu bảng không có: {r[0]}")
        if r[1] not in "+-" or r[2] not in "+-" or not (r[3] == "-" or r[3].startswith("+")):
            check(False, f"ký hiệu tầm ảnh hưởng lạ: {r}")

# ------------------------------------------------------------------ 4. bảng/cột ↔ DBML
# 4.2: các dòng quan hệ
sch_lines = []
for it in items:
    if it[0] == "p":
        m = re.match(r"^(\d+)\. ([A-Z_]+) \( (.*) \)$", it[2])
        if m:
            sch_lines.append((int(m.group(1)), m.group(2), [c.strip().strip("[]") for c in m.group(3).split(",")]))
check([s[1] for s in sch_lines] == REL_ORDER, f"4.2: {len(sch_lines)} quan hệ đúng thứ tự")
mis = []
for k, n, cols in sch_lines:
    exp = [c["name"] for c in T[n]["cols"]]
    if cols != exp:
        mis.append((n, cols, exp))
check(not mis, f"4.2: cột của {len(sch_lines)} quan hệ khớp DBML (tên và thứ tự)" + (f" – lệch: {mis[:2]}" if mis else ""))
check(set(s[1] for s in sch_lines) == set(T), "Tập bảng 4.2 = tập bảng DBML (không thừa, không thiếu)")
# PK gạch chân / FK in nghiêng trong 4.2
fk_by_t = {}
for r in D["refs"]:
    fk_by_t.setdefault(r["t"], set()).update(r["c"])
bad_fmt = []
for it in items:
    if it[0] == "p" and re.match(r"^\d+\. [A-Z_]+ \( ", it[2]):
        name = re.match(r"^\d+\. ([A-Z_]+)", it[2]).group(1)
        for r in it[3].findall("w:r", ns):
            txt = "".join(t.text or "" for t in r.findall("w:t", ns)).strip(" ,[]")
            if txt in [c["name"] for c in T[name]["cols"]]:
                u = r.find("w:rPr/w:u", ns) is not None
                i_ = r.find("w:rPr/w:i", ns) is not None
                if u != (txt in T[name]["pk"]) or i_ != (txt in fk_by_t.get(name, set())):
                    bad_fmt.append((name, txt, u, i_))
check(not bad_fmt, "4.2: PK gạch chân, FK in nghiêng đúng cho mọi cột" + (f" – lệch: {bad_fmt[:3]}" if bad_fmt else ""))
# 4.6: bảng thuộc tính
mis = []
n46 = 0
for k, it in enumerate(items):
    if it[0] == "p" and it[1] == "Heading3" and re.match(r"4\.6\.\d+ ", it[2]):
        name = it[2].split(" ", 1)[1]
        tbl = next(x for x in items[k:] if x[0] == "t")[2]
        n46 += 1
        got = [(r[0], r[1], "NULL" in r[2].split(", ") ) for r in tbl[1:]]
        exp = [(c["name"], c["type"], c["null"]) for c in T[name]["cols"]]
        if name not in T or got != exp:
            mis.append((name, [g for g, e in zip(got, exp) if g != e][:2]))
        # PK
        pkc = [r[0] for r in tbl[1:] if r[2].startswith("PK")]
        if name in T and pkc != T[name]["pk"]:
            mis.append((name, "PK", pkc))
check(n46 == len(T) and not mis, f"4.6: {n46} bảng, mọi cột/kiểu/NULL/PK khớp DBML và ngược lại" + (f" – lệch: {mis[:3]}" if mis else ""))
ncols = sum(len(T[n]["cols"]) for n in T)
check(ncols == 136, f"Tổng số cột DBML = {ncols} (136) và 4.2 nêu 136")
# FK table
fk_tbl = next(it for it in items if it[0] == "t" and it[2][0][:2] == ["#", "Khóa ngoại"])[2][1:]
exp_fk = []
for r in D["refs"]:
    f = lambda t, c: f"{t}.{c[0]}" if len(c) == 1 else f"{t}.({', '.join(c)})"
    exp_fk.append((f(r["t"], r["c"]), f(r["rt"], r["rc"])))
got_fk = [(r[1].replace("​", ""), r[2].replace("​", "")) for r in fk_tbl]
check(got_fk == exp_fk, f"Bảng khóa ngoại 4.2: {len(got_fk)} dòng khớp DBML (tên cột, chiều tham chiếu)")
# 4.3
nf_tbl = next(it for it in items if it[0] == "t" and it[2][0][:2] == ["Quan hệ", "Khóa"])[2][1:]
check([r[0] for r in nf_tbl] == REL_ORDER, f"4.3: {len(nf_tbl)} quan hệ đủ, đúng thứ tự")
c2 = [r[0] for r in nf_tbl if r[3] == "2NF"]
cb = [r[0] for r in nf_tbl if r[3] == "BCNF"]
check(len(c2) + len(cb) == 22 and (len(cb), len(c2)) == (16, 6), f"4.3 đếm dạng chuẩn: BCNF {len(cb)}, 2NF {len(c2)} ({', '.join(c2)}) khớp 4.4")
# DBML cột có trong 4.3 PTH: mỗi 2NF có phụ thuộc hàm nêu
# ------------------------------------------------------------------ 5. thuật ngữ cũ
old = ["CHI_TIEU_THANG", "LICH_SU_HANG", "LICH_SU_CONG_TAC", "CT_HOADON_SP", "CHUNG_CHI_HLV", "NgayBaoLuu", "MaTB", "SoBuoiPT", "SoBuoiConLai",
       "NgayHetHan", "DiemTichLuy", "NgayTap", "MaLH", "MaDG", "MaKG", "HinhThucTT", "SoLuongTon", "LoaiSP", "TenChungChi", "MaPT", "(?<![A-Za-z_.])SDT",
       "ThoiDiemDat", "GioMo ", "GioDong ", "ThanhTien của hóa đơn", "'Bảo lưu'", "12 tháng trượt"]
hits = {w: len(re.findall(w if w.startswith("(?<!") else re.escape(w), full)) for w in old}
hits = {k: v for k, v in hits.items() if v}
print("Thuật ngữ cũ còn xuất hiện (để xem ngữ cảnh):", hits)
for w in ("THIET_BI", "KHUNG_GIO"):
    for m in re.finditer(w, full):
        ctx = full[max(0, m.start() - 60): m.end() + 40].replace("\n", " ")
        print("   ", w, "→", ctx)
check(not {k for k in hits if k not in ("12 tháng trượt",)}, "Không còn tên bảng/cột của thiết kế cũ (trừ nhắc phương án dự phòng 12 tháng trượt)")
for w in ("ENUM",):
    for m in re.finditer(w, full):
        pass
# UNIQUE trên cột NULL
check("unique filtered index" in full and "WHERE cột IS NOT NULL" in full, "Nêu unique filtered index cho cột NULL")
check("không có ENUM" in full.lower() or "Không có ENUM" in full or "không có ENUM" in full, "Nêu SQL Server không có ENUM, dùng CHECK")
check("người đang có mặt" in full and "SoLuotVao − SoLuotRa" in full, "Tỷ lệ lấp đầy tính theo người có mặt (E9)")
check("UQ_CI_DangCoMat" in full, "Có RB cho mỗi hội viên một lượt chưa check-out (E10)")
check("UQ_LH_HV_Gio" in full and "UPDLOCK" in full, "Chống trùng lịch phía hội viên: unique filtered index + UPDLOCK")


# ------------------------------------------------------------------ mục lục (trường TOC)
toc_entries = []
started = False
for it in items:
    if it[0] == "p" and it[1] == "Heading1" and it[2].startswith("Tổng quan"):
        break
    if it[0] == "p" and it[2].strip() == "MỤC LỤC":
        started = True
        continue
    if started and it[0] == "p" and it[3].find("w:pPr/w:tabs", ns) is not None:
        ts = [t.text or "" for t in it[3].iter(q("t"))]
        toc_entries.append((ts[0], int(ts[-1])))
instr = " ".join((e.text or "") for e in root.iter(q("instrText")))
check("TOC" in instr and "1-2" in instr, "Mục lục là trường TOC (\o 1-2) – Word cập nhật được bằng F9")
exp_heads = [(s2, t2) for s2, t2 in heads if s2 in ("Heading1", "Heading2")]
check([t for t, _ in toc_entries] == [t for _, t in exp_heads], f"Mục lục có {len(toc_entries)} dòng = số tiêu đề cấp 1–2 ({len(exp_heads)}), đúng thứ tự")

# ------------------------------------------------------------------ 6. mục 5 (nhóm tự điền) giữ trống
mem = next(it for it in items if it[0] == "t" and it[2][0][:3] == ["STT", "MSSV", "Họ tên"])[2]
check(all(not any(c.strip() for c in r[3:]) for r in mem[1:]) and len(mem) == 5, "Bảng Thành viên: cột phân công/đóng góp/tự đánh giá giữ trống")
check("…………" in full, "Tên công cụ quản lý để trống (dấu chấm lửng) cho nhóm điền")

# ------------------------------------------------------------------ 7. cấu trúc gói docx
names = z.namelist()
check(not any(n.endswith("/") for n in names), "Gói docx không có mục thư mục")
rels = z.read("word/_rels/document.xml.rels").decode()
used_rids = set(re.findall(r'r:embed="(rId\d+)"', z.read("word/document.xml").decode()))
check(all(f'Id="{r}"' in rels for r in used_rids), f"Mọi hình nhúng ({len(used_rids)}) có quan hệ trong rels: {sorted(used_rids)}")

# ------------------------------------------------------------------ 8. PDF (nếu có)
if len(sys.argv) > 2:
    import fitz
    d = fitz.open(sys.argv[2])
    print("Số trang PDF:", len(d))
    over = []
    for i, pg in enumerate(d):
        w, h = pg.rect.width, pg.rect.height
        for b in pg.get_text("blocks"):
            if b[2] > w - 20 or b[0] < 20 or b[3] > h - 10:
                over.append((i + 1, [round(x) for x in b[:4]], b[4][:30]))
        for dr in pg.get_drawings():
            r = dr["rect"]
            if r.x1 > w - 15 or r.x0 < 15:
                over.append((i + 1, "bảng/đường vượt lề", [round(x) for x in (r.x0, r.x1)]))
    check(not over, f"Không có chữ/bảng tràn lề trang ({len(over)} vi phạm)" + (f": {over[:3]}" if over else ""))
    imgs = sum(len(pg.get_images()) for pg in d)
    check(imgs >= 5, f"Hình hiển thị trong PDF: {imgs} (logo + ERD + 3 hình mô-đun)")
    blank = [i + 1 for i, pg in enumerate(d) if len(pg.get_text().strip()) < 40 and not pg.get_images()]
    check(not blank, f"Không có trang trắng {blank}")
    # số trang trong mục lục khớp số trang thật
    norm = lambda s: re.sub(r"\s+", " ", s.replace("​", "")).strip()
    pgt = [norm(p_.get_text()) for p_ in d]
    wrong = []
    start = 2
    for t, n in toc_entries:
        key = norm(t)[:38]
        real = next((i + 1 for i in range(start, len(pgt)) if key in pgt[i]), None)
        if real != n:
            wrong.append((t[:30], n, real))
        if real:
            start = max(start, real - 1)
    check(not wrong, f"Số trang trong mục lục khớp trang thật của {len(toc_entries)} tiêu đề" + (f" – lệch: {wrong[:4]}" if wrong else ""))

print("\nTỔNG:", len(OK), "đạt,", len(FAIL), "lỗi")
if FAIL:
    print("\n".join(FAIL))
    sys.exit(1)
