"""Phần 1: Tổng quan, mục 1 (QT1–QT7), mục 2 (tần suất), mục 3 (mức quan niệm)."""
from xmllib import *
from model import *

CN_ROWS = [
    ("CN01", "Check-in: xác thực quyền + ghi log",
     "Quét thẻ/QR tại thiết bị (ThietBi) của một chi nhánh bất kỳ; tìm DANG_KY_GOI 'Hoạt động' còn hạn theo MaHV (IX_DK_XacThuc); ghi CHECK_IN (MaHV, MaCN, MaPhong, MaDK, ThietBi)",
     "Đọc + Ghi", "≈14.000 lượt/ngày; cao điểm 17h–20h ≈10.000 lượt (≈56 lượt/phút toàn hệ thống)", "Cao", "Đề vấn đề 1; yêu cầu < 50 ms (RB16)"),
    ("CN02", "Check-out", "Cập nhật ThoiGianRa của lượt check-in đang mở (ThoiGianRa IS NULL) của hội viên",
     "Ghi", "≈14.000 lượt/ngày; dồn vào 18h–21h", "Cao", "Mỗi check-in có một check-out"),
    ("CN03", "Đặt lịch PT 1-1",
     "Khóa DANG_KY_GOI (UPDLOCK), kiểm tra số lịch Đã đặt ≤ BuoiConLai và HLV công tác tại chi nhánh vào NgayGioHen, tạo LICH_HEN_PT; hai unique filtered index chặn trùng giờ",
     "Đọc + Ghi", "≈1.000 lượt/ngày; cao điểm 17h–21h và cuối tuần", "Cao", "12 chi nhánh × ≈10 HLV × ≈8 buổi/ngày ≈ 960; đề vấn đề 2"),
    ("CN04", "Hủy/đổi lịch PT", "Đổi TrangThai = 'Hủy' để giải phóng giờ hẹn; đổi giờ = hủy rồi đặt mới (CN03)",
     "Ghi", "≈150 lượt/ngày", "Trung bình", "≈15% lịch đã đặt"),
    ("CN05", "Hoàn thành buổi PT", "Đổi TrangThai = 'Đã hoàn thành', trừ BuoiConLai; gói có SoBuoi > 0 hết buổi thì chuyển 'Hết hạn'",
     "Ghi", "≈850 lượt/ngày", "Trung bình", "≈85% lịch không hủy"),
    ("CN06", "Đánh giá HLV", "Hội viên chấm điểm 1–5 và nhận xét (DANH_GIA_PT), mỗi lịch tối đa một đánh giá",
     "Ghi", "≈250 lượt/ngày", "Trung bình", "≈30% buổi hoàn thành có đánh giá (≈255)"),
    ("CN07", "Tra cứu lịch sử tập luyện / lịch hẹn PT của hội viên",
     "Danh sách CHECK_IN và LICH_HEN_PT theo MaHV (cả hai bảng đều có MaHV), theo khoảng thời gian",
     "Đọc", "≈1.500 lượt/ngày", "Cao", "Lễ tân tra cứu + hội viên xem trên ứng dụng"),
    ("CN08", "Đăng ký hội viên mới", "Tạo HOI_VIEN và dòng DIEM_LOYALTY của năm hiện tại (hạng ngưỡng 0, chi tiêu 0, điểm 0)",
     "Ghi", "≈33 lượt/ngày (≈3 lượt/chi nhánh/ngày)", "Thấp", "≈12.000 hội viên mới/năm ÷ 365 ngày ≈ 33/ngày"),
    ("CN09", "Mua / gia hạn gói, vé Spa lẻ",
     "Dòng CHI_TIET_HOA_DON loại Gói và sinh SoLuong bản ghi DANG_KY_GOI (MaHV, MaCN, MaGoi, NgayBatDau, NgayKetThuc, BuoiConLai)",
     "Ghi", "≈150 lượt/ngày", "Trung bình", "≈12 gói/chi nhánh/ngày × 12 chi nhánh ≈ 144"),
    ("CN10", "Bán sản phẩm", "Lập hóa đơn có dòng CHI_TIET_HOA_DON loại Sản phẩm, trừ TON_KHO của chi nhánh",
     "Ghi", "≈600 lượt/ngày; cao điểm 17h–20h", "Trung bình", "≈50 hóa đơn SP/chi nhánh/ngày × 12"),
    ("CN11", "Lập hóa đơn / thanh toán",
     "Tạo HOA_DON và các dòng CHI_TIET_HOA_DON; tính TongTienGoc, GiamGia, ThanhToanThucTe, chọn HinhThucThanhToan; cộng DOANH_THU_NGAY",
     "Ghi", "≈750 hóa đơn/ngày (≈1,6 hóa đơn/phút lúc cao điểm, giả định ≈50% dồn vào 17h–21h)", "Trung bình", "= CN09 + CN10"),
    ("CN12", "Cập nhật điểm & hạng Loyalty",
     "Một UPDATE theo khóa chính DIEM_LOYALTY (MaHV, NamXet): cộng TongChiTieuNam, DiemThuong, gán MaHang theo ngưỡng (RB04)",
     "Đọc + Ghi", "≈750 lần/ngày", "Trung bình", "Mỗi hóa đơn thanh toán kích hoạt 1 lần (đề vấn đề 4)"),
    ("CN13", "Tra cứu hạng/điểm hội viên", "Đọc dòng DIEM_LOYALTY của năm hiện tại theo khóa chính (MaHV, NamXet)",
     "Đọc", "≈800 lượt/ngày", "Trung bình", "Tại quầy khi thanh toán"),
    ("CN14", "Hủy hóa đơn", "Đảo ngược: DANG_KY_GOI chuyển 'Hủy', hoàn TON_KHO, trừ DIEM_LOYALTY của năm lập, trừ DOANH_THU_NGAY",
     "Ghi", "≈15 lượt/ngày", "Thấp", "≈2% hóa đơn"),
    ("CN15", "Cập nhật tồn kho (nhập hàng/kiểm kê)", "Tăng/điều chỉnh TON_KHO.SoLuong, ghi NgayCapNhat",
     "Ghi", "≈30 lượt/ngày", "Thấp", "2–3 đợt nhập/chi nhánh/ngày"),
    ("CN16", "Quản lý danh mục: gói, sản phẩm, phòng, loại và dịch vụ chi nhánh, hạng hội viên",
     "Thêm/sửa/ngừng bán GOI_DICH_VU, SAN_PHAM, PHONG, LOAI_DICH_VU, CHI_NHANH_DICH_VU, HANG_HOI_VIEN",
     "Ghi", "≈10 lượt/ngày", "Thấp", "Thay đổi danh mục hiếm"),
    ("CN17", "Điều chuyển nhân viên", "Đóng và mở bản ghi LICH_SU_DIEU_CHUYEN, cập nhật NHAN_VIEN.MaCN trong một giao dịch",
     "Ghi", "≈5 lượt/tháng", "Thấp", "≈50 lượt điều chuyển/năm ≈ 4/tháng"),
    ("CN18", "Cập nhật lương cơ bản / thêm sửa nhân viên", "Sửa NHAN_VIEN, HUAN_LUYEN_VIEN, HLV_CHUNG_CHI",
     "Ghi", "≈10 lượt/tháng", "Thấp", "Định kỳ"),
    ("CN19", "Tính hoa hồng PT",
     "Đếm lịch 'Đã hoàn thành' của HLV theo chi nhánh của từng giai đoạn trong LICH_SU_DIEU_CHUYEN, nhân HoaHongMoiBuoi (RB25)",
     "Đọc", "1 lần/tháng toàn hệ thống + ≈10 lượt xem lẻ/ngày", "Thấp", "Đề vấn đề 5"),
    ("CN20", "BC doanh thu theo ngày/tháng/quý/năm (chi nhánh)", "Tổng hợp từ DOANH_THU_NGAY theo chi nhánh và kỳ",
     "Đọc", "≈120 lượt/ngày", "Trung bình", "≈10 lần/chi nhánh/ngày; đề vấn đề 3 (< 1 phút)"),
    ("CN21", "DS hội viên check-in trong ngày theo khung giờ", "Liệt kê CHECK_IN theo ngày/giờ/chi nhánh",
     "Đọc", "≈240 lượt/ngày", "Trung bình", "≈20 lần/chi nhánh/ngày"),
    ("CN22", "Tỷ lệ lấp đầy theo khung giờ/chi nhánh",
     "Số người đang có mặt (cộng dồn SoLuotVao − SoLuotRa trong THONG_KE_CHECKIN) chia tổng SucChua của PHONG đang hoạt động trong chi nhánh (RB27)",
     "Đọc", "≈430 lượt/ngày (12 chi nhánh × 36 lần làm mới, mỗi 5 phút trong 3 giờ cao điểm)", "Trung bình", "Đề vấn đề 3"),
    ("CN23", "Gói/sản phẩm bán chạy tại chi nhánh", "Tổng hợp CHI_TIET_HOA_DON theo MaGoi (gói) và MaSP (sản phẩm)",
     "Đọc", "≈36 lượt/ngày", "Thấp", "≈3 lần/chi nhánh/ngày"),
    ("CN24", "Báo cáo tồn kho", "Liệt kê TON_KHO theo chi nhánh, cảnh báo sắp hết",
     "Đọc", "≈60 lượt/ngày", "Trung bình", "≈5 lần/chi nhánh/ngày"),
    ("CN25", "Hiệu suất làm việc HLV", "Số buổi dạy ('Đã hoàn thành'), điểm đánh giá trung bình (DANH_GIA_PT)",
     "Đọc", "≈30 lượt/ngày", "Thấp", "Quản lý chi nhánh xem định kỳ"),
    ("CN26", "Hội viên sắp hết hạn / lâu chưa quay lại", "Job hằng ngày + truy vấn lễ tân trên DANG_KY_GOI (NgayKetThuc) và CHECK_IN (MaHV, ThoiGianVao)",
     "Đọc", "1 job/ngày + ≈36 lượt truy vấn/ngày", "Thấp", "Đề mục 4"),
    ("CN27", "BC công ty: doanh thu toàn hệ thống, so sánh chi nhánh, gói doanh thu cao nhất 6 tháng, phân bố hạng",
     "Tổng hợp liên chi nhánh từ DOANH_THU_NGAY, CHI_TIET_HOA_DON và DIEM_LOYALTY (NamXet, MaHang)",
     "Đọc", "≈35 lượt/ngày", "Thấp", "Ban giám đốc"),
    ("CN28", "Job cập nhật trạng thái gói hết hạn", "Đổi TrangThai gói 'Hoạt động' có NgayKetThuc đã qua thành 'Hết hạn'",
     "Ghi", "1 lần/ngày (batch, ≈100–200 gói)", "Thấp", "Chạy đêm"),
    ("CN29", "Job tạo dòng Loyalty của năm mới",
     "0h ngày 1/1: tạo DIEM_LOYALTY (MaHV, năm mới, 0, 0, hạng ngưỡng 0) cho mọi hội viên (RB05)",
     "Ghi", "1 lần/năm (≈30.000 dòng)", "Thấp", "Hạng xét theo năm dương lịch (E1)"),
    ("CN30", "Job đóng lượt check-in chưa check-out",
     "Lúc GioDongCua của chi nhánh, đặt ThoiGianRa cho các lượt còn mở để số người có mặt không rò sang ngày sau (RB27)",
     "Ghi", "1 lần/ngày/chi nhánh (12 lần/ngày)", "Thấp", "Cần cho tỷ lệ lấp đầy (E9)"),
]
assert len(CN_ROWS) == N_CN
_cnt = {}
for r in CN_ROWS:
    _cnt[r[5]] = _cnt.get(r[5], 0) + 1
assert _cnt == LEVELS, _cnt


def overview():
    n_ent, n_lk = len(ENTITIES), len(LINKS)
    o = [h1("Tổng quan giai đoạn 1", first=True, page_break=True)]
    o.append(p(f"Báo cáo gồm các nội dung giai đoạn 1 theo tài liệu yêu cầu nộp: (1) mô tả chi tiết quy trình nghiệp vụ, (2) bảng phân tích tần suất chức năng, (3) thiết kế mức quan niệm gồm mô hình ERD ({n_ent} thực thể, {n_lk} mối liên kết) và mô tả các ràng buộc chưa thể hiện trên mô hình, (4) thiết kế mức logic gồm lược đồ CSDL quan hệ, khóa, phụ thuộc hàm, dạng chuẩn, ràng buộc (bối cảnh – nội dung – bảng tầm ảnh hưởng) và mô tả quan hệ/thuộc tính.", after=100))
    o.append(h2("Giả định quy mô và cách xếp mức tần suất"))
    o.append(bullet("Quy mô hệ thống: 12 chi nhánh (theo đề), khoảng 30.000 hội viên còn hiệu lực (≈2.500/chi nhánh), ≈180 nhân viên (13–17 người/chi nhánh: 1 quản lý, 2–3 lễ tân, 2–3 nhân viên bán hàng và 8–10 HLV; lấy trung bình ≈15 người/chi nhánh). Khi tính tải đặt lịch PT nhóm lấy cận trên ≈10 HLV/chi nhánh, tức ≈120 HLV."))
    o.append(bullet("Check-in: đề nêu hơn 10.000 lượt trong khung 17h00–20h00 và dữ liệu check-in + lịch tập tăng hơn 300.000 dòng/tháng. Nhóm ước lượng ≈14.000 lượt check-in/ngày (≈420.000/tháng), trong đó ≈10.000 lượt dồn vào 3 giờ cao điểm (≈3.300 lượt/giờ, ≈56 lượt/phút toàn hệ thống, ≈1 lượt/giây). Con số 420.000 lớn hơn mốc “hơn 300.000 dòng/tháng” của đề vì đề chỉ nêu cận dưới: 10.000 lượt giờ cao điểm × 30 ngày đã là 300.000 dòng/tháng, cộng thêm ≈4.000 lượt/ngày ngoài giờ cao điểm (≈29% lượt trong ngày) thì được ≈14.000 × 30 = 420.000 dòng/tháng, nên vẫn khớp với đề."))
    o.append(bullet("Chương trình hội viên thân thiết: đề viết hạng “dựa trên tổng chi tiêu trong năm”, nên nhóm xét hạng theo năm dương lịch (DIEM_LOYALTY.NamXet); cụm “12 tháng qua” ở vấn đề 4 là cách tính của hệ thống cũ. Hệ quả là hạng của mọi hội viên về mức thấp nhất vào ngày 1/1 hằng năm. Nếu cần 12 tháng trượt thì đổi NamXet thành NamThang và xét hạng bằng tổng tối đa 12 dòng tháng; thay đổi này chỉ ảnh hưởng DIEM_LOYALTY, RB04 và RB05."))
    o.append(bullet("Đề không có bảo lưu gói, khung giờ PT cố định hay thực thể thiết bị nên mô hình không có: trạng thái gói chỉ gồm Hoạt động, Hết hạn, Hủy; mỗi buổi PT dài 60 phút và bắt đầu tại phút 00; ThietBi của CHECK_IN là một chuỗi văn bản. Gói không kèm buổi PT có SoBuoi = 0."))
    o.append(bullet("Các con số còn lại là ước lượng của nhóm từ quy mô trên, dùng để xếp mức độ tần suất; sẽ hiệu chỉnh lại khi có dữ liệu quan sát thực tế."))
    o.append(bullet("Thang mức độ tần suất: Cao ≥ 1.000 lần/ngày hoặc nằm trên đường găng giờ cao điểm; Trung bình 50–999 lần/ngày; Thấp < 50 lần/ngày hoặc chạy định kỳ."))
    return o


def qt():
    o = [h1("1. Mô tả chi tiết quy trình nghiệp vụ")]
    o.append(p("Mỗi quy trình nêu tác nhân, diễn biến từng bước và các quy tắc nghiệp vụ. Mã ràng buộc RBxx trỏ tới mục 4.5."))

    def qt_block(title, actors, steps, rules, numid):
        o.append(h2(title))
        o.append(labeled("Tác nhân:", actors))
        o.append(label("Diễn biến:"))
        for s in steps:
            o.append(numbered(s, numid))
        o.append(label("Quy tắc nghiệp vụ:"))
        for r in rules:
            o.append(bullet(r))

    qt_block("QT1. Đăng ký hội viên và mua gói dịch vụ / vé Spa lẻ",
             "Lễ tân (lập hóa đơn), hội viên, hệ thống",
             ["Hội viên mới cung cấp họ tên, SĐT, giới tính, ngày sinh và (nếu có) email, CCCD. Lễ tân kiểm tra SĐT chưa tồn tại, email và CCCD (nếu có) chưa tồn tại (RB03), rồi tạo HOI_VIEN (NgayDangKy = hôm nay). MaHV do hệ thống tự cấp.",
              "Trong cùng giao dịch tạo dòng DIEM_LOYALTY của năm hiện tại cho hội viên mới: TongChiTieuNam = 0, DiemThuong = 0, MaHang = hạng có ngưỡng 0 (Silver) (RB05).",
              "Hội viên chọn gói (Gym/Yoga 3–6–12 tháng, PT 1-1 theo số buổi, vé Spa lẻ) tại một chi nhánh đang cung cấp loại dịch vụ đó (CHI_NHANH_DICH_VU.TrangThai = 'Hoạt động', RB30). Gói phải còn được bán (ConHieuLuc = 1). Vé Spa lẻ là gói thuộc loại Spa mua riêng, không kèm Gym/Yoga, và có thời hạn như mọi gói khác.",
              "Lễ tân lập hóa đơn (QT5). Mỗi gói mua là một dòng CHI_TIET_HOA_DON (Loai = 'Gói', MaGoi, SoLuong, DonGia = giá hiện hành) (RB07, RB10).",
              "Với dòng Gói có SoLuong = n, hệ thống sinh đúng n bản ghi DANG_KY_GOI gắn (MaHD, SoThuTu) của dòng đó (RB08): MaHV và MaCN lấy từ hóa đơn (RB12), MaGoi = MaGoi của dòng, NgayBatDau = ngày chọn (mặc định hôm nay), NgayKetThuc = NgayBatDau + ThoiHanThang tháng (RB11), BuoiConLai = SoBuoi của gói, TrangThai = 'Hoạt động'.",
              "Hội viên đã có gói đang dùng vẫn mua thêm được, kể cả mua lại cùng gói (DANG_KY_GOI có khóa riêng MaDK). Khi đặt lịch PT hoặc check-in mà có nhiều gói hợp lệ, gói có NgayKetThuc sớm nhất được dùng trước (FEFO)."],
             ["SĐT của hội viên là duy nhất toàn hệ thống; Email và CCCD duy nhất nếu có giá trị (RB03).",
              "Gói không có trường số lượng riêng: số bản ghi DANG_KY_GOI của một dòng Gói bằng SoLuong của dòng đó và mỗi bản ghi truy ngược được về đúng dòng chi tiết đã thanh toán nó (RB08).",
              "Trạng thái gói chỉ thuộc {'Hoạt động', 'Hết hạn', 'Hủy'} (RB02). Gói có SoBuoi > 0 dùng hết buổi (BuoiConLai = 0) chuyển 'Hết hạn'; mọi gói 'Hoạt động' quá NgayKetThuc chuyển 'Hết hạn' (CN28).",
              "Hủy hóa đơn thì các DANG_KY_GOI của hóa đơn chuyển 'Hủy' và chi tiêu/điểm được trừ lại (RB04, RB12)."], 3)

    qt_block("QT2. Check-in / check-out tại chi nhánh",
             "Hội viên, thiết bị quét thẻ/QR, hệ thống",
             ["Hội viên quét thẻ hoặc QR tại một cửa kiểm soát của chi nhánh bất kỳ trong hệ thống. Thiết bị gửi mã hội viên, chi nhánh nơi đặt thiết bị, tên thiết bị (chuỗi ThietBi) và phòng nếu là cửa phòng.",
              "Hệ thống tìm gói hợp lệ bằng một lần seek chỉ mục IX_DK_XacThuc theo MaHV: DANG_KY_GOI có TrangThai = 'Hoạt động' và NgayBatDau ≤ hôm nay ≤ NgayKetThuc (RB16). Nếu có nhiều gói, chọn gói có NgayKetThuc sớm nhất. Không cần chọn gói cụ thể nên đây chỉ là phép tìm theo MaHV.",
              "Nếu hợp lệ: ghi một dòng CHECK_IN (MaHV, MaCN = chi nhánh nơi quét, MaPhong nếu vào phòng, MaDK = gói tìm được, ThoiGianVao, ThietBi) và mở cửa; trigger/job cộng một lượt vào THONG_KE_CHECKIN (MaCN, ngày, giờ) ở cột SoLuotVao.",
              "Nếu không hợp lệ: từ chối, hiển thị lý do (hết hạn / chưa đăng ký), không ghi CHECK_IN.",
              "Khi ra, hội viên quét lại; hệ thống cập nhật ThoiGianRa của lượt check-in đang mở và cộng một lượt vào SoLuotRa của giờ ra. Cuối ngày, job đóng các lượt chưa check-out vào lúc GioDongCua của chi nhánh (CN30, RB27)."],
             ["Thời gian xử lý xác thực + ghi log mục tiêu dưới 50 ms (vấn đề 1), kể cả giờ cao điểm 17h00–20h00 (RB16). ThietBi chỉ là chuỗi ghi nhận, không tham gia xác thực nên không cần chỉ mục.",
              "Mỗi hội viên chỉ có tối đa một lượt check-in chưa check-out tại một thời điểm, cài bằng unique filtered index (RB15).",
              "CHECK_IN lưu cả MaHV và MaDK: MaHV phải bằng hội viên của gói MaDK, và khi có MaPhong thì MaCN phải bằng chi nhánh của phòng (RB17). MaCN của CHECK_IN không buộc bằng chi nhánh đăng ký gói vì hội viên được tập tại bất kỳ chi nhánh nào.",
              "Check-in chỉ ghi nhận quyền vào chi nhánh và không trừ buổi; buổi PT được trừ ở QT3."], 4)

    qt_block("QT3. Đặt lịch và thực hiện buổi tập PT 1-1, đánh giá HLV",
             "Hội viên, lễ tân, HLV, hệ thống",
             ["Hội viên có gói 'Hoạt động' với SoBuoi > 0 và còn buổi chọn HLV, chi nhánh và NgayGioHen. Giờ hẹn bắt đầu tại phút 00 và mỗi buổi dài ThoiLuong = 60 phút (RB19).",
              "Trong một giao dịch, thủ tục đặt lịch: (a) khóa dòng DANG_KY_GOI bằng UPDLOCK và kiểm tra gói đang 'Hoạt động', còn hạn tại NgayGioHen và số lịch 'Đã đặt' của gói nhỏ hơn BuoiConLai (RB20); (b) kiểm tra HLV công tác tại chi nhánh đó vào ngày NgayGioHen theo LICH_SU_DIEU_CHUYEN và giờ hẹn nằm trong GioMoCua–GioDongCua của chi nhánh (RB21); (c) thêm LICH_HEN_PT (MaHV lấy từ gói – RB18, MaHLV, MaCN, MaDK, NgayGioHen, ThoiLuong, TrangThai = 'Đã đặt').",
              "Nếu hai hội viên cùng lúc đặt một HLV vào cùng giờ, unique filtered index (MaHLV, NgayGioHen) khiến đúng một giao dịch thành công; thủ tục bắt lỗi 2601/2627 và trả “khung giờ đã có người đặt” (RB19). Index (MaHV, NgayGioHen) chặn hội viên đặt hai lịch cùng giờ.",
              "Đến giờ, hội viên check-in (QT2); sau buổi tập HLV/lễ tân chuyển lịch sang 'Đã hoàn thành' và hệ thống trừ BuoiConLai của gói (RB20); gói có SoBuoi > 0 hết buổi thì chuyển 'Hết hạn'.",
              "Hội viên hoặc HLV hủy trước giờ hẹn: lịch chuyển 'Hủy' và giờ hẹn được giải phóng (index chỉ xét lịch khác 'Hủy'); buổi chưa trừ nên không phải hoàn lại.",
              "Sau khi hoàn thành, hội viên chấm điểm 1–5 và nhận xét (DANH_GIA_PT), mỗi buổi tối đa một đánh giá (RB22)."],
             ["Không cho phép overbooking: vì ThoiLuong cố định 60 phút và giờ hẹn tròn giờ nên hai lịch chồng khoảng thời gian khi và chỉ khi trùng NgayGioHen; do đó unique filtered index (MaHLV, NgayGioHen) và (MaHV, NgayGioHen) với TrangThai <> 'Hủy' là đủ để chặn tuyệt đối (vấn đề 2, RB19). Nếu sau này ThoiLuong nhận nhiều giá trị (30/60/90) thì phải thêm trigger kiểm tra chồng khoảng có UPDLOCK.",
              "Số lịch 'Đã đặt' của một gói không vượt BuoiConLai (RB20); kiểm tra dưới UPDLOCK để hai giao dịch đồng thời không cùng vượt.",
              "LICH_HEN_PT lưu cả MaHV và MaDK; MaHV phải bằng hội viên của gói (RB18).",
              "Chi nhánh của buổi hẹn là chi nhánh HLV công tác vào ngày hẹn (RB21). Chỉ lịch 'Đã hoàn thành' mới được đánh giá và mới tính hoa hồng (RB22, RB25)."], 5)

    qt_block("QT4. Bán sản phẩm và quản lý tồn kho",
             "Nhân viên bán hàng/lễ tân, hội viên, quản lý chi nhánh",
             ["Nhân viên bán hàng chọn sản phẩm (Whey protein, bình nước, thảm yoga…) và số lượng (theo DonViTinh của sản phẩm) cho hội viên.",
              "Hệ thống kiểm tra sản phẩm đang bán (ConBan = 1) và TON_KHO.SoLuong tại chi nhánh đủ số lượng.",
              "Lập hóa đơn (QT5): mỗi sản phẩm là một dòng CHI_TIET_HOA_DON (Loai = 'Sản phẩm', MaSP, SoLuong, DonGia = GiaBan hiện hành) (RB07, RB10). Khi hóa đơn thanh toán, TON_KHO của chi nhánh giảm đúng số lượng bán bằng một UPDATE có điều kiện SoLuong ≥ số lượng bán, NgayCapNhat được ghi.",
              "Quản lý chi nhánh cập nhật tồn kho khi nhập hàng/kiểm kê và xem báo cáo tồn kho thực phẩm bổ sung/phụ kiện."],
             ["Tồn kho theo từng chi nhánh không được âm (CHECK TON_KHO.SoLuong ≥ 0, RB02); bán vượt tồn bị từ chối.",
              "Hủy hóa đơn thì hoàn lại tồn kho cùng số lượng (QT5)."], 6)

    qt_block("QT5. Lập hóa đơn, thanh toán và cập nhật hạng/điểm Loyalty",
             "Lễ tân/nhân viên bán hàng, hội viên, hệ thống",
             ["Nhân viên (đang công tác tại chi nhánh lập hóa đơn vào ngày lập, RB13) tạo HOA_DON (MaNV, MaHV, MaCN, NgayLap) và thêm các dòng CHI_TIET_HOA_DON đánh số SoThuTu: mỗi dòng là một gói (QT1) hoặc một sản phẩm (QT4). DonGia là giá hiện hành tại lúc lập và không đổi về sau (RB10).",
              "Hệ thống tính ThanhTien của dòng = SoLuong × DonGia (cột tính), TongTienGoc = Σ ThanhTien, áp GiamGia (nếu có) và ThanhToanThucTe = TongTienGoc − GiamGia (RB09).",
              "Hội viên thanh toán bằng Tiền mặt, VNPay hoặc Thẻ (HinhThucThanhToan); hóa đơn có TrangThai = 'Đã thanh toán'; DOANH_THU_NGAY của chi nhánh và ngày lập được cộng thêm (RB28).",
              "Ngay sau khi thanh toán, trong cùng giao dịch, hệ thống cập nhật Loyalty bằng một câu UPDATE theo khóa chính DIEM_LOYALTY (MaHV, NamXet = năm của NgayLap) với UPDLOCK, HOLDLOCK, không quét lại hóa đơn cũ (vấn đề 4): TongChiTieuNam += ThanhToanThucTe; DiemThuong += ⌊ThanhToanThucTe / 100.000⌋; MaHang = hạng có NguongChiTieu lớn nhất không vượt TongChiTieuNam mới; NgayCapNhat = hiện tại (RB04).",
              "Vào 0h ngày 1/1, job tạo sẵn dòng DIEM_LOYALTY của năm mới cho mọi hội viên (Silver, 0, 0) (RB05, CN29).",
              "Hủy hóa đơn: TrangThai = 'Hủy'; các DANG_KY_GOI của hóa đơn chuyển 'Hủy' (RB12); hoàn TON_KHO; trừ ngược TongChiTieuNam và DiemThuong đúng dòng của năm lập hóa đơn rồi tính lại hạng (CHECK ≥ 0 chặn âm); trừ DOANH_THU_NGAY."],
             ["Ba hạng Silver – Gold – Platinum xét theo tổng chi tiêu trong năm dương lịch; 1 điểm = 100.000 VNĐ, điểm cộng theo từng hóa đơn (RB04). Hạng hiện tại là MaHang của dòng DIEM_LOYALTY có NamXet = năm hiện tại; HOI_VIEN không lưu hạng.",
              "Ngưỡng hạng duy nhất và có hạng ngưỡng 0 để mọi mức chi tiêu đều có hạng (RB06).",
              "Mỗi hóa đơn có ít nhất một dòng chi tiết (RB14); dòng chi tiết là gói hoặc sản phẩm, không cả hai (RB07).",
              "Hóa đơn đã thanh toán không xóa, chỉ chuyển 'Hủy' và đảo ngược các tác động nêu trên."], 7)

    qt_block("QT6. Quản lý nhân sự: điều chuyển, lương cơ bản, hoa hồng PT",
             "Ban giám đốc / quản lý nhân sự, quản lý chi nhánh",
             ["Nhân viên mới được tạo với chức vụ (HLV, Lễ tân, Quản lý, Bán hàng), lương cơ bản, NgayVaoLam, ConLamViec = 1, MaCN = chi nhánh vào làm, kèm bản ghi LICH_SU_DIEU_CHUYEN đầu tiên (MaCN, NgayBatDau = NgayVaoLam, NgayKetThuc = NULL, LyDo = 'Vào làm') (RB23). Nhân viên có ChucVu = 'HLV' có thêm bản ghi HUAN_LUYEN_VIEN (ChuyenMon, HoaHongMoiBuoi) và các chứng chỉ (HLV_CHUNG_CHI) (RB26).",
              "Khi điều chuyển, trong một giao dịch hệ thống đóng bản ghi LICH_SU_DIEU_CHUYEN đang mở (NgayKetThuc = ngày trước ngày chuyển), mở bản ghi mới tại chi nhánh đích (MaCN, NgayBatDau = ngày chuyển, LyDo) và cập nhật NHAN_VIEN.MaCN sang chi nhánh đích (RB23, RB24).",
              "Khi nhân viên nghỉ việc: đóng bản ghi đang mở và đặt ConLamViec = 0 (RB24).",
              "Quản lý nhân sự cập nhật lương cơ bản khi có điều chỉnh.",
              "Cuối tháng, tính hoa hồng PT: với mỗi lịch 'Đã hoàn thành' của HLV trong tháng, nối LICH_SU_DIEU_CHUYEN của HLV có NgayBatDau ≤ ngày hẹn ≤ NgayKetThuc (hoặc đang mở) để biết chi nhánh của giai đoạn đó; nhóm theo chi nhánh đó và nhân HoaHongMoiBuoi (RB25)."],
             ["Tại mọi thời điểm, nhân viên đang làm việc thuộc đúng một chi nhánh; các giai đoạn công tác của một nhân viên liên tiếp, không chồng lấn và tối đa một bản ghi đang mở (RB23).",
              "NHAN_VIEN.MaCN là chi nhánh hiện tại và phải bằng MaCN của bản ghi đang mở khi ConLamViec = 1 (RB24).",
              "ChucVu = 'HLV' khi và chỉ khi nhân viên có bản ghi HUAN_LUYEN_VIEN (RB26).",
              "Một HLV chuyển chi nhánh giữa tháng được tính hoa hồng riêng cho từng chi nhánh theo giai đoạn (vấn đề 5, RB25).",
              "Đề không nêu việc mỗi chi nhánh có đúng một quản lý nên ràng buộc này chưa được cài (RB29, chờ xác nhận)."], 8)

    qt_block("QT7. Báo cáo thống kê và theo dõi hội viên (cấp chi nhánh và công ty)",
             "Quản lý chi nhánh, ban giám đốc, hệ thống",
             ["Cấp chi nhánh: doanh thu theo ngày/tháng/quý/năm; danh sách hội viên check-in trong ngày theo khung giờ; gói/sản phẩm bán chạy; tồn kho; lịch sử tập luyện và lịch hẹn PT của một hội viên; hiệu suất HLV (số buổi dạy, điểm đánh giá trung bình); hội viên sắp hết hạn hoặc lâu chưa quay lại; tỷ lệ lấp đầy theo khung giờ/chi nhánh.",
              "Tỷ lệ lấp đầy tính theo số người đang có mặt chứ không theo số lượt vào: người có mặt cuối giờ h = Σ (SoLuotVao − SoLuotRa) của THONG_KE_CHECKIN từ giờ 0 đến h (hoặc đếm trực tiếp CHECK_IN có ThoiGianVao ≤ t < ThoiGianRa); chia cho tổng SucChua của các PHONG có ConHoatDong = 1 trong chi nhánh (RB27).",
              "Cấp công ty: doanh thu toàn hệ thống và so sánh giữa chi nhánh; gói mang lại doanh thu cao nhất 6 tháng gần nhất; tỷ lệ phân bố hạng hội viên (đếm theo MaHang của DIEM_LOYALTY trong năm); quản lý nhân sự toàn hệ thống.",
              "Báo cáo nặng (doanh thu, lấp đầy) đọc từ hai bảng tổng hợp DOANH_THU_NGAY và THONG_KE_CHECKIN được cập nhật bởi trigger hoặc job, không quét trực tiếp bảng log (vấn đề 3, RB27, RB28).",
              "Mỗi ngày một job quét các gói sắp hết hạn trong 7 ngày và các hội viên không check-in quá 30 ngày để lễ tân liên hệ; gói 'Hoạt động' quá NgayKetThuc chuyển sang 'Hết hạn' (CN26, CN28)."],
             ["Doanh thu chỉ tính hóa đơn 'Đã thanh toán' (RB28).",
              "Báo cáo cấp chi nhánh chỉ thấy dữ liệu của chi nhánh đó; cấp công ty thấy toàn hệ thống."], 9)
    o.append(p("", after=100))
    o.append(sect_break("portrait", "rId8"))
    return o


def freq():
    o = [h1("2. Bảng phân tích tần suất chức năng")]
    o.append(p("Tần suất là ước lượng của nhóm theo giả định quy mô ở phần Tổng quan; số liệu lấy trực tiếp từ đề được ghi rõ ở cột cơ sở. Cột Đọc/Ghi phục vụ thiết kế mức vật lý ở giai đoạn 2."))
    hdr = ["Mã", "Chức năng", "Mô tả chức năng", "Đọc/Ghi", "Tần suất", "Mức độ", "Cơ sở ước lượng"]
    o.append(table([802, 2482, 3279, 1105, 3098, 892, 2912], hdr, [list(r) for r in CN_ROWS]))
    c = LEVELS
    o.append(p(f"Tổng hợp: {N_CN} chức năng, trong đó mức Cao {c['Cao']}, Trung bình {c['Trung bình']}, Thấp {c['Thấp']}. Các chức năng mức Cao (check-in, check-out, đặt lịch PT, tra cứu lịch sử) là đối tượng ưu tiên tối ưu ở giai đoạn 2.", after=100))
    o.append(p("", after=100))
    return o


def conceptual():
    n_ent, n_lk = len(ENTITIES), len(LINKS)
    o = [h1("3. Thiết kế mức quan niệm"), h2("3.1 Mô hình ERD (ký hiệu Crow-Foot)")]
    o.append(p(f"Mô hình ERD gốc (hình ở mục 3.3) gồm {n_ent} kiểu thực thể: {len(ENT_THUONG)} thực thể thường ({', '.join(ENT_THUONG)}); {len(ENT_LOP_CON)} lớp con của chuyên biệt hóa (HUAN_LUYEN_VIEN, lớp con của NHAN_VIEN với điều kiện ChucVu = 'HLV'); {len(ENT_KET_HOP)} thực thể kết hợp có khóa riêng (DANG_KY_GOI nối HOI_VIEN – GOI_DICH_VU và đăng ký tại CHI_NHANH; CHECK_IN nối HOI_VIEN – CHI_NHANH, tùy chọn PHONG, và dùng một DANG_KY_GOI; LICH_HEN_PT nối HOI_VIEN – HUAN_LUYEN_VIEN – CHI_NHANH và thuộc một DANG_KY_GOI; LICH_SU_DIEU_CHUYEN nối NHAN_VIEN – CHI_NHANH theo thời gian); {len(ENT_NN)} quan hệ N–N có thuộc tính (CHI_NHANH_DICH_VU: TrangThai; TON_KHO: SoLuong, NgayCapNhat); và {len(ENT_YEU)} thực thể yếu (DIEM_LOYALTY: chủ HOI_VIEN, khóa bộ phận NamXet; CHI_TIET_HOA_DON: chủ HOA_DON, khóa bộ phận SoThuTu). Tổng cộng {len(ENT_THUONG)} + {len(ENT_LOP_CON)} + {len(ENT_KET_HOP)} + {len(ENT_NN)} + {len(ENT_YEU)} = {n_ent} thực thể."))
    o.append(p("Các quy ước riêng của ERD này: ThietBi là thuộc tính văn bản của CHECK_IN (không có thực thể THIET_BI); ERD không có KHUNG_GIO và không có bảo lưu gói; thuộc tính dẫn xuất viết trong ngoặc vuông ([Tuoi], [TongTienGoc], [ThanhToanThucTe], [ThanhTien], [NgayKetThuc]), thuộc tính đa trị trong ngoặc nhọn ({ChungChi}), khóa thay thế ghi (AK). THONG_KE_CHECKIN và DOANH_THU_NGAY là bảng dẫn xuất chỉ có ở mức logic (vấn đề 3), không vẽ trên ERD."))
    o.append(p(f"Bảng dưới liệt kê {n_lk} mối liên kết đếm trực tiếp từ hình ERD ({n_lk - 1} liên kết thông thường và 1 chuyên biệt hóa ký hiệu U). Quy ước đọc X ||--o< Y: ký hiệu ở đầu cạnh của thực thể nào cho biết số thể hiện của thực thể đó ứng với một thể hiện của thực thể kia, nên mỗi X có 0..N Y và mỗi Y thuộc đúng 1 X; cột Min..Max ghi lần lượt ký hiệu ở đầu cạnh phía Từ rồi phía Đến. Nét đứt (..) là liên kết định danh của thực thể yếu. Liên kết “xuất ra” ghi 0..N ở phía DANG_KY_GOI vì một dòng Gói có SoLuong = n sinh ra n bản ghi DANG_KY_GOI (RB08)."))
    rows = []
    for k, (lab, a, ca, b, cb, note, dashed) in enumerate(LINKS, 1):
        mm = "–" if ca is None else f"{ca} – {cb}"
        rows.append([str(k), lab, a, notation(ca, cb, dashed), b, mm, note])
    o.append(table([600, 2300, 2700, 1400, 2900, 1600, 3070],
                   ["#", "Mối liên kết", "Từ", "Ký hiệu", "Đến", "Min..Max (Từ – Đến)", "Ghi chú"], rows, center_cols=(0,), sz=24))
    o.append(p("", after=100))
    o.append(sect_break("landscape", "rId10"))
    return o


def conceptual2():
    o = [h2("3.2 Chú giải ký hiệu")]
    legend = [
        ["Đầu cạnh || (hai gạch)", "Đúng một (1..1)"],
        ["Đầu cạnh o| (vòng tròn + gạch)", "Không hoặc một (0..1)"],
        ["Đầu cạnh |< (gạch + chân chim)", "Một hoặc nhiều (1..N)"],
        ["Đầu cạnh o< (vòng tròn + chân chim)", "Không hoặc nhiều (0..N)"],
        ["Hộp nền xanh dương", "Thực thể thường (kể cả HUAN_LUYEN_VIEN, lớp con của chuyên biệt hóa)"],
        ["Hộp nền xanh lá, góc vuông / bo góc", "Thực thể kết hợp có khóa riêng (DANG_KY_GOI, CHECK_IN, LICH_HEN_PT, LICH_SU_DIEU_CHUYEN) / quan hệ N–N có thuộc tính (CHI_NHANH_DICH_VU, TON_KHO)"],
        ["Hộp nền cam, viền đôi", "Thực thể yếu (DIEM_LOYALTY, CHI_TIET_HOA_DON); mối liên kết định danh vẽ nét đứt (“tích lũy”, “gồm” với HOA_DON)"],
        ["Ký hiệu U (không có vòng tròn), nhãn ChucVu = 'HLV'", "Chuyên biệt hóa partial, một lớp con, d/o không áp dụng: HUAN_LUYEN_VIEN là tập con của NHAN_VIEN. Ba chức vụ còn lại (Lễ tân, Quản lý, Bán hàng) không có thuộc tính hay mối liên kết riêng nên không tách thành thực thể. Điều kiện của chuyên biệt hóa ghi trên hình là ChucVu = 'HLV'"],
        ["Tên thuộc tính gạch chân / (AK)", "Khóa chính (thực thể yếu: khóa bộ phận) / khóa thay thế (duy nhất). ERD không vẽ khóa ngoại: các mối liên kết đã thể hiện chúng, khóa ngoại xuất hiện ở lược đồ logic (mục 4.2)"],
        ["Tên(Thành phần), [Tên], {Tên}", "Thuộc tính tổng hợp (DiaChi, HoTen) / dẫn xuất / đa trị"],
    ]
    o.append(table([3200, 6438], ["Ký hiệu", "Ý nghĩa"], legend))
    o.append(p("", after=100))
    o.append(h2("3.3 Hình ERD"))
    o.append(p("Hình dưới là ERD gốc dùng làm nguồn chuẩn cho toàn bộ thiết kế (file CSDLA_v3.png và bản chỉnh sửa được CSDLA_v3.drawio nộp kèm). Các hình mô-đun của lược đồ quan hệ nằm ở mục 4.2.", keep=True))
    # ảnh 1572x2150: rộng 17,0 cm -> cao 23,25 cm
    cx = int(16.0 * 360000)
    from PIL import Image as _I
    _w, _h = _I.open(r"D:\HK1_Năm 3\CSDL Nâng cao - Pass hangvu@hcmus-20260913\Đồ án\CSDLA_v3.png").size
    cy = int(cx * _h / _w)
    o.append(image("rId9", cx, cy, "CSDLA_v3.png", "ERD gốc FitLife Hub (19 thực thể)"))
    return o


def constraints_34():
    o = [h2("3.4 Mô tả các ràng buộc chưa thể hiện trên ERD", page_break=True)]
    o.append(p("Các điều kiện dưới đây có trong đặc tả/quy trình nhưng ký hiệu ERD không biểu diễn được; chúng được hình thức hóa ở mục 4.5 (cột cuối là mã ràng buộc). Bản số tối thiểu 1 của “gồm” (mỗi hóa đơn có ít nhất một dòng, RB14) đã có trên ERD và chỉ cần kiểm tra khi cài đặt nên không nằm trong bảng."))
    rows = [
        ["Giờ mở cửa nhỏ hơn giờ đóng cửa", "CHI_NHANH", "ERD không có ràng buộc so sánh giữa hai thuộc tính", "RB01"],
        ["Miền giá trị: TrangThai, HinhThucThanhToan, ChucVu, Loai, GioiTinh thuộc tập cố định; số lượng, giá, sức chứa, điểm không âm; Diem từ 1 đến 5; ThoiGianRa sau ThoiGianVao", "HOI_VIEN, HOA_DON, NHAN_VIEN, CHI_TIET_HOA_DON, PHONG, DANH_GIA_PT, CHECK_IN và các bảng khác", "ERD không ghi miền giá trị của thuộc tính; SQL Server không có ENUM nên cài bằng CHECK", "RB02"],
        ["Khóa thay thế cho phép NULL (Email, CCCD, SoDienThoai của nhân viên) vẫn phải duy nhất khi có giá trị", "HOI_VIEN, NHAN_VIEN", "ERD ký hiệu (AK) nhưng không phân biệt thuộc tính tùy chọn; UNIQUE thường của SQL Server chỉ cho một NULL", "RB03"],
        ["Hạng và điểm Loyalty theo năm: tổng chi tiêu năm, điểm = ⌊ThanhToanThucTe / 100.000⌋ mỗi hóa đơn, hạng ứng với ngưỡng; cộng thêm khi thanh toán, trừ ngược khi hủy", "DIEM_LOYALTY, HOA_DON, HANG_HOI_VIEN", "Giá trị tổng hợp theo thời gian từ thực thể khác, ERD không có công thức", "RB04"],
        ["Mỗi hội viên có dòng DIEM_LOYALTY của năm hiện tại; dòng năm mới tạo sẵn vào 1/1", "HOI_VIEN, DIEM_LOYALTY", "Bản số 0..N của “tích lũy” không buộc phải có dòng của năm hiện tại", "RB05"],
        ["Ngưỡng chi tiêu của các hạng khác nhau và có đúng một hạng ngưỡng 0", "HANG_HOI_VIEN", "Ràng buộc liên bộ trên giá trị thuộc tính", "RB06"],
        ["Dòng chi tiết hóa đơn là gói hoặc sản phẩm, không cả hai, khớp với Loai", "CHI_TIET_HOA_DON, GOI_DICH_VU, SAN_PHAM", "Hai liên kết “gồm” đều 0..1 phía gói/sản phẩm nhưng ERD không ghi loại trừ lẫn nhau", "RB07"],
        ["Số DANG_KY_GOI sinh ra từ một dòng Gói bằng SoLuong, cùng MaGoi với dòng; dòng Sản phẩm không sinh gói", "DANG_KY_GOI, CHI_TIET_HOA_DON", "Ràng buộc đếm và đồng nhất giá trị giữa hai thực thể", "RB08"],
        ["Tiền hóa đơn: TongTienGoc = Σ ThanhTien, 0 ≤ GiamGia ≤ TongTienGoc, ThanhToanThucTe = TongTienGoc − GiamGia", "HOA_DON, CHI_TIET_HOA_DON", "Thuộc tính dẫn xuất [ ] không kèm công thức", "RB09"],
        ["ThanhTien = SoLuong × DonGia; DonGia là giá chốt lúc bán, chỉ bán gói/sản phẩm đang bán", "CHI_TIET_HOA_DON, GOI_DICH_VU, SAN_PHAM", "Thuộc tính dẫn xuất và ràng buộc giá trị theo thời điểm", "RB10"],
        ["NgayKetThuc = NgayBatDau + ThoiHanThang tháng; trạng thái gói không có bảo lưu", "DANG_KY_GOI, GOI_DICH_VU", "Thuộc tính dẫn xuất phụ thuộc thực thể khác", "RB11"],
        ["Đăng ký gói cùng hội viên và cùng chi nhánh với hóa đơn đã thanh toán nó; hủy hóa đơn thì hủy gói", "DANG_KY_GOI, HOA_DON, CHI_TIET_HOA_DON", "Dư thừa có chủ đích: hai đường nối tới HOI_VIEN và CHI_NHANH phải cho cùng kết quả", "RB12"],
        ["Chi nhánh của hóa đơn là chi nhánh nhân viên lập đang công tác vào ngày lập", "HOA_DON, NHAN_VIEN, LICH_SU_DIEU_CHUYEN", "Ràng buộc theo thời gian giữa nhiều thực thể", "RB13"],
        ["Mỗi hội viên tối đa một lượt check-in chưa check-out", "CHECK_IN", "Duy nhất có điều kiện (ThoiGianRa IS NULL)", "RB15"],
        ["Check-in chỉ khi gói 'Hoạt động' còn hạn tại thời điểm vào; xác thực dưới 50 ms", "CHECK_IN, DANG_KY_GOI", "Ràng buộc thời gian giữa hai thực thể và yêu cầu hiệu năng", "RB16"],
        ["MaHV của CHECK_IN bằng hội viên của gói; MaCN bằng chi nhánh của phòng khi có phòng", "CHECK_IN, DANG_KY_GOI, PHONG", "Dư thừa có chủ đích: nhiều đường nối tới cùng thực thể", "RB17"],
        ["MaHV của LICH_HEN_PT bằng hội viên của gói", "LICH_HEN_PT, DANG_KY_GOI", "Dư thừa có chủ đích: hai đường nối tới HOI_VIEN", "RB18"],
        ["Chống overbooking: mọi lịch dài 60 phút, bắt đầu tròn giờ; một HLV và một hội viên không có hai lịch chưa hủy cùng thời điểm", "LICH_HEN_PT", "Duy nhất có điều kiện (TrangThai ≠ 'Hủy') và ràng buộc khoảng thời gian", "RB19"],
        ["Số lịch 'Đã đặt' không vượt BuoiConLai; BuoiConLai = SoBuoi − số lịch đã hoàn thành", "LICH_HEN_PT, DANG_KY_GOI, GOI_DICH_VU", "Ràng buộc đếm giữa các thực thể", "RB20"],
        ["Chi nhánh của buổi hẹn là chi nhánh HLV công tác vào ngày hẹn; giờ hẹn trong giờ mở cửa", "LICH_HEN_PT, LICH_SU_DIEU_CHUYEN, CHI_NHANH", "Ràng buộc theo thời gian giữa nhiều thực thể", "RB21"],
        ["Mỗi lịch tối đa một đánh giá và chỉ lịch 'Đã hoàn thành' mới được đánh giá", "DANH_GIA_PT, LICH_HEN_PT", "Phụ thuộc vào giá trị trạng thái của thực thể khác", "RB22"],
        ["Các giai đoạn công tác của một nhân viên liên tiếp, không chồng lấn, tối đa một bản ghi đang mở, bản ghi đầu = ngày vào làm", "LICH_SU_DIEU_CHUYEN, NHAN_VIEN", "Ràng buộc thời gian động, ERD không có ký hiệu", "RB23"],
        ["NHAN_VIEN.MaCN (chi nhánh hiện tại) bằng chi nhánh của bản ghi đang mở; nghỉ việc thì đóng bản ghi", "NHAN_VIEN, LICH_SU_DIEU_CHUYEN", "Dư thừa có chủ đích giữa “làm việc tại” và “được điều chuyển”", "RB24"],
        ["Hoa hồng PT tính theo chi nhánh của từng giai đoạn, không theo chi nhánh hiện tại", "LICH_HEN_PT, LICH_SU_DIEU_CHUYEN, HUAN_LUYEN_VIEN", "Quy tắc tổng hợp theo thời gian (vấn đề 5)", "RB25"],
        ["ChucVu = 'HLV' khi và chỉ khi nhân viên có bản ghi HUAN_LUYEN_VIEN", "NHAN_VIEN, HUAN_LUYEN_VIEN", "Điều kiện xác định (predicate) của chuyên biệt hóa theo giá trị thuộc tính", "RB26"],
        ["Số người đang có mặt và tỷ lệ lấp đầy khớp dữ liệu CHECK_IN và SucChua", "THONG_KE_CHECKIN, CHECK_IN, PHONG", "Bảng dẫn xuất chỉ có ở mức logic, không có trên ERD", "RB27"],
        ["Doanh thu ngày khớp hóa đơn 'Đã thanh toán'", "DOANH_THU_NGAY, HOA_DON", "Bảng dẫn xuất chỉ có ở mức logic, không có trên ERD", "RB28"],
        ["Mỗi chi nhánh có đúng một quản lý (đề không nêu, chờ xác nhận)", "CHI_NHANH, NHAN_VIEN", "Ràng buộc đếm có điều kiện trên giá trị thuộc tính", "RB29"],
        ["Chi nhánh chỉ bán gói và có phòng thuộc loại dịch vụ mà chi nhánh cung cấp (kế thừa v2, chờ xác nhận)", "DANG_KY_GOI, PHONG, CHI_NHANH_DICH_VU", "Ràng buộc tham chiếu miền giữa nhiều thực thể", "RB30"],
    ]
    o.append(table([3300, 2500, 2638, 1200], ["Ràng buộc", "Thực thể liên quan", "Lý do không biểu diễn được trên ERD", "Mã"], rows))
    return o


def build_part1_front():
    """Phần đầu: Tổng quan → hết mục 3.1 (kết thúc phân đoạn ngang)."""
    return overview() + qt() + freq() + conceptual()


def build_part1_back():
    """3.2 → 3.4 (phân đoạn dọc)."""
    return conceptual2() + constraints_34()
