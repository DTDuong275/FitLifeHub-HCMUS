"""Nội dung 30 ràng buộc toàn vẹn RB01–RB30 (mục 4.5). Mã, thứ tự và tên khớp model.RB và DBML."""

# Mỗi phần tử: code -> dict(loai, boi_canh, noi_dung [list đoạn], cai_dat [list đoạn], tam_anh_huong [(bảng, thêm, xóa, sửa)])
RBX = {}


def add(code, loai, boi_canh, noi_dung, cai_dat, impact):
    RBX[code] = dict(loai=loai, boi_canh=boi_canh, noi_dung=noi_dung, cai_dat=cai_dat, impact=impact)


add("RB01", "Miền giá trị (liên thuộc tính)", "CHI_NHANH",
    ["∀ cn ∈ CHI_NHANH: cn.GioMoCua < cn.GioDongCua (giả định chi nhánh không mở qua nửa đêm)"],
    ["CHECK CK_CN_Gio."],
    [("CHI_NHANH", "+", "-", "+ (GioMoCua, GioDongCua)")])

add("RB02", "Miền giá trị (CHECK thay cho ENUM)", "Mọi quan hệ có CHECK miền giá trị (liệt kê ở bảng tầm ảnh hưởng)",
    ["∀ dk ∈ DANG_KY_GOI: dk.TrangThai ∈ {'Hoạt động', 'Hết hạn', 'Hủy'} ∧ dk.NgayKetThuc > dk.NgayBatDau ∧ dk.BuoiConLai ≥ 0",
     "∀ lh ∈ LICH_HEN_PT: lh.TrangThai ∈ {'Đã đặt', 'Đã hoàn thành', 'Hủy'}",
     "∀ hd ∈ HOA_DON: hd.TrangThai ∈ {'Đã thanh toán', 'Hủy'} ∧ hd.HinhThucThanhToan ∈ {'Tiền mặt', 'VNPay', 'Thẻ'}",
     "∀ nv ∈ NHAN_VIEN: nv.ChucVu ∈ {'HLV', 'Lễ tân', 'Quản lý', 'Bán hàng'} ∧ nv.LuongCoBan ≥ 0",
     "∀ ct ∈ CHI_TIET_HOA_DON: ct.Loai ∈ {'Gói', 'Sản phẩm'} ∧ ct.SoLuong > 0 ∧ ct.DonGia ≥ 0",
     "∀ cd ∈ CHI_NHANH_DICH_VU: cd.TrangThai ∈ {'Hoạt động', 'Tạm ngưng'}",
     "∀ hv ∈ HOI_VIEN: hv.GioiTinh ∈ {'Nam', 'Nữ', 'Khác'} ∧ hv.NgaySinh ≤ hv.NgayDangKy",
     "∀ p ∈ PHONG: p.SucChua > 0; ∀ g ∈ GOI_DICH_VU: g.ThoiHanThang > 0 ∧ g.SoBuoi ≥ 0 ∧ g.GiaTien ≥ 0; ∀ sp ∈ SAN_PHAM: sp.GiaBan ≥ 0; ∀ tk ∈ TON_KHO: tk.SoLuong ≥ 0",
     "∀ h ∈ HANG_HOI_VIEN: h.NguongChiTieu ≥ 0; ∀ hlv ∈ HUAN_LUYEN_VIEN: hlv.HoaHongMoiBuoi ≥ 0",
     "∀ dl ∈ DIEM_LOYALTY: dl.TongChiTieuNam ≥ 0 ∧ dl.DiemThuong ≥ 0 ∧ dl.NamXet ∈ [2000, 2100]",
     "∀ ls ∈ LICH_SU_DIEU_CHUYEN: ls.NgayKetThuc IS NULL ∨ ls.NgayKetThuc ≥ ls.NgayBatDau; ∀ dg ∈ DANH_GIA_PT: dg.Diem ∈ [1, 5]; ∀ ci ∈ CHECK_IN: ci.ThoiGianRa IS NULL ∨ ci.ThoiGianRa > ci.ThoiGianVao"],
    ["SQL Server không có ENUM: mỗi tập giá trị cài bằng CHECK (cột IN (N'...')) (CK_DK_TrangThai, CK_LH_TrangThai, CK_HD_TrangThai, CK_HD_HinhThuc, CK_NV_ChucVu, CK_CT_Loai, CK_CNDV_TrangThai, CK_HV_GioiTinh); các miền số/ngày cài bằng CHECK cùng tên quy ước CK_<bảng>_<cột>.",
     "CHECK TON_KHO.SoLuong ≥ 0 là chốt chặn bán vượt tồn và trừ âm khi hủy hóa đơn."],
    [("DANG_KY_GOI", "+", "-", "+ (TrangThai, NgayBatDau, NgayKetThuc, BuoiConLai)"),
     ("LICH_HEN_PT", "+", "-", "+ (TrangThai)"),
     ("HOA_DON", "+", "-", "+ (TrangThai, HinhThucThanhToan)"),
     ("NHAN_VIEN", "+", "-", "+ (ChucVu, LuongCoBan)"),
     ("CHI_TIET_HOA_DON", "+", "-", "+ (Loai, SoLuong, DonGia)"),
     ("CHI_NHANH_DICH_VU", "+", "-", "+ (TrangThai)"),
     ("HOI_VIEN", "+", "-", "+ (GioiTinh, NgaySinh, NgayDangKy)"),
     ("PHONG", "+", "-", "+ (SucChua)"),
     ("GOI_DICH_VU", "+", "-", "+ (ThoiHanThang, SoBuoi, GiaTien)"),
     ("SAN_PHAM", "+", "-", "+ (GiaBan)"),
     ("TON_KHO", "+", "-", "+ (SoLuong)"),
     ("HANG_HOI_VIEN", "+", "-", "+ (NguongChiTieu)"),
     ("HUAN_LUYEN_VIEN", "+", "-", "+ (HoaHongMoiBuoi)"),
     ("DIEM_LOYALTY", "+", "-", "+ (TongChiTieuNam, DiemThuong, NamXet)"),
     ("LICH_SU_DIEU_CHUYEN", "+", "-", "+ (NgayBatDau, NgayKetThuc)"),
     ("DANH_GIA_PT", "+", "-", "+ (Diem)"),
     ("CHECK_IN", "+", "-", "+ (ThoiGianVao, ThoiGianRa)")])

add("RB03", "Liên bộ (duy nhất, có điều kiện với cột NULL)", "HOI_VIEN, NHAN_VIEN, CHI_NHANH, LOAI_DICH_VU, HANG_HOI_VIEN",
    ["∀ h1 ≠ h2 ∈ HOI_VIEN: h1.SoDienThoai ≠ h2.SoDienThoai ∧ (h1.Email IS NOT NULL ⇒ h1.Email ≠ h2.Email) ∧ (h1.CCCD IS NOT NULL ⇒ h1.CCCD ≠ h2.CCCD)",
     "∀ n1 ≠ n2 ∈ NHAN_VIEN: n1.SoDienThoai IS NOT NULL ⇒ n1.SoDienThoai ≠ n2.SoDienThoai",
     "TenLoai, TenHang, CHI_NHANH.SoDienThoai duy nhất (các khóa thay thế NOT NULL)"],
    ["Khóa thay thế NOT NULL dùng UNIQUE thường. Khóa thay thế cho phép NULL (Email, CCCD, SoDienThoai của nhân viên) dùng unique filtered index UQ_HV_Email, UQ_HV_CCCD, UQ_NV_SDT … WHERE cột IS NOT NULL; không dùng UNIQUE thường vì SQL Server chỉ cho một giá trị NULL."],
    [("HOI_VIEN", "+", "-", "+ (SoDienThoai, Email, CCCD)"),
     ("NHAN_VIEN", "+", "-", "+ (SoDienThoai)"),
     ("CHI_NHANH", "+", "-", "+ (SoDienThoai)"),
     ("LOAI_DICH_VU", "+", "-", "+ (TenLoai)"),
     ("HANG_HOI_VIEN", "+", "-", "+ (TenHang)")])

add("RB04", "Liên quan hệ (thống kê, theo thời gian)", "DIEM_LOYALTY, HOA_DON, HANG_HOI_VIEN",
    ["Với hóa đơn hd, đặt năm(hd) = YEAR(hd.NgayLap) và H(dl) = {hd ∈ HOA_DON : hd.MaHV = dl.MaHV ∧ năm(hd) = dl.NamXet ∧ hd.TrangThai = 'Đã thanh toán'}.",
     "∀ dl ∈ DIEM_LOYALTY: dl.TongChiTieuNam = Σ hd.ThanhToanThucTe (hd ∈ H(dl)) ∧ dl.DiemThuong = Σ ⌊hd.ThanhToanThucTe / 100.000⌋ (hd ∈ H(dl)) ∧ dl.MaHang = h.MaHang với h ∈ HANG_HOI_VIEN có NguongChiTieu lớn nhất thỏa h.NguongChiTieu ≤ dl.TongChiTieuNam"],
    ["Thanh toán hóa đơn là MỘT câu UPDATE theo khóa chính (MaHV, NamXet = YEAR(NgayLap)) WITH (UPDLOCK, HOLDLOCK): TongChiTieuNam += ThanhToanThucTe, DiemThuong += FLOOR(ThanhToanThucTe / 100000), MaHang = hạng có ngưỡng lớn nhất không vượt tổng mới, NgayCapNhat = hiện tại; không SUM lại hóa đơn cũ (vấn đề 4).",
     "Hủy hóa đơn trừ ngược đúng dòng của năm lập hóa đơn rồi tính lại hạng; CHECK ≥ 0 (RB02) chặn âm. Giả định: “tổng chi tiêu trong năm” của đề là năm dương lịch."],
    [("DIEM_LOYALTY", "+", "+", "+ (TongChiTieuNam, DiemThuong, MaHang)"),
     ("HOA_DON", "+", "-", "+ (ThanhToanThucTe, TrangThai, MaHV, NgayLap)"),
     ("HANG_HOI_VIEN", "-", "+", "+ (NguongChiTieu)")])

add("RB05", "Liên quan hệ (theo thời gian)", "HOI_VIEN, DIEM_LOYALTY, HANG_HOI_VIEN",
    ["∀ hv ∈ HOI_VIEN: ∃ dl ∈ DIEM_LOYALTY: dl.MaHV = hv.MaHV ∧ dl.NamXet = YEAR(GETDATE())",
     "Dòng mới tạo có dl.TongChiTieuNam = 0 ∧ dl.DiemThuong = 0 ∧ dl.MaHang = h.MaHang với h.NguongChiTieu = 0 (Silver)"],
    ["Thủ tục đăng ký hội viên tạo dòng của năm hiện tại trong cùng giao dịch với HOI_VIEN; job 0h ngày 1/1 tạo sẵn dòng năm mới cho mọi hội viên. Hạng hiện tại = MaHang của dòng NamXet = YEAR(GETDATE()); HOI_VIEN không có cột hạng. Hệ quả: hạng về Silver mỗi 1/1 (phương án dự phòng 12 tháng trượt: đổi NamXet thành NamThang)."],
    [("HOI_VIEN", "+", "-", "-"),
     ("DIEM_LOYALTY", "-", "+", "-"),
     ("HANG_HOI_VIEN", "-", "+", "+ (NguongChiTieu)")])

add("RB06", "Liên bộ", "HANG_HOI_VIEN",
    ["∀ h1 ≠ h2 ∈ HANG_HOI_VIEN: h1.NguongChiTieu ≠ h2.NguongChiTieu; ∃! h ∈ HANG_HOI_VIEN: h.NguongChiTieu = 0 (hạng thấp nhất, Silver)"],
    ["UNIQUE UQ_HANG_Nguong (NguongChiTieu); mọi mức chi tiêu ≥ 0 đều có đúng một hạng. Đây là ràng buộc nhóm đề xuất, không có trên ERD."],
    [("HANG_HOI_VIEN", "+", "+", "+ (NguongChiTieu)")])

add("RB07", "Liên thuộc tính", "CHI_TIET_HOA_DON",
    ["∀ ct ∈ CHI_TIET_HOA_DON: (ct.Loai = 'Gói' ∧ ct.MaGoi IS NOT NULL ∧ ct.MaSP IS NULL) ∨ (ct.Loai = 'Sản phẩm' ∧ ct.MaSP IS NOT NULL ∧ ct.MaGoi IS NULL)"],
    ["CHECK CK_CT_XOR. Khóa ngoại MaGoi, MaSP cho phép NULL theo bản số 0..1 của hai liên kết “gồm”."],
    [("CHI_TIET_HOA_DON", "+", "-", "+ (Loai, MaGoi, MaSP)")])

add("RB08", "Liên quan hệ (đồng nhất giá trị, bản số)", "DANG_KY_GOI, CHI_TIET_HOA_DON",
    ["∀ ct ∈ CHI_TIET_HOA_DON, ct.Loai = 'Gói': |{dk ∈ DANG_KY_GOI : dk.MaHD = ct.MaHD ∧ dk.SoThuTu = ct.SoThuTu}| = ct.SoLuong ∧ mọi dk trong tập đó có dk.MaGoi = ct.MaGoi",
     "∀ dk ∈ DANG_KY_GOI: ∃ ct ∈ CHI_TIET_HOA_DON: ct.MaHD = dk.MaHD ∧ ct.SoThuTu = dk.SoThuTu ∧ ct.Loai = 'Gói'",
     "Liên kết “xuất ra” là 0..N ở phía DANG_KY_GOI vì SoLuong có thể lớn hơn 1, nên khóa ngoại ghép (MaHD, SoThuTu) không có UNIQUE."],
    ["Khóa ngoại phức hợp (MaHD, SoThuTu, MaGoi) → CHI_TIET_HOA_DON, đích UNIQUE UQ_CT_HD_STT_Goi: buộc MaGoi trùng và chặn tham chiếu tới dòng sản phẩm (MaGoi NULL).",
     "Số gói bằng SoLuong: trigger AFTER INSERT chặn vượt SoLuong; thủ tục lập hóa đơn sinh đủ SoLuong bản ghi trong cùng giao dịch và kiểm tra bằng nhau trước COMMIT (CHECK không đếm được dòng khác)."],
    [("DANG_KY_GOI", "+", "+", "+ (MaHD, SoThuTu, MaGoi)"),
     ("CHI_TIET_HOA_DON", "+", "+", "+ (Loai, SoLuong, MaGoi, MaHD, SoThuTu)")])

add("RB09", "Liên quan hệ (thống kê, dữ liệu dẫn xuất)", "HOA_DON, CHI_TIET_HOA_DON",
    ["∀ hd ∈ HOA_DON: hd.TongTienGoc = Σ ct.ThanhTien (ct.MaHD = hd.MaHD) ∧ 0 ≤ hd.GiamGia ≤ hd.TongTienGoc ∧ hd.ThanhToanThucTe = hd.TongTienGoc − hd.GiamGia"],
    ["TongTienGoc là cột thường (vượt quan hệ nên không dùng được cột tính): thủ tục lập hóa đơn ghi, trigger trên CHI_TIET_HOA_DON kiểm tra khớp. ThanhToanThucTe là cột tính PERSISTED. CHECK CK_HD_GiamGia. Vi phạm 3NF có chủ đích (E5)."],
    [("HOA_DON", "+", "-", "+ (TongTienGoc, GiamGia)"),
     ("CHI_TIET_HOA_DON", "+", "+", "+ (SoLuong, DonGia, MaHD)")])

add("RB10", "Liên quan hệ (dữ liệu dẫn xuất, theo thời gian)", "CHI_TIET_HOA_DON, GOI_DICH_VU, SAN_PHAM",
    ["∀ ct ∈ CHI_TIET_HOA_DON: ct.ThanhTien = ct.SoLuong × ct.DonGia",
     "Khi thêm ct: (ct.Loai = 'Gói' ⇒ ct.DonGia = GOI_DICH_VU(ct.MaGoi).GiaTien ∧ ConHieuLuc = 1) ∧ (ct.Loai = 'Sản phẩm' ⇒ ct.DonGia = SAN_PHAM(ct.MaSP).GiaBan ∧ ConBan = 1); ct.DonGia không đổi sau khi lập hóa đơn"],
    ["ThanhTien là cột tính PERSISTED. DonGia là giá chốt tại lúc bán nên không dẫn xuất từ GiaTien/GiaBan hiện tại; trigger chặn sửa DonGia của hóa đơn đã lập."],
    [("CHI_TIET_HOA_DON", "+", "-", "+ (SoLuong, DonGia)"),
     ("GOI_DICH_VU", "-", "-", "-"),
     ("SAN_PHAM", "-", "-", "-")])

add("RB11", "Liên quan hệ (dữ liệu dẫn xuất, theo thời gian)", "DANG_KY_GOI, GOI_DICH_VU",
    ["Khi thêm dk ∈ DANG_KY_GOI: dk.NgayKetThuc = dk.NgayBatDau + GOI_DICH_VU(dk.MaGoi).ThoiHanThang tháng; dk.TrangThai ∈ {'Hoạt động', 'Hết hạn', 'Hủy'} (không có bảo lưu)",
     "Về sau dk.NgayKetThuc không đổi khi GOI_DICH_VU.ThoiHanThang thay đổi"],
    ["NgayKetThuc lưu có chủ đích, cột thường do thủ tục đăng ký ghi (phụ thuộc bảng khác), để IX_DK_XacThuc không phải nối GOI_DICH_VU. Vi phạm 3NF có chủ đích (E5, E7)."],
    [("DANG_KY_GOI", "+", "-", "+ (NgayBatDau, NgayKetThuc, MaGoi)"),
     ("GOI_DICH_VU", "-", "-", "-")])

add("RB12", "Liên quan hệ (đồng nhất giá trị)", "DANG_KY_GOI, HOA_DON, CHI_TIET_HOA_DON",
    ["∀ dk ∈ DANG_KY_GOI, hd = HOA_DON(dk.MaHD): dk.MaHV = hd.MaHV ∧ dk.MaCN = hd.MaCN ∧ (hd.TrangThai = 'Hủy' ⇒ dk.TrangThai = 'Hủy')"],
    ["Trigger AFTER INSERT/UPDATE trên DANG_KY_GOI và HOA_DON (nối qua CHI_TIET_HOA_DON); thủ tục hủy hóa đơn chuyển các DANG_KY_GOI của hóa đơn sang 'Hủy'."],
    [("DANG_KY_GOI", "+", "-", "+ (MaHD, MaHV, MaCN, TrangThai)"),
     ("HOA_DON", "-", "-", "+ (MaHV, MaCN, TrangThai)")])

add("RB13", "Liên quan hệ (theo thời gian)", "HOA_DON, NHAN_VIEN, LICH_SU_DIEU_CHUYEN",
    ["∀ hd ∈ HOA_DON: ∃ ls ∈ LICH_SU_DIEU_CHUYEN: ls.MaNV = hd.MaNV ∧ ls.MaCN = hd.MaCN ∧ ls.NgayBatDau ≤ ngày(hd.NgayLap) ∧ (ls.NgayKetThuc IS NULL ∨ ngày(hd.NgayLap) ≤ ls.NgayKetThuc)"],
    ["Trigger AFTER INSERT/UPDATE trên HOA_DON tra LICH_SU_DIEU_CHUYEN theo chỉ mục IX_LS_TraCuu."],
    [("HOA_DON", "+", "-", "+ (MaNV, MaCN, NgayLap)"),
     ("LICH_SU_DIEU_CHUYEN", "-", "+", "+ (MaCN, NgayBatDau, NgayKetThuc)")])

add("RB14", "Liên quan hệ (bản số)", "HOA_DON, CHI_TIET_HOA_DON",
    ["∀ hd ∈ HOA_DON: ∃ ct ∈ CHI_TIET_HOA_DON: ct.MaHD = hd.MaHD (bản số 1..N của “gồm”)"],
    ["Phần đầu hóa đơn được ghi trước các dòng nên ràng buộc kiểm tra ở cuối giao dịch lập hóa đơn (SQL Server không có ràng buộc trì hoãn)."],
    [("HOA_DON", "+", "-", "-"),
     ("CHI_TIET_HOA_DON", "-", "+", "+ (MaHD)")])

add("RB15", "Liên bộ (duy nhất, có điều kiện)", "CHECK_IN",
    ["∀ hv ∈ HOI_VIEN: |{ci ∈ CHECK_IN : ci.MaHV = hv.MaHV ∧ ci.ThoiGianRa IS NULL}| ≤ 1"],
    ["Unique filtered index UQ_CI_DangCoMat (MaHV) WHERE ThoiGianRa IS NULL, chặn quét trùng. Lưu ý vật lý: nếu phân vùng CHECK_IN theo ThoiGianVao thì chỉ mục này không chứa cột phân vùng nên không aligned; phương án thay là kiểm tra trong thủ tục check-in với UPDLOCK (quyết định ở giai đoạn 2)."],
    [("CHECK_IN", "+", "-", "+ (MaHV, ThoiGianRa)")])

add("RB16", "Liên quan hệ (theo thời gian, hiệu năng)", "CHECK_IN, DANG_KY_GOI",
    ["Khi thêm ci ∈ CHECK_IN, dk = DANG_KY_GOI(ci.MaDK): dk.MaHV = ci.MaHV ∧ dk.TrangThai = 'Hoạt động' ∧ dk.NgayBatDau ≤ ngày(ci.ThoiGianVao) ≤ dk.NgayKetThuc. Ràng buộc chỉ xét lúc ghi nên thay đổi gói về sau không làm lượt cũ vi phạm",
     "Xác thực và ghi log mất dưới 50 ms (vấn đề 1)"],
    ["Chỉ mục IX_DK_XacThuc (MaHV, TrangThai, NgayBatDau, NgayKetThuc) INCLUDE (MaDK, MaCN, BuoiConLai): một lần seek theo MaHV ra đúng gói còn hạn; INSERT vào CHECK_IN chỉ cần khóa chính. CHECK_IN.ThietBi là chuỗi, không tham gia xác thực nên không cần chỉ mục."],
    [("CHECK_IN", "+", "-", "+ (MaDK, MaHV, ThoiGianVao)"),
     ("DANG_KY_GOI", "-", "-", "-")])

add("RB17", "Liên quan hệ (đồng nhất giá trị)", "CHECK_IN, DANG_KY_GOI, PHONG",
    ["∀ ci ∈ CHECK_IN: ci.MaHV = DANG_KY_GOI(ci.MaDK).MaHV ∧ (ci.MaPhong IS NOT NULL ⇒ ci.MaCN = PHONG(ci.MaPhong).MaCN)",
     "Không có ràng buộc ci.MaCN = DANG_KY_GOI(ci.MaDK).MaCN vì hội viên được tập tại bất kỳ chi nhánh nào"],
    ["Khóa ngoại phức hợp (MaDK, MaHV) → DANG_KY_GOI (đích UQ_DK_DK_HV) và (MaPhong, MaCN) → PHONG (đích UQ_PHONG_Phong_CN); khi MaPhong NULL SQL Server bỏ qua kiểm tra, đúng ý nghĩa 0..1."],
    [("CHECK_IN", "+", "-", "+ (MaHV, MaDK, MaCN, MaPhong)"),
     ("DANG_KY_GOI", "-", "-", "+ (MaHV)"),
     ("PHONG", "-", "-", "+ (MaCN)")])

add("RB18", "Liên quan hệ (đồng nhất giá trị)", "LICH_HEN_PT, DANG_KY_GOI",
    ["∀ lh ∈ LICH_HEN_PT: lh.MaHV = DANG_KY_GOI(lh.MaDK).MaHV"],
    ["Khóa ngoại phức hợp (MaDK, MaHV) → DANG_KY_GOI (đích UQ_DK_DK_HV)."],
    [("LICH_HEN_PT", "+", "-", "+ (MaHV, MaDK)"),
     ("DANG_KY_GOI", "-", "-", "+ (MaHV)")])

add("RB19", "Liên bộ (có điều kiện) / miền giá trị", "LICH_HEN_PT",
    ["∀ lh ∈ LICH_HEN_PT: lh.ThoiLuong = 60 ∧ MINUTE(lh.NgayGioHen) = 0 ∧ SECOND(lh.NgayGioHen) = 0",
     "∀ lh1 ≠ lh2, cả hai có TrangThai ≠ 'Hủy': lh1.NgayGioHen = lh2.NgayGioHen ⇒ lh1.MaHLV ≠ lh2.MaHLV ∧ lh1.MaHV ≠ lh2.MaHV",
     "Vì mọi lịch dài 60 phút và bắt đầu tròn giờ, hai lịch chồng khoảng thời gian khi và chỉ khi trùng NgayGioHen, nên điều kiện trên tương đương không có overbooking"],
    ["CHECK CK_LH_ThoiLuong (= 60) và CK_LH_Gio; unique filtered index UQ_LH_HLV_Gio (MaHLV, NgayGioHen) và UQ_LH_HV_Gio (MaHV, NgayGioHen) đều WHERE TrangThai <> N'Hủy'. Thủ tục đặt lịch bắt lỗi 2601/2627 và trả “khung giờ đã có người đặt”. Nếu sau này ThoiLuong nhận nhiều giá trị (30/60/90) phải thêm trigger kiểm tra chồng khoảng NgayGioHen < kết thúc của lịch kia và kết thúc > NgayGioHen, có UPDLOCK."],
    [("LICH_HEN_PT", "+", "-", "+ (MaHLV, MaHV, NgayGioHen, ThoiLuong, TrangThai)")])

add("RB20", "Liên quan hệ (thống kê)", "LICH_HEN_PT, DANG_KY_GOI, GOI_DICH_VU",
    ["∀ dk ∈ DANG_KY_GOI: |{lh ∈ LICH_HEN_PT : lh.MaDK = dk.MaDK ∧ lh.TrangThai = 'Đã đặt'}| ≤ dk.BuoiConLai",
     "Khi đặt lh: dk.TrangThai = 'Hoạt động' ∧ dk.NgayBatDau ≤ ngày(lh.NgayGioHen) ≤ dk.NgayKetThuc ∧ GOI_DICH_VU(dk.MaGoi).SoBuoi > 0",
     "∀ dk có g = GOI_DICH_VU(dk.MaGoi), g.SoBuoi > 0: dk.BuoiConLai = g.SoBuoi − |{lh ∈ LICH_HEN_PT : lh.MaDK = dk.MaDK ∧ lh.TrangThai = 'Đã hoàn thành'}|"],
    ["Thủ tục đặt lịch khóa dòng DANG_KY_GOI bằng UPDLOCK rồi đếm lịch 'Đã đặt' trong cùng giao dịch để hai giao dịch đồng thời không cùng vượt; hoàn thành lịch trừ BuoiConLai (CHECK ≥ 0)."],
    [("LICH_HEN_PT", "+", "+", "+ (MaDK, NgayGioHen, TrangThai)"),
     ("DANG_KY_GOI", "-", "-", "+ (BuoiConLai, MaGoi, TrangThai)")])

add("RB21", "Liên quan hệ (theo thời gian)", "LICH_HEN_PT, LICH_SU_DIEU_CHUYEN, CHI_NHANH",
    ["∀ lh ∈ LICH_HEN_PT: ∃ ls ∈ LICH_SU_DIEU_CHUYEN: ls.MaNV = lh.MaHLV ∧ ls.MaCN = lh.MaCN ∧ ls.NgayBatDau ≤ ngày(lh.NgayGioHen) ∧ (ls.NgayKetThuc IS NULL ∨ ngày(lh.NgayGioHen) ≤ ls.NgayKetThuc)",
     "Giờ hẹn nằm trong giờ mở cửa: CHI_NHANH(lh.MaCN).GioMoCua ≤ giờ(lh.NgayGioHen) ∧ giờ(lh.NgayGioHen) + 60 phút ≤ GioDongCua"],
    ["Thủ tục đặt lịch tra LICH_SU_DIEU_CHUYEN theo IX_LS_TraCuu (MaNV, NgayBatDau) INCLUDE (NgayKetThuc, MaCN) và đọc CHI_NHANH; kiểm tra giờ mở cửa làm trong thủ tục vì CHECK không tra được bảng khác. Độ mịn của lịch sử điều chuyển là ngày."],
    [("LICH_HEN_PT", "+", "-", "+ (MaHLV, MaCN, NgayGioHen)"),
     ("LICH_SU_DIEU_CHUYEN", "-", "+", "+ (MaCN, NgayBatDau, NgayKetThuc)"),
     ("CHI_NHANH", "-", "-", "+ (GioMoCua, GioDongCua)")])

add("RB22", "Liên quan hệ (bản số 1 – 0..1, theo trạng thái)", "DANH_GIA_PT, LICH_HEN_PT",
    ["∀ dg ∈ DANH_GIA_PT, lh = LICH_HEN_PT(dg.MaLichHen): lh.TrangThai = 'Đã hoàn thành' ∧ dg.NgayDanhGia ≥ lh.NgayGioHen",
     "∀ dg1 ≠ dg2 ∈ DANH_GIA_PT: dg1.MaLichHen ≠ dg2.MaLichHen"],
    ["UNIQUE UQ_DG_LichHen (MaLichHen) cho bản số 1 – (0..1); trigger kiểm tra trạng thái lịch lúc thêm đánh giá; CHECK Diem ∈ [1, 5] ở RB02."],
    [("DANH_GIA_PT", "+", "-", "+ (MaLichHen, NgayDanhGia)"),
     ("LICH_HEN_PT", "-", "+", "+ (TrangThai, NgayGioHen)")])

add("RB23", "Liên bộ / liên quan hệ (theo thời gian)", "LICH_SU_DIEU_CHUYEN, NHAN_VIEN",
    ["∀ nv ∈ NHAN_VIEN: tập bản ghi ls ∈ LICH_SU_DIEU_CHUYEN có ls.MaNV = nv.MaNV khác rỗng (bản số 1..N); xếp theo NgayBatDau thì bản ghi đầu có NgayBatDau = nv.NgayVaoLam và LyDo = 'Vào làm'; bản ghi sau bắt đầu đúng một ngày sau NgayKetThuc của bản ghi trước (liên tiếp, không hở, không chồng)",
     "Mỗi nv có tối đa một ls có NgayKetThuc IS NULL"],
    ["UNIQUE UQ_LS_NV_Bat (MaNV, NgayBatDau); unique filtered index UQ_LS_NV_Mo (MaNV) WHERE NgayKetThuc IS NULL; trigger kiểm tra liên tiếp/không chồng. Điều chuyển = đóng bản ghi cũ và mở bản ghi mới trong một giao dịch. Khoảng [NgayBatDau, NgayKetThuc] đóng hai đầu, độ mịn theo ngày."],
    [("LICH_SU_DIEU_CHUYEN", "+", "+", "+ (MaNV, NgayBatDau, NgayKetThuc)"),
     ("NHAN_VIEN", "+", "-", "+ (NgayVaoLam)")])

add("RB24", "Liên quan hệ (đồng nhất giá trị)", "NHAN_VIEN, LICH_SU_DIEU_CHUYEN",
    ["∀ nv ∈ NHAN_VIEN, nv.ConLamViec = 1: ∃! ls ∈ LICH_SU_DIEU_CHUYEN: ls.MaNV = nv.MaNV ∧ ls.NgayKetThuc IS NULL ∧ ls.MaCN = nv.MaCN",
     "∀ nv, nv.ConLamViec = 0: không tồn tại ls có ls.MaNV = nv.MaNV ∧ ls.NgayKetThuc IS NULL"],
    ["Trigger khi điều chuyển và nghỉ việc; nghỉ việc đóng bản ghi đang mở. Dư thừa có chủ đích giữa hai quan hệ “làm việc tại” và “được điều chuyển” (E6), không phải phụ thuộc hàm trong một quan hệ."],
    [("NHAN_VIEN", "+", "-", "+ (MaCN, ConLamViec)"),
     ("LICH_SU_DIEU_CHUYEN", "+", "+", "+ (MaNV, MaCN, NgayKetThuc)")])

add("RB25", "Liên quan hệ (thống kê, theo thời gian)", "LICH_HEN_PT, LICH_SU_DIEU_CHUYEN, HUAN_LUYEN_VIEN",
    ["∀ hlv, cn, tháng t: HoaHong(hlv, cn, t) = hlv.HoaHongMoiBuoi × |{lh ∈ LICH_HEN_PT : lh.MaHLV = hlv.MaHLV ∧ lh.TrangThai = 'Đã hoàn thành' ∧ lh.NgayGioHen thuộc t ∧ ∃ ls ∈ LICH_SU_DIEU_CHUYEN: ls.MaNV = lh.MaHLV ∧ ls.MaCN = cn ∧ ls.NgayBatDau ≤ ngày(lh.NgayGioHen) ≤ ISNULL(ls.NgayKetThuc, '9999-12-31')}|",
     "Chi nhánh để tính hoa hồng là chi nhánh của giai đoạn tại thời điểm tập, không phải NHAN_VIEN.MaCN hiện tại"],
    ["Truy vấn nối LICH_HEN_PT (Đã hoàn thành) với LICH_SU_DIEU_CHUYEN theo IX_LS_TraCuu, nhóm theo LICH_SU_DIEU_CHUYEN.MaCN. Nhờ RB21 có lh.MaCN = ls.MaCN nên cũng có thể nhóm thẳng theo LICH_HEN_PT.MaCN bằng chỉ mục IX_LH_HoaHong (vấn đề 5)."],
    [("LICH_HEN_PT", "+", "-", "+ (MaHLV, MaCN, NgayGioHen, TrangThai)"),
     ("LICH_SU_DIEU_CHUYEN", "+", "+", "+ (MaCN, NgayBatDau, NgayKetThuc)"),
     ("HUAN_LUYEN_VIEN", "-", "-", "+ (HoaHongMoiBuoi)")])

add("RB26", "Liên quan hệ (chuyên biệt hóa)", "NHAN_VIEN, HUAN_LUYEN_VIEN",
    ["∀ nv ∈ NHAN_VIEN: nv.ChucVu = 'HLV' ⇔ ∃ hlv ∈ HUAN_LUYEN_VIEN: hlv.MaHLV = nv.MaNV",
     "Không cho đổi ChucVu khỏi 'HLV' nếu HLV còn lịch hẹn hoặc lịch sử điều chuyển"],
    ["Chuyên biệt hóa partial, một lớp con, d/o không áp dụng. Trigger trên NHAN_VIEN và HUAN_LUYEN_VIEN; MaHLV vừa là khóa chính vừa là khóa ngoại tới NHAN_VIEN.MaNV."],
    [("NHAN_VIEN", "+", "-", "+ (ChucVu)"),
     ("HUAN_LUYEN_VIEN", "+", "+", "+ (MaHLV)")])

add("RB27", "Liên quan hệ (thống kê, dữ liệu dẫn xuất)", "THONG_KE_CHECKIN, CHECK_IN, PHONG",
    ["∀ t ∈ THONG_KE_CHECKIN: t.SoLuotVao = |{ci ∈ CHECK_IN : ci.MaCN = t.MaCN ∧ ngày(ci.ThoiGianVao) = t.Ngay ∧ giờ(ci.ThoiGianVao) = t.Gio}| ∧ t.SoLuotRa = |{ci ∈ CHECK_IN : ci.MaCN = t.MaCN ∧ ngày(ci.ThoiGianRa) = t.Ngay ∧ giờ(ci.ThoiGianRa) = t.Gio}|",
     "Số người đang có mặt tại chi nhánh cn lúc t: CoMat(cn, t) = |{ci ∈ CHECK_IN : ci.MaCN = cn ∧ ci.ThoiGianVao ≤ t ∧ (ci.ThoiGianRa IS NULL ∨ t < ci.ThoiGianRa)}| = Σ (SoLuotVao − SoLuotRa) cộng dồn từ giờ 0 của ngày đến giờ của t",
     "TyLeLapDay(cn, t) = CoMat(cn, t) / Σ {p.SucChua : p ∈ PHONG, p.MaCN = cn ∧ p.ConHoatDong = 1}"],
    ["“Số lượt vào” khác “số người đang có mặt”: phải trừ lượt đã ra. Trigger/job cập nhật THONG_KE_CHECKIN từ CHECK_IN (vào: +1 ở giờ ThoiGianVao; ra: +1 ở giờ ThoiGianRa); job cuối ngày đóng các lượt chưa check-out lúc GioDongCua để cộng dồn không rò sang ngày sau. Lượt không có MaPhong vẫn tính vào tử số cấp chi nhánh; mẫu số dùng SucChua hiện tại của phòng hoạt động (chỉ mục IX_PHONG_CN)."],
    [("THONG_KE_CHECKIN", "+", "+", "+ (SoLuotVao, SoLuotRa)"),
     ("CHECK_IN", "+", "+", "+ (MaCN, ThoiGianVao, ThoiGianRa)"),
     ("PHONG", "-", "-", "+ (SucChua, ConHoatDong)")])

add("RB28", "Liên quan hệ (thống kê, dữ liệu dẫn xuất)", "DOANH_THU_NGAY, HOA_DON",
    ["∀ d ∈ DOANH_THU_NGAY: d.TongTien = Σ hd.ThanhToanThucTe ∧ d.SoHoaDon = |{hd}| với hd ∈ HOA_DON, hd.MaCN = d.MaCN ∧ ngày(hd.NgayLap) = d.Ngay ∧ hd.TrangThai = 'Đã thanh toán'"],
    ["Cập nhật bằng trigger hoặc job cuối ngày; hủy hóa đơn trừ ngược đúng ngày lập. Doanh thu tháng/quý/năm = SUM theo Ngay."],
    [("DOANH_THU_NGAY", "+", "+", "+ (TongTien, SoHoaDon)"),
     ("HOA_DON", "+", "+", "+ (MaCN, NgayLap, ThanhToanThucTe, TrangThai)")])

add("RB29", "Liên quan hệ (thống kê) – ĐỀ XUẤT, CHƯA CÀI, CHỜ XÁC NHẬN", "CHI_NHANH, NHAN_VIEN",
    ["∀ cn ∈ CHI_NHANH: |{nv ∈ NHAN_VIEN : nv.ChucVu = 'Quản lý' ∧ nv.ConLamViec = 1 ∧ nv.MaCN = cn.MaCN}| = 1"],
    ["Đề liệt kê “Quản lý chi nhánh” là một chức vụ nhưng không nói mỗi chi nhánh có đúng một quản lý nên chưa cài. Nếu được duyệt: trigger kiểm tra cuối giao dịch (thay hoặc điều chuyển quản lý và mở chi nhánh mới phải nằm trong một giao dịch; cho phép tạm thời 0 hoặc 2 quản lý trong giao dịch, kiểm tra ngay trước COMMIT vì SQL Server không có ràng buộc trì hoãn)."],
    [("CHI_NHANH", "+", "-", "-"),
     ("NHAN_VIEN", "+", "-", "+ (ChucVu, MaCN, ConLamViec)")])

add("RB30", "Liên quan hệ (tham chiếu miền) – KẾ THỪA V2, CHỜ XÁC NHẬN", "DANG_KY_GOI, PHONG, GOI_DICH_VU, CHI_NHANH_DICH_VU",
    ["∀ dk ∈ DANG_KY_GOI (kiểm tra khi mua): ∃ cd ∈ CHI_NHANH_DICH_VU: cd.MaCN = dk.MaCN ∧ cd.MaLoai = GOI_DICH_VU(dk.MaGoi).MaLoai ∧ cd.TrangThai = 'Hoạt động'",
     "∀ p ∈ PHONG: ∃ cd ∈ CHI_NHANH_DICH_VU: cd.MaCN = p.MaCN ∧ cd.MaLoai = p.MaLoai"],
    ["Kế thừa từ báo cáo v2 (đề nói mỗi chi nhánh cung cấp danh sách dịch vụ, ERD có CHI_NHANH_DICH_VU nhưng không buộc gói và phòng phải thuộc các dịch vụ đó). Trigger trên DANG_KY_GOI và PHONG nếu được duyệt."],
    [("DANG_KY_GOI", "+", "-", "+ (MaCN, MaGoi)"),
     ("PHONG", "+", "-", "+ (MaCN, MaLoai)"),
     ("GOI_DICH_VU", "-", "-", "+ (MaLoai)"),
     ("CHI_NHANH_DICH_VU", "-", "+", "+ (TrangThai)")])

assert list(RBX) == [f"RB{i:02d}" for i in range(1, 31)]
