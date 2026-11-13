"""Phần 3: mục 4.5 (RB01–RB30), 4.6 (mô tả quan hệ/thuộc tính), mục 5 và khối thành viên (giữ nguyên v2)."""
import re, zipfile
from lxml import etree
from xmllib import *
from model import *
import dbml_parse
from rb_data import RBX
from desc46 import D46
import part2

D = part2.D
T = D["tables"]
REFS = D["refs"]
V2 = r"D:\HK1_Năm 3\CSDL Nâng cao - Pass hangvu@hcmus-20260913\Đồ án\BaoCao_GD1_FitLifeHub_v2.docx"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def rb_section():
    o = [h2("4.5 Mô tả ràng buộc toàn vẹn")]
    o.append(p(f"Mỗi ràng buộc gồm bối cảnh (các quan hệ liên quan), nội dung (biểu thức logic), cách cài đặt trên SQL Server và bảng tầm ảnh hưởng. Có {len(RBX)} ràng buộc RB01–RB{len(RBX):02d} (RB29 và RB30 là đề xuất chờ xác nhận, chưa cài). Trong bảng tầm ảnh hưởng: '+' nghĩa là thao tác đó có thể làm vi phạm ràng buộc nên phải kiểm tra; '-' là không ảnh hưởng; '+ (A, B)' là phép sửa chỉ cần kiểm tra khi thay đổi thuộc tính A hoặc B."))
    for (code, title) in RB:
        d = RBX[code]
        o.append(h3(f"{code} – {title}"))
        rows = [["Loại", d["loai"]], ["Bối cảnh", d["boi_canh"]], ["Nội dung", d["noi_dung"]], ["Cài đặt", d["cai_dat"]]]
        o.append(table([1400, 8238], ["Mục", "Mô tả"], rows, keep=(len(d["noi_dung"]) < 3), first_bold=True))
        o.append(spacer(keep=True))
        imp = [[a, b, c, e] for a, b, c, e in d["impact"]]
        o.append(table([3000, 900, 900, 4838], ["Bảng tầm ảnh hưởng", "Thêm", "Xóa", "Sửa"], imp, keep=(len(imp) < 5), center_cols=(1, 2)))
        o.append(spacer())
    return o


def col_constraint(table_name, c, extra):
    t = T[table_name]
    fks = [r for r in REFS if r["t"] == table_name and c["name"] in r["c"]]
    parts = []
    is_pk = c["name"] in t["pk"]
    if is_pk:
        parts.append("PK")
    if fks:
        parts.append("FK → " + fks[0]["rt"])
    if not is_pk:
        parts.append("NULL" if c["null"] else "NOT NULL")
    if extra:
        parts.append(extra)
    return ", ".join(parts)


def attr_section():
    o = [h2("4.6 Mô tả quan hệ và thuộc tính"),
         p("Với mỗi quan hệ: ý nghĩa, sau đó bảng thuộc tính gồm kiểu dữ liệu SQL Server, ràng buộc (khóa, khóa ngoại, NULL/NOT NULL, miền giá trị, mã RB) và ý nghĩa. Kiểu dữ liệu và khả năng NULL lấy từ lược đồ chuẩn/DBML. PK ghép được ghi ở từng cột thành phần.")]
    for k, name in enumerate(REL_ORDER, 1):
        intro, cols = D46[name]
        t = T[name]
        assert [c[0] for c in cols] == [c["name"] for c in t["cols"]], name
        o.append(h3(f"4.6.{k} {name}"))
        pk = ", ".join(t["pk"])
        o.append(p(f"{intro} Khóa chính: {pk}.", keep=True))
        rows = []
        for c, (cn, extra, desc) in zip(t["cols"], cols):
            rows.append([c["name"], c["type"], col_constraint(name, c, extra), desc])
        o.append(table([2100, 2000, 2338, 3200], ["Thuộc tính", "Kiểu dữ liệu", "Ràng buộc", "Mô tả"], rows, sz=22))
        o.append(spacer())
    return o


def section5():
    o = [h1("5. Đối chiếu yêu cầu nộp giai đoạn 1")]
    nq, nrb, nlk, nent = len(REL_ORDER), len(RBX), len(LINKS), len(ENTITIES)
    rows = [
        ["Mô tả chi tiết quy trình nghiệp vụ", f"Mục 1 (QT1 – QT{N_QT})"],
        ["Bảng phân tích tần suất của chức năng (chức năng, mô tả, tần suất, mức độ)", f"Mục 2 (CN01 – CN{N_CN})"],
        ["Thiết kế mức quan niệm: mô hình ERD", f"Mục 3.1 – 3.3 (ERD {nent} thực thể, bảng {nlk} mối liên kết, chú giải, hình ERD gốc) và file ERD kèm theo"],
        ["Mô tả các ràng buộc chưa thể hiện trên mô hình", "Mục 3.4"],
        ["Lược đồ CSDL quan hệ", f"Mục 4.1 – 4.2 ({nq} quan hệ, {len(part2.FK_ALL)} khóa ngoại, ba hình mô-đun)"],
        ["Mỗi quan hệ: khóa, phụ thuộc hàm, dạng chuẩn; kết luận dạng chuẩn", "Mục 4.3 và 4.4"],
        ["Mô tả ràng buộc: bối cảnh, nội dung, bảng tầm ảnh hưởng", f"Mục 4.5 (RB01 – RB{nrb:02d})"],
        ["Mô tả thông tin của quan hệ và các thuộc tính", f"Mục 4.6 (4.6.1 – 4.6.{nq})"],
        ["Thông tin cá nhân, nhóm, đánh giá cá nhân và nhóm; công cụ quản lý tiến độ", "Trang bìa và mục Thành viên và đánh giá đóng góp (nhóm điền phân công, đánh giá, tên công cụ)"],
    ]
    o.append(table([4800, 4838], ["Yêu cầu giai đoạn 1", "Vị trí trong báo cáo"], rows))
    # khối thành viên: lấy nguyên từ v2 (phần tử 450–455), nhóm tự điền
    z = zipfile.ZipFile(V2)
    root = etree.fromstring(z.read("word/document.xml"))
    body = root.find(f"{{{W}}}body")
    ch = list(body)
    for el in ch[450:456]:
        s = etree.tostring(el, encoding="unicode")
        s = re.sub(r' xmlns:\w+="[^"]+"', "", s)
        o.append(s)
    return o


def build():
    return rb_section() + attr_section() + section5()
