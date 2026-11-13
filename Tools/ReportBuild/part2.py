"""Phần 2: mục 4.1 – 4.4 (ánh xạ, lược đồ quan hệ, khóa/PTH/dạng chuẩn, kết luận dạng chuẩn)."""
from xmllib import *
from model import *
import dbml_parse

D = dbml_parse.parse()
T = D["tables"]
REFS = D["refs"]
FK_ERD = [r for r in REFS if r["t"] not in DERIVED_TABLES]       # 33 khóa ngoại của ERD
FK_ALL = REFS                                                       # 35 (kể cả 2 bảng dẫn xuất)
DERIVED_COLS = {("HOA_DON", "TongTienGoc"), ("HOA_DON", "ThanhToanThucTe"),
                ("CHI_TIET_HOA_DON", "ThanhTien"), ("DANG_KY_GOI", "NgayKetThuc")}

NF = {  # dạng chuẩn thật sự của từng quan hệ (xem bảng 4.3)
    "CHI_NHANH": "BCNF", "LOAI_DICH_VU": "BCNF", "CHI_NHANH_DICH_VU": "BCNF", "PHONG": "BCNF",
    "GOI_DICH_VU": "BCNF", "SAN_PHAM": "BCNF", "TON_KHO": "BCNF", "HANG_HOI_VIEN": "BCNF", "HOI_VIEN": "BCNF",
    "DIEM_LOYALTY": "2NF", "NHAN_VIEN": "BCNF", "HUAN_LUYEN_VIEN": "BCNF", "HLV_CHUNG_CHI": "BCNF",
    "LICH_SU_DIEU_CHUYEN": "BCNF", "HOA_DON": "2NF", "CHI_TIET_HOA_DON": "2NF", "DANG_KY_GOI": "2NF",
    "CHECK_IN": "2NF", "LICH_HEN_PT": "2NF", "DANH_GIA_PT": "BCNF", "THONG_KE_CHECKIN": "BCNF",
    "DOANH_THU_NGAY": "BCNF",
}
N_BCNF = sum(1 for v in NF.values() if v == "BCNF")
N_2NF = sum(1 for v in NF.values() if v == "2NF")
LIST_2NF = [k for k in REL_ORDER if NF[k] == "2NF"]
assert set(NF) == set(REL_ORDER) == set(T), (set(NF) ^ set(T))


def fk_cols(table):
    s = set()
    for r in REFS:
        if r["t"] == table:
            s.update(r["c"])
    return s


def schema_markup(table):
    t = T[table]
    fks = fk_cols(table)
    parts = []
    for c in t["cols"]:
        n = c["name"]
        txt = f"[{n}]" if (table, n) in DERIVED_COLS else n
        pk, fk = n in t["pk"], n in fks
        if pk and fk:
            txt = f"__^^{txt}^^__"
        elif pk:
            txt = f"__{txt}__"
        elif fk:
            txt = f"^^{txt}^^"
        parts.append(txt)
    return ", ".join(parts)


def nullable_cols():
    out = []
    for n in REL_ORDER:
        for c in T[n]["cols"]:
            if c["null"]:
                out.append((n, c["name"]))
    return out


def mapping_rules():
    nq, nl = len(REL_ORDER), len(LINKS)
    o = [h1("4. Thiết kế mức logic"), h2("4.1 Quy tắc ánh xạ ERD sang quan hệ")]
    rules = [
        f"Thực thể thường và thực thể kết hợp có khóa riêng ({', '.join(ENT_THUONG + ENT_KET_HOP)}) thành một quan hệ; khóa chính là khóa của thực thể (MaCN, MaLoai, MaPhong, MaGoi, MaSP, MaHang, MaHV, MaHD, MaNV, MaDanhGia, MaDK, MaCheckIn, MaLichHen, MaDieuChuyen).",
        "Thuộc tính tổng hợp chỉ giữ các thành phần đơn: DiaChi thành SoNha, Duong, Quan, ThanhPho; HoTen thành Ho, TenDem, Ten (HOI_VIEN, NHAN_VIEN).",
        "Thuộc tính dẫn xuất [Tuoi] không lưu (tính từ NgaySinh bằng view/hàm vì phụ thuộc ngày hiện tại). Bốn thuộc tính dẫn xuất còn lại ([TongTienGoc], [ThanhToanThucTe], [ThanhTien], [NgayKetThuc]) được lưu có chủ đích, xem bảng cuối mục này.",
        "Thuộc tính đa trị {ChungChi} thành quan hệ HLV_CHUNG_CHI (MaHLV, ChungChi), khóa gồm cả hai thuộc tính.",
        "Thực thể yếu (DIEM_LOYALTY, CHI_TIET_HOA_DON) nhận khóa chính của thực thể chủ cộng khóa bộ phận: (MaHV, NamXet) và (MaHD, SoThuTu); phần khóa của thực thể chủ đồng thời là khóa ngoại.",
        "Thực thể kết hợp có khóa riêng dùng mã riêng làm khóa chính, khóa của các thực thể tham gia thành khóa ngoại. Khóa dự tuyển (MaNV, NgayBatDau) của LICH_SU_DIEU_CHUYEN được giữ bằng UNIQUE.",
        "Quan hệ N–N có thuộc tính (CHI_NHANH_DICH_VU, TON_KHO) thành quan hệ riêng, khóa gồm khóa của hai thực thể ((MaCN, MaLoai), (MaCN, MaSP)) cộng các thuộc tính của mối liên kết.",
        "Chuyên biệt hóa partial, một lớp con, d/o không áp dụng (ký hiệu U): HUAN_LUYEN_VIEN thành quan hệ riêng, MaHLV vừa là khóa chính vừa là khóa ngoại tham chiếu NHAN_VIEN.MaNV (1–(0..1)); ChucVu = 'HLV' khi và chỉ khi có dòng ở đây (RB26). Lễ tân, Quản lý, Bán hàng chỉ là giá trị của ChucVu.",
        "Mối liên kết 1–N: khóa ngoại đặt ở phía N. Mối liên kết 1–(0..1) LICH_HEN_PT – DANH_GIA_PT: khóa ngoại MaLichHen ở DANH_GIA_PT kèm UNIQUE. Hai liên kết “gồm” tới GOI_DICH_VU và SAN_PHAM (0..1 phía gói/sản phẩm): MaGoi, MaSP trong CHI_TIET_HOA_DON cho phép NULL và loại trừ nhau bằng CHECK theo Loai (RB07). Liên kết “xuất ra”: khóa ngoại ghép (MaHD, SoThuTu) ở DANG_KY_GOI, không có UNIQUE để một dòng sinh được SoLuong gói (RB08).",
        "Quy tắc riêng của SQL Server: không có ENUM nên miền giá trị cài bằng CHECK (cột IN (N'...')) (RB02); UNIQUE trên cột cho phép NULL (Email, CCCD, SoDienThoai nhân viên) phải là unique filtered index WHERE cột IS NOT NULL (RB03); không có ràng buộc trì hoãn nên các kiểm tra “tối thiểu một” và đếm nhiều dòng thực hiện ở cuối giao dịch của thủ tục (RB08, RB14).",
        "Dư thừa có chủ đích (E3) được giữ đồng nhất bằng khóa ngoại phức hợp ở mức vật lý (khai báo) hoặc bằng trigger; danh sách ở mục 4.4.",
        "Bảng dẫn xuất THONG_KE_CHECKIN và DOANH_THU_NGAY không có trên ERD, được thêm ở mức logic để phục vụ báo cáo nhanh (vấn đề 3, RB27, RB28).",
        f"Số quan hệ: {len(ENTITIES)} thực thể của ERD ánh xạ thành {len(ENTITIES)} quan hệ, cộng HLV_CHUNG_CHI tách từ thuộc tính đa trị thành {len(ENTITIES) + 1} quan hệ, cộng {len(DERIVED_TABLES)} bảng dẫn xuất, tổng cộng {nq} quan hệ. Số khóa ngoại: {nl} mối liên kết của ERD cho {nl} khóa ngoại, cộng 1 của HLV_CHUNG_CHI thành {len(FK_ERD)} khóa ngoại, cộng {len(FK_ALL) - len(FK_ERD)} của hai bảng dẫn xuất thành {len(FK_ALL)}.",
    ]
    for r in rules:
        o.append(bullet(r))
    o.append(p("Thuộc tính dẫn xuất của ERD và cách xử lý (E5):", after=60, keep=True, bold=True))
    e5 = [
        ["[ThanhTien] của CHI_TIET_HOA_DON = SoLuong × DonGia", "Lưu", "Cột tính PERSISTED", "Cùng dòng nên DBMS tự duy trì, không thể lệch; dùng lại khi cộng doanh thu và xếp hạng gói bán chạy (RB10)."],
        ["[TongTienGoc] của HOA_DON = Σ ThanhTien", "Lưu", "Cột thường; thủ tục lập hóa đơn ghi, trigger trên CHI_TIET_HOA_DON kiểm tra khớp", "Vượt quan hệ nên không dùng được cột tính; báo cáo doanh thu khỏi nối CHI_TIET_HOA_DON. Vi phạm 3NF có chủ đích (RB09)."],
        ["[ThanhToanThucTe] của HOA_DON = TongTienGoc − GiamGia", "Lưu", "Cột tính PERSISTED, CHECK GiamGia ≤ TongTienGoc", "Đầu vào của điểm Loyalty và doanh thu, cần đọc nhanh và đánh chỉ mục; DBMS tự duy trì (RB09)."],
        ["[NgayKetThuc] của DANG_KY_GOI = NgayBatDau + ThoiHanThang tháng", "Lưu", "Cột thường; thủ tục đăng ký ghi và kiểm tra", "Phụ thuộc GOI_DICH_VU.ThoiHanThang nên không là cột tính; cần trong chỉ mục xác thực check-in (vấn đề 1); đổi thời hạn gói sau này không ảnh hưởng gói đã bán (RB11)."],
        ["[Tuoi] của HOI_VIEN", "Không lưu", "View hoặc hàm tính từ NgaySinh", "Phụ thuộc ngày hiện tại nên không thể PERSISTED; lưu sẽ sai theo thời gian."],
    ]
    o.append(table([2500, 900, 2400, 3838], ["Thuộc tính dẫn xuất", "Lưu?", "Cách duy trì", "Lý do (dạng chuẩn / hiệu năng)"], e5))
    o.append(p("", after=100))
    return o


FK_NOTE = {
    "FK_DL_HV": "1 – N: thực thể yếu, FK nằm trong PK",
    "FK_CT_HD": "1 – N: thực thể yếu, FK nằm trong PK",
    "FK_CT_Goi": "N – (0..1): phía FK tùy chọn",
    "FK_CT_SP": "N – (0..1): phía FK tùy chọn",
    "FK_DK_CT": "FK ghép; một dòng chi tiết có thể có nhiều DANG_KY_GOI (RB08)",
    "FK_HLV_NV": "1 – (0..1): chuyên biệt hóa, FK là PK",
    "FK_CC_HLV": "1 – N: thuộc tính đa trị",
    "FK_DG_LH": "1 – (0..1): FK + UNIQUE",
    "FK_CI_Phong": "N – (0..1): phía FK tùy chọn",
    "FK_TKCI_CN": "bảng dẫn xuất (không thuộc ERD)",
    "FK_DTN_CN": "bảng dẫn xuất (không thuộc ERD)",
}


def ref_label(r):
    lab = r["label"]
    if r["name"] in ("FK_CT_HD", "FK_CT_Goi", "FK_CT_SP"):
        return f"gồm ({r['rt']})"
    if r["name"] == "FK_HLV_NV":
        return "U (chuyên biệt hóa)"
    if r["name"] == "FK_CC_HLV":
        return "{ChungChi} đa trị"
    if r["name"] in ("FK_TKCI_CN", "FK_DTN_CN"):
        return "–"
    return re.sub(r"\s*\(.*$", "", lab)


def fmt_cols(t, cols):
    return f"{t}.{cols[0]}" if len(cols) == 1 else f"{t}.({', '.join(cols)})"


def logical_schema():
    nq = len(REL_ORDER)
    o = [h2("4.2 Lược đồ cơ sở dữ liệu quan hệ")]
    o.append(p(f"Gạch chân là thuộc tính khóa chính; in nghiêng là khóa ngoại (khóa chính đồng thời là khóa ngoại vừa gạch chân vừa in nghiêng); thuộc tính trong ngoặc vuông là dẫn xuất có lưu. Lược đồ gồm {nq} quan hệ ({len(ENTITIES) + 1} quan hệ ánh xạ từ ERD và {len(DERIVED_TABLES)} bảng dẫn xuất), nội dung lấy từ lược đồ chuẩn và khớp file DBML."))
    nulls = nullable_cols()
    fkn = [f"{a}.{b}" for a, b in nulls if b in fk_cols(a)]
    nonfk = [f"{a}.{b}" for a, b in nulls if b not in fk_cols(a)]
    o.append(p(f"Khóa ngoại: mọi khóa ngoại đều NOT NULL, trừ {len(fkn)} khóa ngoại tùy chọn ({', '.join(fkn)}): hai khóa đầu loại trừ nhau theo Loai (RB07), CHECK_IN.MaPhong là bản số 0..1 của “vào phòng”. Thuộc tính không khóa được phép NULL có chủ đích ({len(nonfk)} cột): {', '.join(nonfk)}. DANH_GIA_PT.MaLichHen là UNIQUE vì mỗi buổi PT có tối đa một đánh giá. Kiểu dữ liệu và miền giá trị từng cột ở mục 4.6.", after=100))
    for k, n in enumerate(REL_ORDER, 1):
        o.append(schema_line(k, n, schema_markup(n)))
    o.append(p(f"Tổng cộng {nq} quan hệ, {sum(len(T[n]['cols']) for n in REL_ORDER)} cột. Các cột có ký hiệu [ ] được giải thích ở bảng thuộc tính dẫn xuất (mục 4.1).", after=100))
    # --- khóa ngoại
    o.append(p(f"Danh sách {len(FK_ALL)} khóa ngoại: {len(FK_ERD)} khóa ngoại của ERD (mỗi mối liên kết một khóa ngoại, thêm khóa ngoại của HLV_CHUNG_CHI) và {len(FK_ALL) - len(FK_ERD)} khóa ngoại của hai bảng dẫn xuất:", keep=True, bold=True, after=60))
    rows = []
    for k, r in enumerate(FK_ALL, 1):
        nullable = any(c["null"] for c in T[r["t"]]["cols"] if c["name"] in r["c"])
        rows.append([str(k), fmt_cols(r["t"], r["c"]), fmt_cols(r["rt"], r["rc"]), ref_label(r),
                     "NULL" if nullable else "NOT NULL", FK_NOTE.get(r["name"], "N – 1")])
    o.append(table([500, 2700, 2700, 1500, 900, 1338], ["#", "Khóa ngoại", "Tham chiếu", "Mối liên kết trên ERD", "NULL?", "Bản số / ghi chú"], rows, center_cols=(0,), sz=22))
    o.append(p("", after=100))
    o.append(p("Khóa ngoại phức hợp thực thi ở mức vật lý (E3): mỗi dòng thay cho khóa ngoại đơn cùng mối liên kết ở bảng trên nên không làm tăng số khóa ngoại; bảng đích phải có UNIQUE tương ứng.", keep=True, bold=True, after=60))
    comp = [
        ["DANG_KY_GOI", "(MaHD, SoThuTu, MaGoi)", "CHI_TIET_HOA_DON (MaHD, SoThuTu, MaGoi), UNIQUE UQ_CT_HD_STT_Goi", "MaGoi của DANG_KY_GOI trùng gói ở dòng chi tiết; dòng sản phẩm (MaGoi NULL) không thể được tham chiếu (RB08)"],
        ["CHECK_IN", "(MaDK, MaHV)", "DANG_KY_GOI (MaDK, MaHV), UNIQUE UQ_DK_DK_HV", "CHECK_IN.MaHV bằng hội viên của gói (RB17)"],
        ["LICH_HEN_PT", "(MaDK, MaHV)", "DANG_KY_GOI (MaDK, MaHV), UNIQUE UQ_DK_DK_HV", "LICH_HEN_PT.MaHV bằng hội viên của gói (RB18)"],
        ["CHECK_IN", "(MaPhong, MaCN)", "PHONG (MaPhong, MaCN), UNIQUE UQ_PHONG_Phong_CN", "CHECK_IN.MaCN bằng PHONG.MaCN khi có phòng; MaPhong NULL thì không kiểm tra (RB17)"],
    ]
    o.append(table([1500, 1900, 3000, 3238], ["Bảng", "Khóa ngoại phức hợp", "Tham chiếu", "Mục đích"], comp))
    o.append(p("", after=100))
    # --- hình mô-đun trên các trang ngang
    o.append(sect_break("portrait", "rId14"))
    o.append(p("Ba hình dưới đây vẽ lược đồ quan hệ theo mô-đun (hộp có tên bảng, ô cột; khóa chính gạch liền, khóa ngoại gạch đứt, mũi tên từ khóa ngoại đến khóa chính được tham chiếu; bảng nhạt nét đứt thuộc mô-đun khác). Ba hình cộng lại phủ đúng 33 khóa ngoại của ERD, mỗi khóa ngoại một lần: hình 1 có 7, hình 2 có 12, hình 3 có 14; hai bảng dẫn xuất không vẽ. Hình tổng 20 bảng (luoc_do_tong.png) và file chỉnh sửa luoc_do_quan_he_v4.drawio nộp kèm.", after=100, page_break_before=False))
    for k, (rid, hpx, ttl) in enumerate([("rId11", 1208, "Hình 1 – Danh mục, chi nhánh, sản phẩm & tồn kho (7 bảng, 7 khóa ngoại)"),
                                         ("rId12", 1728, "Hình 2 – Hội viên, loyalty, gói đăng ký & hóa đơn (6 bảng, 12 khóa ngoại)"),
                                         ("rId13", 1728, "Hình 3 – Nhân sự, lịch hẹn PT & check-in (7 bảng, 14 khóa ngoại)")], 1):
        cx = int(25.6 * 360000)
        cy = int(cx * hpx / 3400)
        o.append(image(rid, cx, cy, f"luoc_do_mo_dun_{k}.png", ttl, page_break_before=(k > 1)))
    o.append(sect_break("landscape", "rId10"))
    return o


def normal_forms():
    o = [h2("4.3 Khóa, phụ thuộc hàm và dạng chuẩn của từng quan hệ")]
    o.append(p("Phụ thuộc hàm được xác định từ ràng buộc dữ liệu trong đặc tả và các ràng buộc ở mục 4.5. Quan hệ đạt BCNF khi mọi vế trái của phụ thuộc hàm không tầm thường là siêu khóa; nếu có vế trái không là siêu khóa và vế phải là thuộc tính không khóa (phụ thuộc bắc cầu) thì quan hệ chỉ đạt 2NF (mọi khóa chính ở đây là đơn hoặc không có phụ thuộc từng phần vào khóa ghép). Giá trị dẫn xuất từ quan hệ khác (ví dụ tổng chi tiêu theo hóa đơn) không tạo phụ thuộc hàm bên trong một quan hệ nên được ghi ở cột nhận xét."))
    r = [
        ["CHI_NHANH", "MaCN; SoDienThoai", "MaCN → TenCN, SoNha, Duong, Quan, ThanhPho, SoDienThoai, GioMoCua, GioDongCua; SoDienThoai → MaCN", "BCNF", "Mọi vế trái là khóa. Không giả định Quan → ThanhPho vì tên quận không duy nhất giữa các thành phố."],
        ["LOAI_DICH_VU", "MaLoai; TenLoai", "MaLoai → TenLoai, MoTa; TenLoai → MaLoai", "BCNF", ""],
        ["CHI_NHANH_DICH_VU", "(MaCN, MaLoai)", "(MaCN, MaLoai) → TrangThai", "BCNF", "Thuộc tính không khóa phụ thuộc đầy đủ vào khóa ghép."],
        ["PHONG", "MaPhong", "MaPhong → MaCN, MaLoai, TenPhong, SucChua, ConHoatDong", "BCNF", "(MaPhong, MaCN) là siêu khóa, chỉ dùng làm đích khóa ngoại phức hợp của CHECK_IN (E3). ERD không nêu TenPhong duy nhất nên không coi (MaCN, TenPhong) là khóa."],
        ["GOI_DICH_VU", "MaGoi", "MaGoi → TenGoi, MaLoai, ThoiHanThang, SoBuoi, GiaTien, ConHieuLuc", "BCNF", ""],
        ["SAN_PHAM", "MaSP", "MaSP → TenSP, GiaBan, Loai, DonViTinh, ConBan", "BCNF", ""],
        ["TON_KHO", "(MaCN, MaSP)", "(MaCN, MaSP) → SoLuong, NgayCapNhat", "BCNF", ""],
        ["HANG_HOI_VIEN", "MaHang; TenHang; NguongChiTieu", "MaHang → TenHang, NguongChiTieu; TenHang → MaHang; NguongChiTieu → MaHang", "BCNF", "NguongChiTieu là khóa dự tuyển nhờ UNIQUE (RB06)."],
        ["HOI_VIEN", "MaHV; SoDienThoai; Email; CCCD", "Mỗi khóa dự tuyển → các thuộc tính còn lại", "BCNF", "Tuoi không lưu nên không có NgaySinh → Tuoi. HOI_VIEN không có cột hạng; hạng nằm ở DIEM_LOYALTY. Email, CCCD cho phép NULL nên là unique filtered index (RB03)."],
        ["DIEM_LOYALTY", "(MaHV, NamXet)", "(MaHV, NamXet) → TongChiTieuNam, DiemThuong, NgayCapNhat, MaHang; TongChiTieuNam → MaHang", "2NF", "TongChiTieuNam → MaHang (qua ngưỡng ở HANG_HOI_VIEN) là phụ thuộc bắc cầu nên vi phạm 3NF. Cố ý lưu MaHang để đọc hạng bằng một lần tra khóa chính và đếm phân bố hạng không phải so ngưỡng (vấn đề 4); nhất quán bằng RB04, RB06."],
        ["NHAN_VIEN", "MaNV; SoDienThoai", "MaNV → mọi thuộc tính; SoDienThoai → mọi thuộc tính (khi khác NULL)", "BCNF", "MaCN là chi nhánh hiện tại và trùng bản ghi đang mở của LICH_SU_DIEU_CHUYEN: dư thừa giữa hai quan hệ, không phải phụ thuộc hàm trong NHAN_VIEN; nhất quán bằng RB24 (E6)."],
        ["HUAN_LUYEN_VIEN", "MaHLV", "MaHLV → ChuyenMon, HoaHongMoiBuoi", "BCNF", "MaHLV vừa là khóa chính vừa là khóa ngoại tới NHAN_VIEN (RB26)."],
        ["HLV_CHUNG_CHI", "(MaHLV, ChungChi)", "Không có phụ thuộc hàm không tầm thường", "BCNF", "Tách thuộc tính đa trị nên không còn phụ thuộc đa trị không tầm thường: đạt cả 4NF."],
        ["LICH_SU_DIEU_CHUYEN", "MaDieuChuyen; (MaNV, NgayBatDau)", "MaDieuChuyen ↔ (MaNV, NgayBatDau); mỗi khóa → MaNV, MaCN, NgayBatDau, NgayKetThuc, LyDo", "BCNF", "MaCN là chi nhánh đích của từng giai đoạn; các giai đoạn liên tiếp, không chồng (RB23)."],
        ["HOA_DON", "MaHD", "MaHD → mọi thuộc tính; (TongTienGoc, GiamGia) → ThanhToanThucTe; (MaNV, NgayLap) → MaCN", "2NF", "Hai vế trái sau không phải siêu khóa nên vi phạm 3NF: ThanhToanThucTe là cột tính PERSISTED để làm đầu vào Loyalty và doanh thu (E5, RB09); MaCN là hệ quả của RB13 (một nhân viên tại một thời điểm chỉ ở một chi nhánh), giữ vì ERD có liên kết “lập tại” và báo cáo doanh thu theo chi nhánh."],
        ["CHI_TIET_HOA_DON", "(MaHD, SoThuTu)", "(MaHD, SoThuTu) → Loai, MaGoi, MaSP, SoLuong, DonGia, ThanhTien; (SoLuong, DonGia) → ThanhTien", "2NF", "ThanhTien phụ thuộc bắc cầu nên vi phạm 3NF; giữ dưới dạng cột tính PERSISTED (E5, RB10). Loai quyết định MaGoi hay MaSP có giá trị (RB07) là ràng buộc loại trừ trên NULL, không phải phụ thuộc hàm. DonGia là giá chốt, không phụ thuộc MaGoi/MaSP."],
        ["DANG_KY_GOI", "MaDK", "MaDK → mọi thuộc tính; (MaHD, SoThuTu) → MaGoi; MaHD → MaHV, MaCN; (MaGoi, NgayBatDau) → NgayKetThuc", "2NF", "Các vế trái (MaHD, SoThuTu), MaHD, (MaGoi, NgayBatDau) không phải siêu khóa vì một dòng chi tiết sinh SoLuong gói (RB08) nên vi phạm 3NF. Giữ có chủ đích (E3, E5): MaHV để xác thực check-in tìm gói theo hội viên không phải nối hóa đơn (RB16), MaCN để đối chiếu RB12 và RB30, NgayKetThuc để chỉ mục xác thực không nối GOI_DICH_VU (RB11)."],
        ["CHECK_IN", "MaCheckIn", "MaCheckIn → mọi thuộc tính; MaDK → MaHV; MaPhong → MaCN (khi MaPhong khác NULL)", "2NF", "Vi phạm 3NF có chủ đích (E3): MaHV lặp để tra lịch sử tập luyện và xác thực theo hội viên không phải nối DANG_KY_GOI (vấn đề 1, CN07), MaCN lặp để báo cáo lấp đầy theo chi nhánh; nhất quán bằng khóa ngoại phức hợp (RB17)."],
        ["LICH_HEN_PT", "MaLichHen", "MaLichHen → mọi thuộc tính; MaDK → MaHV; (MaHLV, NgayGioHen) → MaCN", "2NF", "Vi phạm 3NF có chủ đích (E3): MaHV lặp để tra lịch hẹn theo hội viên (RB18); theo RB21 một HLV tại một thời điểm thuộc một chi nhánh nên (MaHLV, NgayGioHen) → MaCN (không là khóa vì lịch 'Hủy' có thể trùng giờ). Giữ MaCN vì ERD có “diễn ra tại” và hoa hồng theo chi nhánh chỉ cần nhóm theo MaCN (vấn đề 5, RB25)."],
        ["DANH_GIA_PT", "MaDanhGia; MaLichHen", "Mỗi khóa → các thuộc tính còn lại", "BCNF", "MaLichHen là khóa dự tuyển nhờ UNIQUE (RB22)."],
        ["THONG_KE_CHECKIN", "(MaCN, Ngay, Gio)", "(MaCN, Ngay, Gio) → SoLuotVao, SoLuotRa", "BCNF", "Bảng dẫn xuất từ CHECK_IN (RB27)."],
        ["DOANH_THU_NGAY", "(MaCN, Ngay)", "(MaCN, Ngay) → TongTien, SoHoaDon", "BCNF", "Bảng dẫn xuất từ HOA_DON (RB28)."],
    ]
    assert [x[0] for x in r] == REL_ORDER
    for x in r:
        assert x[3] == NF[x[0]], x[0]
    o.append(table([1650, 1500, 2600, 850, 3038], ["Quan hệ", "Khóa", "Phụ thuộc hàm", "Dạng chuẩn", "Nhận xét"], [list(x) for x in r], sz=24))
    o.append(p("", after=100))
    return o


def nf_conclusion():
    nq = len(REL_ORDER)
    o = [h2("4.4 Kết luận dạng chuẩn của lược đồ")]
    o.append(p(f"Trong {nq} quan hệ, {N_BCNF} quan hệ đạt BCNF (trong đó HLV_CHUNG_CHI đạt cả 4NF) và {N_2NF} quan hệ chỉ đạt 2NF ({', '.join(LIST_2NF)}). Toàn bộ lược đồ đạt tối thiểu 2NF và 1NF (thuộc tính tổng hợp tách thành phần, thuộc tính đa trị tách thành quan hệ riêng)."))
    o.append(p(f"{N_2NF} quan hệ chưa đạt 3NF vì nhóm cố ý lưu dữ liệu suy ra được để giải quyết các vấn đề hiệu năng của đề, không phải do sơ suất thiết kế:", after=60, keep=True))
    for t in [
        "DIEM_LOYALTY.MaHang (TongChiTieuNam → MaHang): đọc hạng hiện tại và đếm phân bố hạng không phải so ngưỡng; thanh toán chỉ là một UPDATE theo khóa chính (vấn đề 4); nhất quán bằng RB04, RB06.",
        "HOA_DON.ThanhToanThucTe ((TongTienGoc, GiamGia) → ThanhToanThucTe) và HOA_DON.MaCN ((MaNV, NgayLap) → MaCN): đọc nhanh cho Loyalty và doanh thu theo chi nhánh (vấn đề 3, 4); nhất quán bằng RB09, RB13 (E5, E3).",
        "CHI_TIET_HOA_DON.ThanhTien ((SoLuong, DonGia) → ThanhTien): cột tính PERSISTED nên DBMS tự bảo đảm (RB10, E5).",
        "DANG_KY_GOI.MaHV, MaCN, MaGoi, NgayKetThuc (MaHD → MaHV, MaCN; (MaHD, SoThuTu) → MaGoi; (MaGoi, NgayBatDau) → NgayKetThuc): xác thực check-in theo hội viên không phải nối hóa đơn và gói ở đường găng giờ cao điểm (vấn đề 1); nhất quán bằng RB08, RB11, RB12.",
        "CHECK_IN.MaHV, MaCN (MaDK → MaHV; MaPhong → MaCN): tra cứu và báo cáo theo hội viên, chi nhánh không phải nối ở bảng ghi nhiều nhất (vấn đề 1, 3); nhất quán bằng khóa ngoại phức hợp (RB17).",
        "LICH_HEN_PT.MaHV, MaCN (MaDK → MaHV; (MaHLV, NgayGioHen) → MaCN): tra lịch theo hội viên và tính hoa hồng theo chi nhánh không phải nối khoảng thời gian với LICH_SU_DIEU_CHUYEN mỗi lần (vấn đề 5); nhất quán bằng RB18, RB21, RB25.",
    ]:
        o.append(bullet(t))
    o.append(p("Các dư thừa có chủ đích giữa nhiều bảng (E3) và cách giữ đồng nhất:", after=60, keep=True, bold=True))
    e3 = [
        ["CHECK_IN.MaHV = DANG_KY_GOI.MaHV", "Khóa ngoại phức hợp (MaDK, MaHV) → DANG_KY_GOI, cần UNIQUE (MaDK, MaHV)", "Khai báo", "RB17"],
        ["LICH_HEN_PT.MaHV = DANG_KY_GOI.MaHV", "Khóa ngoại phức hợp (MaDK, MaHV) → DANG_KY_GOI", "Khai báo", "RB18"],
        ["CHECK_IN.MaCN = PHONG.MaCN khi có phòng", "Khóa ngoại phức hợp (MaPhong, MaCN) → PHONG, cần UNIQUE (MaPhong, MaCN); MaPhong NULL thì không kiểm tra", "Khai báo", "RB17"],
        ["DANG_KY_GOI.MaGoi = CHI_TIET_HOA_DON.MaGoi", "Khóa ngoại phức hợp (MaHD, SoThuTu, MaGoi) → CHI_TIET_HOA_DON, cần UNIQUE (MaHD, SoThuTu, MaGoi)", "Khai báo", "RB08"],
        ["DANG_KY_GOI.MaHV, MaCN = HOA_DON.MaHV, MaCN", "Trigger AFTER INSERT/UPDATE (nối qua CHI_TIET_HOA_DON)", "Trigger", "RB12"],
        ["HOA_DON.MaCN = chi nhánh của HOA_DON.MaNV tại NgayLap", "Trigger tra LICH_SU_DIEU_CHUYEN", "Trigger", "RB13"],
        ["NHAN_VIEN.MaCN = MaCN của bản ghi đang mở ở LICH_SU_DIEU_CHUYEN", "Trigger khi điều chuyển, nghỉ việc", "Trigger", "RB24"],
    ]
    o.append(table([3000, 3600, 1300, 1738], ["Dư thừa", "Cách giữ đồng nhất", "Loại", "Mã"], e3))
    o.append(p("", after=60))
    o.append(p(f"CHECK_IN.MaCN không buộc bằng DANG_KY_GOI.MaCN vì đề cho hội viên tập tại bất kỳ chi nhánh nào. Bốn dư thừa đầu thực thi bằng khóa ngoại phức hợp nên không thể lệch; ba dư thừa còn lại cần trigger. Ngoài ra các cột lưu giá trị tổng hợp theo thời gian (DIEM_LOYALTY, DANG_KY_GOI.BuoiConLai, THONG_KE_CHECKIN, DOANH_THU_NGAY) được duy trì bằng thủ tục/trigger ở RB04, RB20, RB27, RB28. Nếu cần chuẩn hóa lên 3NF, chỉ việc bỏ các thuộc tính dư thừa và thay bằng view hoặc cột tính toán; giai đoạn 2 sẽ so sánh hiệu năng có/không áp dụng các thuộc tính này."))
    return o


def build():
    return mapping_rules() + logical_schema() + normal_forms() + nf_conclusion()
