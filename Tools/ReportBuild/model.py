"""Dữ kiện chuẩn dùng chung cho mọi phần của báo cáo v3 (một nguồn duy nhất để các con số không lệch)."""

# ---- 19 thực thể của ERD (phân loại theo màu/hình của CSDLA_v3.png)
ENT_THUONG = ["CHI_NHANH", "LOAI_DICH_VU", "PHONG", "GOI_DICH_VU", "SAN_PHAM", "HANG_HOI_VIEN", "HOI_VIEN",
              "HOA_DON", "NHAN_VIEN", "DANH_GIA_PT"]
ENT_LOP_CON = ["HUAN_LUYEN_VIEN"]
ENT_KET_HOP = ["DANG_KY_GOI", "CHECK_IN", "LICH_HEN_PT", "LICH_SU_DIEU_CHUYEN"]
ENT_NN = ["CHI_NHANH_DICH_VU", "TON_KHO"]
ENT_YEU = ["DIEM_LOYALTY", "CHI_TIET_HOA_DON"]
ENTITIES = ENT_THUONG + ENT_LOP_CON + ENT_KET_HOP + ENT_NN + ENT_YEU
DERIVED_TABLES = ["THONG_KE_CHECKIN", "DOANH_THU_NGAY"]

# ---- Thứ tự quan hệ ở mục 4.2 / 4.3 / 4.6 (22 quan hệ = 19 thực thể + HLV_CHUNG_CHI + 2 bảng dẫn xuất)
REL_ORDER = ["CHI_NHANH", "LOAI_DICH_VU", "CHI_NHANH_DICH_VU", "PHONG", "GOI_DICH_VU", "SAN_PHAM", "TON_KHO",
             "HANG_HOI_VIEN", "HOI_VIEN", "DIEM_LOYALTY", "NHAN_VIEN", "HUAN_LUYEN_VIEN", "HLV_CHUNG_CHI",
             "LICH_SU_DIEU_CHUYEN", "HOA_DON", "CHI_TIET_HOA_DON", "DANG_KY_GOI", "CHECK_IN", "LICH_HEN_PT",
             "DANH_GIA_PT", "THONG_KE_CHECKIN", "DOANH_THU_NGAY"]

# ---- 32 mối liên kết của ERD, đọc từ CSDLA_v3.drawio/png.
# (nhãn, Từ, ký hiệu trái, ký hiệu phải, Đến, min..max Từ, min..max Đến, ghi chú)
# Ký hiệu đặt ở đầu cạnh của thực thể đó (ký hiệu gần X cho biết số X ứng với một thể hiện phía bên kia).
L = {"1..1": "||", "0..1": "|o", "0..N": ">o", "1..N": ">|"}   # glyph khi đứng bên trái
R = {"1..1": "||", "0..1": "o|", "0..N": "o<", "1..N": "|<"}   # glyph khi đứng bên phải
LINKS = [
    ("cung cấp", "CHI_NHANH", "1..1", "CHI_NHANH_DICH_VU", "0..N", "một nửa của N–N có thuộc tính", False),
    ("được cung cấp", "LOAI_DICH_VU", "1..1", "CHI_NHANH_DICH_VU", "0..N", "nửa còn lại của N–N có thuộc tính", False),
    ("lưu kho", "CHI_NHANH", "1..1", "TON_KHO", "0..N", "một nửa của N–N có thuộc tính", False),
    ("tồn kho", "SAN_PHAM", "1..1", "TON_KHO", "0..N", "nửa còn lại của N–N có thuộc tính", False),
    ("có phòng", "CHI_NHANH", "1..1", "PHONG", "1..N", "", False),
    ("loại phòng", "LOAI_DICH_VU", "1..1", "PHONG", "0..N", "", False),
    ("phân loại", "LOAI_DICH_VU", "1..1", "GOI_DICH_VU", "0..N", "", False),
    ("làm việc tại", "CHI_NHANH", "1..1", "NHAN_VIEN", "1..N", "chi nhánh hiện tại của nhân viên (RB24)", False),
    ("U (chuyên biệt hóa)", "NHAN_VIEN", None, "HUAN_LUYEN_VIEN", None, "ký hiệu U, ChucVu = 'HLV'; hình không ghi bản số (RB26)", False),
    ("được điều chuyển", "NHAN_VIEN", "1..1", "LICH_SU_DIEU_CHUYEN", "1..N", "mỗi nhân viên có ít nhất một bản ghi (RB23)", False),
    ("tiếp nhận", "CHI_NHANH", "1..1", "LICH_SU_DIEU_CHUYEN", "0..N", "chi nhánh đích của giai đoạn", False),
    ("lập", "NHAN_VIEN", "1..1", "HOA_DON", "0..N", "(RB13)", False),
    ("Thanh toán", "HOI_VIEN", "1..1", "HOA_DON", "0..N", "", False),
    ("lập tại", "CHI_NHANH", "1..1", "HOA_DON", "0..N", "", False),
    ("gồm (HOA_DON)", "HOA_DON", "1..1", "CHI_TIET_HOA_DON", "1..N", "liên kết định danh của thực thể yếu (nét đứt; RB14)", True),
    ("gồm (SAN_PHAM)", "SAN_PHAM", "0..1", "CHI_TIET_HOA_DON", "0..N", "loại trừ với gồm (GOI_DICH_VU) theo Loai (RB07)", False),
    ("gồm (GOI_DICH_VU)", "GOI_DICH_VU", "0..1", "CHI_TIET_HOA_DON", "0..N", "loại trừ với gồm (SAN_PHAM) theo Loai (RB07)", False),
    ("xuất ra", "CHI_TIET_HOA_DON", "1..1", "DANG_KY_GOI", "0..N", "một dòng Gói có SoLuong = n sinh n bản ghi DANG_KY_GOI (RB08)", False),
    ("đăng ký", "HOI_VIEN", "1..1", "DANG_KY_GOI", "0..N", "", False),
    ("được đăng ký", "GOI_DICH_VU", "1..1", "DANG_KY_GOI", "0..N", "dư thừa có chủ đích với CHI_TIET_HOA_DON.MaGoi (RB08)", False),
    ("đăng ký tại", "CHI_NHANH", "1..1", "DANG_KY_GOI", "0..N", "dư thừa có chủ đích với HOA_DON.MaCN (RB12)", False),
    ("tích lũy", "HOI_VIEN", "1..1", "DIEM_LOYALTY", "0..N", "liên kết định danh của thực thể yếu (nét đứt; RB05)", True),
    ("xếp hạng", "HANG_HOI_VIEN", "1..1", "DIEM_LOYALTY", "0..N", "hạng của từng năm (RB04)", False),
    ("check-in", "HOI_VIEN", "1..1", "CHECK_IN", "0..N", "(RB17)", False),
    ("ghi nhận tại", "CHI_NHANH", "1..1", "CHECK_IN", "0..N", "chi nhánh nơi hội viên đến tập (RB17)", False),
    ("vào phòng", "PHONG", "0..1", "CHECK_IN", "0..N", "mỗi lượt có tối đa một phòng (RB17, RB27)", False),
    ("được dùng", "DANG_KY_GOI", "1..1", "CHECK_IN", "0..N", "gói dùng để vào (RB16)", False),
    ("diễn ra tại", "CHI_NHANH", "1..1", "LICH_HEN_PT", "0..N", "(RB21)", False),
    ("phụ trách", "HUAN_LUYEN_VIEN", "1..1", "LICH_HEN_PT", "0..N", "(RB19, RB21)", False),
    ("đặt lịch", "HOI_VIEN", "1..1", "LICH_HEN_PT", "0..N", "dư thừa có chủ đích với DANG_KY_GOI.MaHV (RB18)", False),
    ("thuộc", "DANG_KY_GOI", "1..1", "LICH_HEN_PT", "0..N", "(RB20)", False),
    ("được đánh giá", "LICH_HEN_PT", "1..1", "DANH_GIA_PT", "0..1", "mỗi lịch tối đa một đánh giá (RB22)", False),
]

# ---- Mã ràng buộc RB01..RB30: mã và tên khớp danh mục trong FitLifeHub.v2.dbml
RB = [
    ("RB01", "Giờ mở – đóng cửa"),
    ("RB02", "Miền giá trị (CHECK thay cho ENUM)"),
    ("RB03", "Khóa thay thế: unique filtered index cho cột cho phép NULL"),
    ("RB04", "Thanh toán cập nhật DIEM_LOYALTY bằng một UPDATE theo khóa chính"),
    ("RB05", "Dòng DIEM_LOYALTY của năm mới và của hội viên mới"),
    ("RB06", "Ngưỡng hạng hội viên"),
    ("RB07", "Dòng chi tiết là gói hoặc sản phẩm, loại trừ nhau"),
    ("RB08", "DANG_KY_GOI khớp CHI_TIET_HOA_DON: khóa ghép, số gói = SoLuong, cùng MaGoi"),
    ("RB09", "Tiền hóa đơn: TongTienGoc, GiamGia, ThanhToanThucTe"),
    ("RB10", "Thành tiền dòng chi tiết và đơn giá chốt"),
    ("RB11", "Ngày kết thúc gói lưu có chủ đích, không có bảo lưu"),
    ("RB12", "DANG_KY_GOI cùng hội viên, chi nhánh với hóa đơn"),
    ("RB13", "Chi nhánh hóa đơn = chi nhánh của nhân viên lập tại ngày lập"),
    ("RB14", "Mỗi hóa đơn có ít nhất một dòng chi tiết"),
    ("RB15", "Mỗi hội viên tối đa một lượt check-in chưa check-out"),
    ("RB16", "Xác thực check-in dưới 50 ms"),
    ("RB17", "CHECK_IN: hội viên và chi nhánh đồng nhất"),
    ("RB18", "LICH_HEN_PT: hội viên đồng nhất với gói"),
    ("RB19", "Chống overbooking lịch PT"),
    ("RB20", "Đặt lịch: số lịch Đã đặt không vượt BuoiConLai"),
    ("RB21", "Đặt lịch: HLV công tác tại chi nhánh vào ngày hẹn"),
    ("RB22", "Đánh giá PT: mỗi lịch một đánh giá, chỉ lịch đã hoàn thành"),
    ("RB23", "Lịch sử điều chuyển: các khoảng liên tiếp, tối đa một bản ghi đang mở"),
    ("RB24", "Chi nhánh hiện tại của nhân viên khớp bản ghi đang mở"),
    ("RB25", "Hoa hồng PT theo chi nhánh từng giai đoạn"),
    ("RB26", "Chuyên biệt hóa HUAN_LUYEN_VIEN"),
    ("RB27", "Người đang có mặt và tỷ lệ lấp đầy (THONG_KE_CHECKIN)"),
    ("RB28", "Doanh thu ngày (DOANH_THU_NGAY)"),
    ("RB29", "Mỗi chi nhánh đúng một quản lý (đề xuất, chờ xác nhận)"),
    ("RB30", "Chi nhánh chỉ bán gói và có phòng thuộc loại dịch vụ mà chi nhánh cung cấp (kế thừa v2, chờ xác nhận)"),
]
RB_CODES = [c for c, _ in RB]

# ---- 30 chức năng của bảng tần suất
N_QT = 7
N_CN = 30
LEVELS = {"Cao": 4, "Trung bình": 12, "Thấp": 14}


def notation(frm_card, to_card, dashed=False):
    if frm_card is None:
        return "U"
    dash = ".." if dashed else "--"
    return L[frm_card] + dash + R[to_card]
