# -*- coding: utf-8 -*-
"""NGUỒN DUY NHẤT của lược đồ quan hệ FitLife Hub (dẫn xuất từ ERD CSDLA_v3.png).

Mọi thứ khác (tài liệu LUOC_DO_CHUAN.md, hình PNG, file .drawio, script kiểm tra)
đều đọc từ file này, nên không thể lệch nhau.

Cột: (tên, kiểu SQL Server, NOT NULL?, cờ)
  cờ: P = khóa chính, F = tham gia một khóa ngoại, U = khóa thay thế / có UNIQUE
      (đánh dấu ◆ trên hình), D = thuộc tính dẫn xuất [x] trên ERD nhưng CÓ lưu
"""

GROUPS = {
    "dm": "Danh mục & chi nhánh",
    "hv": "Hội viên & loyalty",
    "goi": "Gói dịch vụ & hóa đơn",
    "sp": "Sản phẩm & tồn kho",
    "ns": "Nhân sự",
    "vh": "Vận hành (check-in, PT)",
}

# Hình mô-đun: tên -> (tiêu đề, [bảng của mô-đun])
MODULES = {
    "M1": ("Mô-đun 1 – Danh mục, chi nhánh, sản phẩm & tồn kho",
           ["LOAI_DICH_VU", "CHI_NHANH_DICH_VU", "CHI_NHANH", "PHONG", "GOI_DICH_VU",
            "SAN_PHAM", "TON_KHO"]),
    "M2": ("Mô-đun 2 – Hội viên, loyalty, gói đăng ký & hóa đơn",
           ["HANG_HOI_VIEN", "HOI_VIEN", "DIEM_LOYALTY", "HOA_DON", "CHI_TIET_HOA_DON",
            "DANG_KY_GOI"]),
    "M3": ("Mô-đun 3 – Nhân sự, lịch hẹn PT & check-in",
           ["NHAN_VIEN", "HUAN_LUYEN_VIEN", "HLV_CHUNG_CHI", "LICH_SU_DIEU_CHUYEN",
            "LICH_HEN_PT", "DANH_GIA_PT", "CHECK_IN"]),
}

NN, NL = True, False

# name: dict(grp, cols, ak, checks, idx, notes)
TABLES = {}


def table(name, grp, cols, ak=(), checks=(), idx=(), notes=()):
    TABLES[name] = dict(grp=grp, cols=list(cols), ak=list(ak), checks=list(checks),
                        idx=list(idx), notes=list(notes))


# ------------------------------------------------------------------ DANH MỤC & CHI NHÁNH
table("LOAI_DICH_VU", "dm", [
    ("MaLoai", "SMALLINT", NN, "P"),
    ("TenLoai", "NVARCHAR(50)", NN, "U"),
    ("MoTa", "NVARCHAR(255)", NL, ""),
], ak=["TenLoai"])

table("CHI_NHANH", "dm", [
    ("MaCN", "SMALLINT", NN, "P"),
    ("TenCN", "NVARCHAR(100)", NN, ""),
    ("SoNha", "NVARCHAR(30)", NN, ""),
    ("Duong", "NVARCHAR(100)", NN, ""),
    ("Quan", "NVARCHAR(50)", NN, ""),
    ("ThanhPho", "NVARCHAR(50)", NN, ""),
    ("SoDienThoai", "VARCHAR(15)", NN, "U"),
    ("GioMoCua", "TIME(0)", NN, ""),
    ("GioDongCua", "TIME(0)", NN, ""),
], ak=["SoDienThoai"],
    checks=["CK_CN_Gio: GioMoCua < GioDongCua (giả định chi nhánh không mở qua nửa đêm)"],
    notes=["DiaChi (tổng hợp) tách thành SoNha, Duong, Quan, ThanhPho"])

table("CHI_NHANH_DICH_VU", "dm", [
    ("MaCN", "SMALLINT", NN, "PF"),
    ("MaLoai", "SMALLINT", NN, "PF"),
    ("TrangThai", "NVARCHAR(20)", NN, ""),
], checks=["CK_CNDV_TrangThai: TrangThai IN (N'Hoạt động', N'Tạm ngưng')  [giá trị do nhóm đề xuất]"],
    notes=["N-N có thuộc tính: khóa ghép (MaCN, MaLoai)"])

table("PHONG", "dm", [
    ("MaPhong", "INT", NN, "P"),
    ("MaCN", "SMALLINT", NN, "F"),
    ("MaLoai", "SMALLINT", NN, "F"),
    ("TenPhong", "NVARCHAR(100)", NN, ""),
    ("SucChua", "SMALLINT", NN, ""),
    ("ConHoatDong", "BIT", NN, ""),
], checks=["CK_PHONG_SucChua: SucChua > 0"],
    idx=["UQ_PHONG_Phong_CN: UNIQUE (MaPhong, MaCN)  -- chỉ để làm đích của FK phức hợp từ CHECK_IN (E3)"])

table("GOI_DICH_VU", "goi", [
    ("MaGoi", "INT", NN, "P"),
    ("TenGoi", "NVARCHAR(100)", NN, ""),
    ("MaLoai", "SMALLINT", NN, "F"),
    ("ThoiHanThang", "SMALLINT", NN, ""),
    ("SoBuoi", "SMALLINT", NN, ""),
    ("GiaTien", "DECIMAL(12,0)", NN, ""),
    ("ConHieuLuc", "BIT", NN, ""),
], checks=["CK_GOI_ThoiHan: ThoiHanThang > 0",
           "CK_GOI_SoBuoi: SoBuoi >= 0   (0 = gói không có buổi PT)",
           "CK_GOI_Gia: GiaTien >= 0"])

table("SAN_PHAM", "sp", [
    ("MaSP", "INT", NN, "P"),
    ("TenSP", "NVARCHAR(150)", NN, ""),
    ("GiaBan", "DECIMAL(12,0)", NN, ""),
    ("Loai", "NVARCHAR(50)", NN, ""),
    ("DonViTinh", "NVARCHAR(20)", NN, ""),
    ("ConBan", "BIT", NN, ""),
], checks=["CK_SP_Gia: GiaBan >= 0"])

table("TON_KHO", "sp", [
    ("MaCN", "SMALLINT", NN, "PF"),
    ("MaSP", "INT", NN, "PF"),
    ("SoLuong", "INT", NN, ""),
    ("NgayCapNhat", "DATETIME2(0)", NN, ""),
], checks=["CK_TK_SoLuong: SoLuong >= 0"],
    notes=["N-N có thuộc tính: khóa ghép (MaCN, MaSP) – MaCN đứng trước vì truy vấn thường theo chi nhánh"])

# ------------------------------------------------------------------ HỘI VIÊN & LOYALTY
table("HANG_HOI_VIEN", "hv", [
    ("MaHang", "SMALLINT", NN, "P"),
    ("TenHang", "NVARCHAR(20)", NN, "U"),
    ("NguongChiTieu", "DECIMAL(15,0)", NN, ""),
], ak=["TenHang"],
    checks=["CK_HANG_Nguong: NguongChiTieu >= 0"],
    idx=["UQ_HANG_Nguong: UNIQUE (NguongChiTieu)  [đề xuất: để ánh xạ chi tiêu -> hạng xác định]"])

table("HOI_VIEN", "hv", [
    ("MaHV", "INT", NN, "P"),
    ("Ho", "NVARCHAR(50)", NN, ""),
    ("TenDem", "NVARCHAR(50)", NL, ""),
    ("Ten", "NVARCHAR(50)", NN, ""),
    ("SoDienThoai", "VARCHAR(15)", NN, "U"),
    ("Email", "VARCHAR(100)", NL, "U"),
    ("CCCD", "CHAR(12)", NL, "U"),
    ("GioiTinh", "NVARCHAR(3)", NN, ""),
    ("NgaySinh", "DATE", NN, ""),
    ("NgayDangKy", "DATE", NN, ""),
], ak=["SoDienThoai", "Email (filtered)", "CCCD (filtered)"],
    checks=["CK_HV_GioiTinh: GioiTinh IN (N'Nam', N'Nữ', N'Khác')",
            "CK_HV_NgaySinh: NgaySinh <= NgayDangKy"],
    idx=["UQ_HV_Email: UNIQUE (Email) WHERE Email IS NOT NULL",
         "UQ_HV_CCCD: UNIQUE (CCCD) WHERE CCCD IS NOT NULL"],
    notes=["HoTen (tổng hợp) tách thành Ho, TenDem, Ten",
           "[Tuoi] KHÔNG lưu (xem E5): tính bằng view/hàm từ NgaySinh"])

table("DIEM_LOYALTY", "hv", [
    ("MaHV", "INT", NN, "PF"),
    ("NamXet", "SMALLINT", NN, "P"),
    ("TongChiTieuNam", "DECIMAL(15,0)", NN, ""),
    ("DiemThuong", "INT", NN, ""),
    ("NgayCapNhat", "DATETIME2(0)", NN, ""),
    ("MaHang", "SMALLINT", NN, "F"),
], checks=["CK_DL_ChiTieu: TongChiTieuNam >= 0", "CK_DL_Diem: DiemThuong >= 0",
           "CK_DL_Nam: NamXet BETWEEN 2000 AND 2100"],
    notes=["Thực thể yếu của HOI_VIEN: khóa (MaHV, NamXet)",
           "Hạng hiện tại = MaHang của dòng NamXet = YEAR(GETDATE()); HOI_VIEN không có cột hạng (E1)"])

# ------------------------------------------------------------------ HÓA ĐƠN & GÓI
table("HOA_DON", "goi", [
    ("MaHD", "BIGINT", NN, "P"),
    ("NgayLap", "DATETIME2(0)", NN, ""),
    ("MaNV", "INT", NN, "F"),
    ("MaHV", "INT", NN, "F"),
    ("MaCN", "SMALLINT", NN, "F"),
    ("TongTienGoc", "DECIMAL(15,0)", NN, "D"),
    ("GiamGia", "DECIMAL(15,0)", NN, ""),
    ("ThanhToanThucTe", "DECIMAL(15,0)", NN, "D"),
    ("HinhThucThanhToan", "NVARCHAR(20)", NN, ""),
    ("TrangThai", "NVARCHAR(20)", NN, ""),
], checks=["CK_HD_HinhThuc: HinhThucThanhToan IN (N'Tiền mặt', N'VNPay', N'Thẻ')",
           "CK_HD_TrangThai: TrangThai IN (N'Đã thanh toán', N'Hủy')",
           "CK_HD_GiamGia: GiamGia >= 0 AND GiamGia <= TongTienGoc"],
    notes=["TongTienGoc: cột thường, thủ tục lập hóa đơn ghi = SUM(ThanhTien); trigger kiểm tra khớp (E5)",
           "ThanhToanThucTe: cột tính PERSISTED = TongTienGoc - GiamGia (E5)"])

table("CHI_TIET_HOA_DON", "goi", [
    ("MaHD", "BIGINT", NN, "PF"),
    ("SoThuTu", "SMALLINT", NN, "P"),
    ("Loai", "NVARCHAR(10)", NN, ""),
    ("MaGoi", "INT", NL, "F"),
    ("MaSP", "INT", NL, "F"),
    ("SoLuong", "INT", NN, ""),
    ("DonGia", "DECIMAL(12,0)", NN, ""),
    ("ThanhTien", "DECIMAL(15,0)", NN, "D"),
], checks=["CK_CT_Loai: Loai IN (N'Gói', N'Sản phẩm')",
           "CK_CT_XOR: (Loai = N'Gói' AND MaGoi IS NOT NULL AND MaSP IS NULL) OR "
           "(Loai = N'Sản phẩm' AND MaSP IS NOT NULL AND MaGoi IS NULL)",
           "CK_CT_SoLuong: SoLuong > 0", "CK_CT_DonGia: DonGia >= 0"],
    idx=["UQ_CT_HD_STT_Goi: UNIQUE (MaHD, SoThuTu, MaGoi)  -- đích của FK phức hợp từ DANG_KY_GOI (E3)"],
    notes=["Thực thể yếu của HOA_DON: khóa (MaHD, SoThuTu)",
           "ThanhTien: cột tính PERSISTED = SoLuong * DonGia (E5)",
           "DonGia là giá chốt tại thời điểm bán (không dẫn xuất từ GiaBan/GiaTien hiện tại)"])

table("DANG_KY_GOI", "goi", [
    ("MaDK", "BIGINT", NN, "P"),
    ("MaHV", "INT", NN, "F"),
    ("MaGoi", "INT", NN, "F"),
    ("MaCN", "SMALLINT", NN, "F"),
    ("MaHD", "BIGINT", NN, "F"),
    ("SoThuTu", "SMALLINT", NN, "F"),
    ("NgayBatDau", "DATE", NN, ""),
    ("NgayKetThuc", "DATE", NN, "D"),
    ("TrangThai", "NVARCHAR(20)", NN, ""),
    ("BuoiConLai", "SMALLINT", NN, ""),
], checks=["CK_DK_TrangThai: TrangThai IN (N'Hoạt động', N'Hết hạn', N'Hủy')",
           "CK_DK_Ngay: NgayKetThuc > NgayBatDau",
           "CK_DK_Buoi: BuoiConLai >= 0"],
    idx=["UQ_DK_DK_HV: UNIQUE (MaDK, MaHV)  -- đích của FK phức hợp từ CHECK_IN, LICH_HEN_PT (E3)",
         "IX_DK_XacThuc: (MaHV, TrangThai, NgayBatDau, NgayKetThuc) INCLUDE (MaDK, MaCN, BuoiConLai)  -- E10"],
    notes=["FK ghép (MaHD, SoThuTu) -> CHI_TIET_HOA_DON; số dòng DANG_KY_GOI của một dòng chi tiết = SoLuong (E4)",
           "NgayKetThuc = DATEADD(MONTH, GOI_DICH_VU.ThoiHanThang, NgayBatDau): lưu có chủ đích (E5, E7)",
           "Không có bảo lưu (E7)"])

# ------------------------------------------------------------------ NHÂN SỰ
table("NHAN_VIEN", "ns", [
    ("MaNV", "INT", NN, "P"),
    ("Ho", "NVARCHAR(50)", NN, ""),
    ("TenDem", "NVARCHAR(50)", NL, ""),
    ("Ten", "NVARCHAR(50)", NN, ""),
    ("SoDienThoai", "VARCHAR(15)", NL, "U"),
    ("ChucVu", "NVARCHAR(20)", NN, ""),
    ("LuongCoBan", "DECIMAL(12,0)", NN, ""),
    ("MaCN", "SMALLINT", NN, "F"),
    ("NgayVaoLam", "DATE", NN, ""),
    ("ConLamViec", "BIT", NN, ""),
], ak=["SoDienThoai (filtered)"],
    checks=["CK_NV_ChucVu: ChucVu IN (N'HLV', N'Lễ tân', N'Quản lý', N'Bán hàng')",
            "CK_NV_Luong: LuongCoBan >= 0"],
    idx=["UQ_NV_SDT: UNIQUE (SoDienThoai) WHERE SoDienThoai IS NOT NULL"],
    notes=["MaCN = chi nhánh hiện tại (quan hệ 'làm việc tại'); phải bằng MaCN của bản ghi đang mở "
           "trong LICH_SU_DIEU_CHUYEN (E6)"])

table("HUAN_LUYEN_VIEN", "ns", [
    ("MaHLV", "INT", NN, "PF"),
    ("ChuyenMon", "NVARCHAR(100)", NN, ""),
    ("HoaHongMoiBuoi", "DECIMAL(12,0)", NN, ""),
], checks=["CK_HLV_HoaHong: HoaHongMoiBuoi >= 0"],
    notes=["Chuyên biệt hóa partial, một lớp con (d/o không áp dụng); MaHLV vừa PK vừa FK -> NHAN_VIEN.MaNV",
           "Ràng buộc: NHAN_VIEN.ChucVu = N'HLV' <=> có dòng ở đây (trigger, E8)"])

table("HLV_CHUNG_CHI", "ns", [
    ("MaHLV", "INT", NN, "PF"),
    ("ChungChi", "NVARCHAR(150)", NN, "P"),
], notes=["Thuộc tính đa trị {ChungChi} của HUAN_LUYEN_VIEN: khóa ghép (MaHLV, ChungChi)"])

table("LICH_SU_DIEU_CHUYEN", "ns", [
    ("MaDieuChuyen", "INT", NN, "P"),
    ("MaNV", "INT", NN, "F"),
    ("MaCN", "SMALLINT", NN, "F"),
    ("NgayBatDau", "DATE", NN, ""),
    ("NgayKetThuc", "DATE", NL, ""),
    ("LyDo", "NVARCHAR(255)", NL, ""),
], ak=["(MaNV, NgayBatDau)"],
    checks=["CK_LS_Ngay: NgayKetThuc IS NULL OR NgayKetThuc >= NgayBatDau"],
    idx=["UQ_LS_NV_Bat: UNIQUE (MaNV, NgayBatDau)",
         "UQ_LS_NV_Mo: UNIQUE (MaNV) WHERE NgayKetThuc IS NULL  -- tối đa một bản ghi đang mở (E6)",
         "IX_LS_TraCuu: (MaNV, NgayBatDau) INCLUDE (NgayKetThuc, MaCN)  -- tra chi nhánh tại thời điểm t"],
    notes=["Khoảng [NgayBatDau, NgayKetThuc] đóng hai đầu, NULL = đang công tác; các khoảng của một NV "
           "liên tiếp, không chồng (trigger); bản ghi đầu tiên tạo khi vào làm (NgayBatDau = NgayVaoLam)"])

# ------------------------------------------------------------------ VẬN HÀNH
table("LICH_HEN_PT", "vh", [
    ("MaLichHen", "BIGINT", NN, "P"),
    ("MaHV", "INT", NN, "F"),
    ("MaHLV", "INT", NN, "F"),
    ("MaCN", "SMALLINT", NN, "F"),
    ("MaDK", "BIGINT", NN, "F"),
    ("NgayGioHen", "DATETIME2(0)", NN, ""),
    ("ThoiLuong", "SMALLINT", NN, ""),
    ("TrangThai", "NVARCHAR(20)", NN, ""),
], checks=["CK_LH_ThoiLuong: ThoiLuong = 60   (phút)",
           "CK_LH_Gio: DATEPART(MINUTE, NgayGioHen) = 0 AND DATEPART(SECOND, NgayGioHen) = 0",
           "CK_LH_TrangThai: TrangThai IN (N'Đã đặt', N'Đã hoàn thành', N'Hủy')"],
    idx=["UQ_LH_HLV_Gio: UNIQUE (MaHLV, NgayGioHen) WHERE TrangThai <> N'Hủy'  -- E2/E7",
         "UQ_LH_HV_Gio: UNIQUE (MaHV, NgayGioHen) WHERE TrangThai <> N'Hủy'  -- E2/E7"],
    notes=["Mọi lịch dài 60 phút, bắt đầu tròn giờ => hai lịch chồng nhau khi và chỉ khi trùng NgayGioHen, "
           "nên unique filtered index chặn tuyệt đối overbooking (E2/E7)"])

table("DANH_GIA_PT", "vh", [
    ("MaDanhGia", "BIGINT", NN, "P"),
    ("MaLichHen", "BIGINT", NN, "FU"),
    ("Diem", "TINYINT", NN, ""),
    ("NhanXet", "NVARCHAR(500)", NL, ""),
    ("NgayDanhGia", "DATETIME2(0)", NN, ""),
], ak=["MaLichHen"],
    checks=["CK_DG_Diem: Diem BETWEEN 1 AND 5"],
    idx=["UQ_DG_LichHen: UNIQUE (MaLichHen)  -- quan hệ 1 - (0..1) với LICH_HEN_PT"],
    notes=["Chỉ đánh giá được lịch có TrangThai = N'Đã hoàn thành' (trigger)"])

table("CHECK_IN", "vh", [
    ("MaCheckIn", "BIGINT", NN, "P"),
    ("MaHV", "INT", NN, "F"),
    ("MaCN", "SMALLINT", NN, "F"),
    ("MaPhong", "INT", NL, "F"),
    ("MaDK", "BIGINT", NN, "F"),
    ("ThoiGianVao", "DATETIME2(0)", NN, ""),
    ("ThoiGianRa", "DATETIME2(0)", NL, ""),
    ("ThietBi", "NVARCHAR(50)", NN, ""),
], checks=["CK_CI_Ra: ThoiGianRa IS NULL OR ThoiGianRa > ThoiGianVao"],
    idx=["UQ_CI_DangCoMat: UNIQUE (MaHV) WHERE ThoiGianRa IS NULL  -- tối đa một lượt chưa check-out (E10)"],
    notes=["ThietBi là chuỗi (cửa/thiết bị), không có thực thể THIET_BI; không tham gia xác thực, không cần chỉ mục"])

# thứ tự bảng khi in tài liệu
ORDER = ["LOAI_DICH_VU", "CHI_NHANH", "CHI_NHANH_DICH_VU", "PHONG", "GOI_DICH_VU", "SAN_PHAM", "TON_KHO",
         "HANG_HOI_VIEN", "HOI_VIEN", "DIEM_LOYALTY", "HOA_DON", "CHI_TIET_HOA_DON", "DANG_KY_GOI",
         "NHAN_VIEN", "HUAN_LUYEN_VIEN", "HLV_CHUNG_CHI", "LICH_SU_DIEU_CHUYEN",
         "LICH_HEN_PT", "DANH_GIA_PT", "CHECK_IN"]

# (bảng nguồn, [cột FK], bảng đích, [cột PK được tham chiếu], tên quan hệ trên ERD)
FKS = [
    ("CHI_NHANH_DICH_VU", ["MaCN"], "CHI_NHANH", ["MaCN"], "cung cấp"),
    ("CHI_NHANH_DICH_VU", ["MaLoai"], "LOAI_DICH_VU", ["MaLoai"], "được cung cấp"),
    ("PHONG", ["MaCN"], "CHI_NHANH", ["MaCN"], "có phòng"),
    ("PHONG", ["MaLoai"], "LOAI_DICH_VU", ["MaLoai"], "loại phòng"),
    ("GOI_DICH_VU", ["MaLoai"], "LOAI_DICH_VU", ["MaLoai"], "phân loại"),
    ("TON_KHO", ["MaSP"], "SAN_PHAM", ["MaSP"], "tồn kho"),
    ("TON_KHO", ["MaCN"], "CHI_NHANH", ["MaCN"], "lưu kho"),
    ("DIEM_LOYALTY", ["MaHV"], "HOI_VIEN", ["MaHV"], "tích lũy"),
    ("DIEM_LOYALTY", ["MaHang"], "HANG_HOI_VIEN", ["MaHang"], "xếp hạng"),
    ("HOA_DON", ["MaNV"], "NHAN_VIEN", ["MaNV"], "lập"),
    ("HOA_DON", ["MaHV"], "HOI_VIEN", ["MaHV"], "Thanh toán"),
    ("HOA_DON", ["MaCN"], "CHI_NHANH", ["MaCN"], "lập tại"),
    ("CHI_TIET_HOA_DON", ["MaHD"], "HOA_DON", ["MaHD"], "gồm (HOA_DON)"),
    ("CHI_TIET_HOA_DON", ["MaGoi"], "GOI_DICH_VU", ["MaGoi"], "gồm (GOI_DICH_VU)"),
    ("CHI_TIET_HOA_DON", ["MaSP"], "SAN_PHAM", ["MaSP"], "gồm (SAN_PHAM)"),
    ("DANG_KY_GOI", ["MaHV"], "HOI_VIEN", ["MaHV"], "đăng ký"),
    ("DANG_KY_GOI", ["MaGoi"], "GOI_DICH_VU", ["MaGoi"], "được đăng ký"),
    ("DANG_KY_GOI", ["MaCN"], "CHI_NHANH", ["MaCN"], "đăng ký tại"),
    ("DANG_KY_GOI", ["MaHD", "SoThuTu"], "CHI_TIET_HOA_DON", ["MaHD", "SoThuTu"], "xuất ra"),
    ("NHAN_VIEN", ["MaCN"], "CHI_NHANH", ["MaCN"], "làm việc tại"),
    ("HUAN_LUYEN_VIEN", ["MaHLV"], "NHAN_VIEN", ["MaNV"], "U (chuyên biệt hóa)"),
    ("HLV_CHUNG_CHI", ["MaHLV"], "HUAN_LUYEN_VIEN", ["MaHLV"], "{ChungChi} đa trị"),
    ("LICH_SU_DIEU_CHUYEN", ["MaNV"], "NHAN_VIEN", ["MaNV"], "được điều chuyển"),
    ("LICH_SU_DIEU_CHUYEN", ["MaCN"], "CHI_NHANH", ["MaCN"], "tiếp nhận"),
    ("LICH_HEN_PT", ["MaCN"], "CHI_NHANH", ["MaCN"], "diễn ra tại"),
    ("LICH_HEN_PT", ["MaHLV"], "HUAN_LUYEN_VIEN", ["MaHLV"], "phụ trách"),
    ("LICH_HEN_PT", ["MaHV"], "HOI_VIEN", ["MaHV"], "đặt lịch"),
    ("LICH_HEN_PT", ["MaDK"], "DANG_KY_GOI", ["MaDK"], "thuộc"),
    ("DANH_GIA_PT", ["MaLichHen"], "LICH_HEN_PT", ["MaLichHen"], "được đánh giá"),
    ("CHECK_IN", ["MaHV"], "HOI_VIEN", ["MaHV"], "check-in"),
    ("CHECK_IN", ["MaCN"], "CHI_NHANH", ["MaCN"], "ghi nhận tại"),
    ("CHECK_IN", ["MaPhong"], "PHONG", ["MaPhong"], "vào phòng"),
    ("CHECK_IN", ["MaDK"], "DANG_KY_GOI", ["MaDK"], "được dùng"),
]

# FK phức hợp THỰC THI ở mức vật lý để giữ dư thừa có chủ đích (E3). Không thêm mũi tên mới trên hình:
# mỗi cái thay cho FK đơn cùng tên ở FKS (cùng một mũi tên).
FK_VATLY = [
    ("DANG_KY_GOI", ["MaHD", "SoThuTu", "MaGoi"], "CHI_TIET_HOA_DON", ["MaHD", "SoThuTu", "MaGoi"],
     "DANG_KY_GOI.MaGoi phải trùng gói ở dòng chi tiết"),
    ("CHECK_IN", ["MaDK", "MaHV"], "DANG_KY_GOI", ["MaDK", "MaHV"], "CHECK_IN.MaHV = DANG_KY_GOI.MaHV"),
    ("LICH_HEN_PT", ["MaDK", "MaHV"], "DANG_KY_GOI", ["MaDK", "MaHV"], "LICH_HEN_PT.MaHV = DANG_KY_GOI.MaHV"),
    ("CHECK_IN", ["MaPhong", "MaCN"], "PHONG", ["MaPhong", "MaCN"],
     "CHECK_IN.MaCN = PHONG.MaCN khi có phòng (MaPhong NULL thì FK không kiểm tra)"),
]

# bảng dẫn xuất mức logic, KHÔNG thuộc ERD, không vẽ trên hình (giữ theo yêu cầu)
DERIVED_TABLES = {
    "THONG_KE_CHECKIN": [
        ("MaCN", "SMALLINT", NN, "PF"), ("Ngay", "DATE", NN, "P"), ("Gio", "TINYINT", NN, "P"),
        ("SoLuotVao", "INT", NN, ""), ("SoLuotRa", "INT", NN, ""),
    ],
    "DOANH_THU_NGAY": [
        ("MaCN", "SMALLINT", NN, "PF"), ("Ngay", "DATE", NN, "P"),
        ("TongTien", "DECIMAL(15,0)", NN, ""), ("SoHoaDon", "INT", NN, ""),
    ],
}
