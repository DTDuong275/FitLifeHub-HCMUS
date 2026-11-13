# -*- coding: utf-8 -*-
"""Bố cục các hình: rows = danh sách hàng, mỗi phần tử (tên bảng, x hoặc None = tự xếp)."""

LAYOUTS = {
    "TONG": dict(
        title="MÔ HÌNH DỮ LIỆU QUAN HỆ – HỆ THỐNG FITLIFE HUB (tổng thể, 20 quan hệ)",
        png="luoc_do_tong.png", W=2000, row_gap=120,
        note="Ghi chú: DANG_KY_GOI(MaHD, SoThuTu) là khóa ngoại ghép tham chiếu khóa chính (MaHD, SoThuTu) của CHI_TIET_HOA_DON. "
             "HLV_CHUNG_CHI là bảng của thuộc tính đa trị {ChungChi}. Ho/TenDem/Ten là thành phần của HoTen; SoNha/Duong/Quan/ThanhPho của DiaChi.",
        rows=[
            [("CHI_NHANH_DICH_VU", 360), ("LOAI_DICH_VU", 40), ("HANG_HOI_VIEN", 1000), ("SAN_PHAM", 1440)],
            [("PHONG", 40), ("GOI_DICH_VU", 600), ("DIEM_LOYALTY", 1220)],
            [("CHI_NHANH", 40), ("TON_KHO", 810), ("HOI_VIEN", 1180)],
            [("NHAN_VIEN", 40), ("HOA_DON", 960)],
            [("HUAN_LUYEN_VIEN", 40), ("HLV_CHUNG_CHI", 500), ("CHI_TIET_HOA_DON", 1020)],
            [("LICH_SU_DIEU_CHUYEN", 200), ("DANG_KY_GOI", 900)],
            [("CHECK_IN", 40), ("LICH_HEN_PT", 1160)],
            [("DANH_GIA_PT", 1000)],
        ]),
    "M1": dict(
        title="Hình 1 – Danh mục, chi nhánh, sản phẩm & tồn kho",
        png="luoc_do_mo_dun_1.png", W=1700, row_gap=130,
        note="Bảng nằm ở mô-đun khác không có trong hình này (xem hình 2, 3).",
        rows=[
            [("LOAI_DICH_VU", 40), ("SAN_PHAM", 1100)],
            [("GOI_DICH_VU", 40), ("PHONG", 740), ("CHI_NHANH_DICH_VU", 1320)],
            [("CHI_NHANH", 40), ("TON_KHO", 900)],
        ]),
    "M2": dict(
        title="Hình 2 – Hội viên, loyalty, gói đăng ký & hóa đơn",
        png="luoc_do_mo_dun_2.png", W=1700, row_gap=130,
        ghosts=["NHAN_VIEN", "CHI_NHANH", "GOI_DICH_VU", "SAN_PHAM"],
        note="Mô-đun 2 tham chiếu 4 bảng thuộc mô-đun 1 và 3 (vẽ nhạt, chỉ có khóa chính).",
        rows=[
            [("HANG_HOI_VIEN", 200), ("DIEM_LOYALTY", 660)],
            [("HOI_VIEN", 40)],
            [("HOA_DON", 240)],
            [("CHI_TIET_HOA_DON", 320), ("NHAN_VIEN", 160), ("SAN_PHAM", 960)],
            [("DANG_KY_GOI", 120), ("GOI_DICH_VU", 1000), ("CHI_NHANH", 1280)],
        ]),
    "M3": dict(
        title="Hình 3 – Nhân sự, lịch hẹn PT & check-in",
        png="luoc_do_mo_dun_3.png", W=1700, row_gap=130,
        ghosts=["CHI_NHANH", "HOI_VIEN", "PHONG", "DANG_KY_GOI"],
        note="Mô-đun 3 tham chiếu 4 bảng thuộc mô-đun 1 và 2 (vẽ nhạt, chỉ có khóa chính).",
        rows=[
            [("LICH_SU_DIEU_CHUYEN", 320), ("PHONG", 1020), ("DANG_KY_GOI", 1240)],
            [("NHAN_VIEN", 40), ("CHECK_IN", 980)],
            [("HUAN_LUYEN_VIEN", 40), ("CHI_NHANH", 740)],
            [("HLV_CHUNG_CHI", 40), ("LICH_HEN_PT", 500)],
            [("DANH_GIA_PT", 500), ("HOI_VIEN", 1120)],
        ]),
}
