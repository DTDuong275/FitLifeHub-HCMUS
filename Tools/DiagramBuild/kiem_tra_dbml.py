# -*- coding: utf-8 -*-
"""So sánh file DBML với LƯỢC ĐỒ CHUẨN (schema.py). Không tin vào nhận xét, chỉ đọc cấu trúc do parser DBML trả về.

Chạy:  python kiem_tra_dbml.py [đường_dẫn.dbml]
Cần:   node + @dbml/core (npm install @dbml/core; hoặc đặt biến NODE_PATH tới thư mục node_modules)
"""
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
DBML = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "FitLifeHub.v2.dbml")

spec = importlib.util.spec_from_file_location("schema", os.path.join(HERE, "schema.py"))
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)

# ---- đọc DBML bằng parser chính thức
tmp = os.path.join(tempfile.gettempdir(), "fitlife_dbml.json")
r = subprocess.run(["node", os.path.join(HERE, "dbml_to_json.js"), DBML, tmp], capture_output=True, text=True,
                   encoding="utf-8", shell=(os.name == "nt"))
results = []


def check(name, ok, detail=""):
    results.append((ok, name, detail))
    print(("[ĐẠT] " if ok else "[LỖI] ") + name + (f"  {detail}" if detail else ""))


check("Cú pháp DBML hợp lệ (parser @dbml/core)", r.returncode == 0, (r.stderr or "")[:400])
if r.returncode != 0:
    sys.exit(1)
J = json.load(open(tmp, encoding="utf-8"))
src = open(DBML, encoding="utf-8").read()

tables = {t["name"]: t for t in J["tables"].values()}
fields_by_id = J["fields"]
idx_by_id = J["indexes"]
enums = {e["name"]: [J["enumValues"][str(v)]["name"] for v in e["valueIds"]] for e in J["enums"].values()}


def cols(t):
    return [fields_by_id[str(i)] for i in t["fieldIds"]]


def norm_type(s):
    return re.sub(r"\s+", "", s).lower()


def table_text(t):
    parts = [t.get("note") or ""]
    parts += [f.get("note") or "" for f in cols(t)]
    for i in t["indexIds"]:
        ix = idx_by_id[str(i)]
        parts += [ix.get("name") or "", ix.get("note") or ""]
    return "\n".join(parts)


def index_cols(ix):
    return [J["indexColumns"][str(c)]["value"] for c in ix["columnIds"]]


def pk_cols(t):
    p = [f["name"] for f in cols(t) if f.get("pk")]
    for i in t["indexIds"]:
        ix = idx_by_id[str(i)]
        if ix.get("pk"):
            p += index_cols(ix)
    return p


# ---------------------------------------------------------------- 1. bảng
expected = set(S.TABLES) | set(S.DERIVED_TABLES)
got = set(tables)
check(f"Tập bảng = {len(S.TABLES)} bảng ERD/quan hệ + {len(S.DERIVED_TABLES)} bảng dẫn xuất",
      expected == got, f"thiếu {sorted(expected - got)} thừa {sorted(got - expected)}")

# ---------------------------------------------------------------- 2. cột, kiểu, NULL, PK, thứ tự
bad = []
n_cols = n_pk = 0
all_defs = {n: [(c[0], c[1], c[2], c[3]) for c in d["cols"]] for n, d in S.TABLES.items()}
all_defs.update({n: [tuple(c) for c in c_] for n, c_ in S.DERIVED_TABLES.items()})
for name, defs in all_defs.items():
    if name not in tables:
        continue
    t = tables[name]
    fs = cols(t)
    if [f["name"] for f in fs] != [d[0] for d in defs]:
        bad.append(f"{name}: tên/thứ tự cột {[f['name'] for f in fs]} != {[d[0] for d in defs]}")
        continue
    for f, (cn, ctype, notnull, flag) in zip(fs, defs):
        n_cols += 1
        if norm_type(f["type"]["type_name"]) != norm_type(ctype):
            bad.append(f"{name}.{cn}: kiểu {f['type']['type_name']} != {ctype}")
        if bool(f.get("not_null")) != bool(notnull):
            bad.append(f"{name}.{cn}: NOT NULL {bool(f.get('not_null'))} != {bool(notnull)}")
        if f.get("enumId"):
            bad.append(f"{name}.{cn}: dùng Enum làm kiểu cột (phải là {ctype} + CHECK)")
        if f.get("default") is not None and f["default"] != {}:
            bad.append(f"{name}.{cn}: có default, lược đồ chuẩn không có")
    exp_pk = [d[0] for d in defs if "P" in d[3]]
    if sorted(pk_cols(t)) != sorted(exp_pk):
        bad.append(f"{name}: PK {pk_cols(t)} != {exp_pk}")
    n_pk += len(exp_pk)
check(f"Cột (tên, thứ tự, kiểu, NULL/NOT NULL), PK của {len(all_defs)} bảng ({n_cols} cột, {n_pk} cột PK); không dùng Enum làm kiểu, không default",
      not bad, "; ".join(bad[:8]))

# ---------------------------------------------------------------- 3. khóa ngoại
refs = []
for rf in J["refs"].values():
    eps = [J["endpoints"][str(e)] for e in rf["endpointIds"]]
    # '*' là phía FK; với quan hệ 1-1 ('-') FK là endpoint đứng trước (quy ước trong file)
    fk, pkk = (eps[0], eps[1]) if eps[0]["relation"] == "*" or eps[1]["relation"] == "1" else (eps[1], eps[0])
    if eps[0]["relation"] == "1" and eps[1]["relation"] == "1":
        fk, pkk = eps[0], eps[1]
    refs.append((fk["tableName"], tuple(fk["fieldNames"]), pkk["tableName"], tuple(pkk["fieldNames"]), rf["name"]))
exp_fk = {(a, tuple(b), c, tuple(d)) for a, b, c, d, _ in S.FKS}
derived_fk = {("THONG_KE_CHECKIN", ("MaCN",), "CHI_NHANH", ("MaCN",)), ("DOANH_THU_NGAY", ("MaCN",), "CHI_NHANH", ("MaCN",))}
got_fk = [x[:4] for x in refs]
check(f"{len(S.FKS)} khóa ngoại ERD khớp (bảng.cột -> bảng.cột, đúng chiều) + 2 FK của bảng dẫn xuất",
      set(got_fk) == exp_fk | derived_fk and len(got_fk) == len(set(got_fk)),
      f"thiếu {sorted((exp_fk | derived_fk) - set(got_fk))} thừa {sorted(set(got_fk) - (exp_fk | derived_fk))}")
comp = [x for x in refs if len(x[1]) > 1]
check("FK ghép duy nhất: DANG_KY_GOI.(MaHD, SoThuTu) -> CHI_TIET_HOA_DON.(MaHD, SoThuTu)",
      len(comp) == 1 and comp[0][:4] == ("DANG_KY_GOI", ("MaHD", "SoThuTu"), "CHI_TIET_HOA_DON", ("MaHD", "SoThuTu")))
names = [x[4] for x in refs]
check("Mỗi Ref có tên và tên không trùng", all(names) and len(names) == len(set(names)))

# ---------------------------------------------------------------- 4. UNIQUE / unique filtered index
bad = []
for name, d in S.TABLES.items():
    t = tables.get(name)
    if not t:
        continue
    ixs = [idx_by_id[str(i)] for i in t["indexIds"]]
    ixmap = {ix["name"]: ix for ix in ixs if ix.get("name")}
    for cn, ctype, notnull, flag in [(c[0], c[1], c[2], c[3]) for c in d["cols"]]:
        if "U" not in flag:
            continue
        f = next(f for f in cols(t) if f["name"] == cn)
        single = [ix for ix in ixs if index_cols(ix) == [cn] and ix.get("unique", False) or
                  (index_cols(ix) == [cn] and "unique" in (ix.get("note") or "").lower())]
        if notnull:
            if not (f.get("unique") or single):
                bad.append(f"{name}.{cn}: cột UNIQUE NOT NULL thiếu unique")
        else:
            if f.get("unique"):
                bad.append(f"{name}.{cn}: cho phép NULL nhưng dùng unique thường")
            if not any("IS NOT NULL" in (ix.get("note") or "") or "WHERE" in (ix.get("note") or "") for ix in single):
                bad.append(f"{name}.{cn}: cho phép NULL nhưng thiếu unique filtered index WHERE ... IS NOT NULL")
    # mọi chỉ mục/UNIQUE của lược đồ chuẩn phải có đúng tên, đúng cột, đúng điều kiện WHERE / INCLUDE
    for line in d["idx"]:
        m = re.match(r"(\w+):\s*(UNIQUE\s*)?\(([^)]*)\)(?:\s+INCLUDE\s*\(([^)]*)\))?(?:\s+WHERE\s+([^-\[]+?))?\s*(?:--|\[|$)", line)
        if not m:
            bad.append(f"{name}: không đọc được dòng chỉ mục chuẩn {line!r}")
            continue
        iname, uq, icols, inc, where = m.groups()
        ix = ixmap.get(iname)
        if not ix:
            bad.append(f"{name}: thiếu chỉ mục {iname}")
            continue
        want = [c.strip() for c in icols.split(",")]
        if index_cols(ix) != want:
            bad.append(f"{name}.{iname}: cột {index_cols(ix)} != {want}")
        if bool(uq) != bool(ix.get("unique")):
            bad.append(f"{name}.{iname}: unique={ix.get('unique')} != {bool(uq)}")
        note = (ix.get("note") or "")
        if inc and re.sub(r"\s", "", inc) not in re.sub(r"\s", "", note):
            bad.append(f"{name}.{iname}: note thiếu INCLUDE ({inc})")
        if where and where.strip() not in note:
            bad.append(f"{name}.{iname}: note thiếu điều kiện WHERE {where.strip()}")
    # khóa thay thế ghép (MaNV, NgayBatDau) nằm trong idx; các CHECK chuẩn phải có tên trong Note
    text = table_text(t)
    for line in d["checks"]:
        ck = line.split(":")[0]
        if ck not in text:
            bad.append(f"{name}: Note không nhắc {ck}")
check("UNIQUE/unique filtered index, mọi chỉ mục chuẩn (tên, cột, INCLUDE, WHERE) và tên mọi CHECK chuẩn có trong DBML", not bad, "; ".join(bad[:10]))
n_filtered = sum(1 for t in tables.values() for i in t["indexIds"] if "WHERE" in (idx_by_id[str(i)].get("note") or ""))
print(f"        (số chỉ mục ghi WHERE trong Note: {n_filtered})")

# ---------------------------------------------------------------- 5. FK ghép vật lý (E3): bảng đích có UNIQUE đúng cột, bảng nguồn có nhắc
bad = []
for src_t, fcols, dst_t, dcols, why in S.FK_VATLY:
    t = tables[dst_t]
    ok = sorted(pk_cols(t)) == sorted(dcols) or any(
        index_cols(idx_by_id[str(i)]) == list(dcols) and idx_by_id[str(i)].get("unique") for i in t["indexIds"])
    if not ok:
        bad.append(f"{dst_t}: thiếu UNIQUE/PK {dcols}")
    if "(" + ", ".join(fcols) + ")" not in table_text(tables[src_t]):
        bad.append(f"{src_t}: Note chưa mô tả FK ghép vật lý ({', '.join(fcols)})")
check("4 FK ghép vật lý (E3): bảng đích có UNIQUE đúng cột; Note bảng nguồn mô tả", not bad, "; ".join(bad))

# ---------------------------------------------------------------- 6. Enum <-> CHECK chuẩn
enum_map = {  # tên enum: (bảng, tên CHECK chuẩn)
    "TrangThaiDK": ("DANG_KY_GOI", "CK_DK_TrangThai"), "TrangThaiLH": ("LICH_HEN_PT", "CK_LH_TrangThai"),
    "TrangThaiHD": ("HOA_DON", "CK_HD_TrangThai"), "HinhThucThanhToan": ("HOA_DON", "CK_HD_HinhThuc"),
    "ChucVuNV": ("NHAN_VIEN", "CK_NV_ChucVu"), "LoaiChiTiet": ("CHI_TIET_HOA_DON", "CK_CT_Loai"),
    "TrangThaiCNDV": ("CHI_NHANH_DICH_VU", "CK_CNDV_TrangThai"), "GioiTinhHV": ("HOI_VIEN", "CK_HV_GioiTinh"),
}
bad = []
for en, (tb, ck) in enum_map.items():
    line = next(c for c in S.TABLES[tb]["checks"] if c.startswith(ck + ":"))
    want = re.findall(r"N'([^']+)'", line)
    if en not in enums:
        bad.append(f"thiếu Enum {en}")
    elif enums[en] != want:
        bad.append(f"Enum {en} {enums[en]} != CHECK {want}")
req = ["TrangThaiDK", "TrangThaiLH", "TrangThaiHD", "HinhThucThanhToan", "ChucVuNV", "LoaiChiTiet"]
check("Enum (6 yêu cầu + 2 bổ sung) khớp giá trị CHECK chuẩn; không có Bảo lưu; ChucVu dùng HLV",
      not bad and all(e in enums for e in req) and "Bảo lưu" not in enums["TrangThaiDK"] and "HLV" in enums["ChucVuNV"], "; ".join(bad))
check("Note của Enum/CHECK nêu cài bằng CHECK (N'...')", "cài bằng CHECK" in src and "CHECK (cột IN (N'...'" in src)

# ---------------------------------------------------------------- 7. cột dẫn xuất (E5)
bad = []
for name, d in S.TABLES.items():
    for c in d["cols"]:
        if "D" in c[3]:
            f = next(f for f in cols(tables[name]) if f["name"] == c[0])
            if "Dẫn xuất" not in (f.get("note") or "") or "LƯU" not in (f.get("note") or ""):
                bad.append(f"{name}.{c[0]}")
hv = tables["HOI_VIEN"]
check("Cột dẫn xuất lưu (TongTienGoc, ThanhToanThucTe, ThanhTien, NgayKetThuc) ghi rõ trong Note cột; [Tuoi] không có cột và Note nêu không lưu",
      not bad and "Tuoi" not in [f["name"] for f in cols(hv)] and "[Tuoi]" in (hv.get("note") or "") and "KHÔNG lưu" in (hv.get("note") or ""),
      "; ".join(bad))

# ---------------------------------------------------------------- 8. bảng dẫn xuất
bad = []
for n in S.DERIVED_TABLES:
    nt = tables[n].get("note") or ""
    if "DẪN XUẤT" not in nt or "KHÔNG có trên ERD" not in nt:
        bad.append(n)
order = [m.group(1) for m in re.finditer(r"^Table (\w+)", src, re.M)]
check("THONG_KE_CHECKIN, DOANH_THU_NGAY ở cuối file, Note ghi bảng dẫn xuất không có trên ERD",
      not bad and order[-2:] == ["THONG_KE_CHECKIN", "DOANH_THU_NGAY"], "; ".join(bad))
tk = [f["name"] for f in cols(tables["THONG_KE_CHECKIN"])]
check("THONG_KE_CHECKIN có SoLuotVao và SoLuotRa (đủ tính người có mặt, E9) và Note nêu công thức lấp đầy theo SucChua",
      {"SoLuotVao", "SoLuotRa"} <= set(tk) and "SoLuot" not in tk and "SucChua" in (tables["THONG_KE_CHECKIN"].get("note") or ""))

# ---------------------------------------------------------------- 9. mã RBxx
header = src.split("Project FitLifeHub")[0]
catalog = set(re.findall(r"\bRB(\d\d)\b", header))
used = set()
for t in tables.values():
    used |= set(re.findall(r"\bRB(\d\d)\b", table_text(t)))
body_enum_refs = set(re.findall(r"\bRB(\d\d)\b", src.split("Project FitLifeHub", 1)[1]))
check(f"Mã RBxx: danh mục {len(catalog)} mã; mọi mã dùng trong Note đều có trong danh mục; mọi mã danh mục đều được dùng",
      used <= catalog and catalog <= (used | body_enum_refs),
      f"dùng nhưng không có trong danh mục {sorted(used - catalog)}; có trong danh mục nhưng chưa dùng {sorted(catalog - used - body_enum_refs)}")

# ---------------------------------------------------------------- 10. index đề xuất thêm
extra = []
for name, t in tables.items():
    canon = set()
    if name in S.TABLES:
        canon = {re.match(r"(\w+):", x).group(1) for x in S.TABLES[name]["idx"]}
    for i in t["indexIds"]:
        ix = idx_by_id[str(i)]
        if not ix.get("pk") and ix.get("name") not in canon:
            extra.append((name, ix.get("name"), ix.get("note") or ""))
bad = [f"{a}.{b}" for a, b, c in extra if "[ĐX]" not in c or not b]
check(f"{len(extra)} chỉ mục đề xuất thêm, đều đánh dấu [ĐX] kèm lý do", not bad, "; ".join(bad))
for a, b, c in extra:
    print(f"        + {a}.{b}")

# ---------------------------------------------------------------- 11. tên cấm của thiết kế cũ
legacy = ["THIET_BI", "KHUNG_GIO", "CHI_TIEU_THANG", "LICH_SU_HANG", "LICH_SU_CONG_TAC", "CT_HOADON_SP", "NgayBaoLuu", "NgayHetHan",
          "SoBuoiPT", "MaPT", "MaTB", "MaKG", "MaLH", "MaDG", "NgayTap", "DiemTichLuy", "SoLuongTon", "HinhThucTT", "LoaiSP"]
ident = set(tables) | {f["name"] for t in tables.values() for f in cols(t)}
check("Không còn tên của thiết kế cũ trong bảng/cột", not (ident & set(legacy)), str(sorted(ident & set(legacy))))
check("Project có database_type: 'SQL Server'", re.search(r"database_type:\s*'SQL Server'", src) is not None)

nbad = sum(1 for ok, _, _ in results if not ok)
print(f"\nKẾT QUẢ: {'ĐẠT TOÀN BỘ' if nbad == 0 else 'CÓ LỖI'} ({nbad} mục lỗi / {len(results)} mục)")
sys.exit(1 if nbad else 0)
