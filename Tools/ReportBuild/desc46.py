"""Mô tả quan hệ/thuộc tính (mục 4.6): intro + {cột: (ràng buộc bổ sung, mô tả)}. Kiểu và NULL lấy từ DBML."""

D46 = {}


def t(name, intro, cols):
    D46[name] = (intro, cols)


t("CHI_NHANH", "Chi nhánh của hệ thống (12 chi nhánh). Thực thể thường; thuộc tính tổng hợp DiaChi tách thành bốn thành phần.", [
    ("MaCN", "", "Mã chi nhánh, khóa chính"),
    ("TenCN", "", "Tên chi nhánh"),
    ("SoNha", "", "Số nhà (thành phần của DiaChi)"),
    ("Duong", "", "Tên đường (thành phần của DiaChi)"),
    ("Quan", "", "Quận/huyện (thành phần của DiaChi)"),
    ("ThanhPho", "", "Thành phố (thành phần của DiaChi)"),
    ("SoDienThoai", "UNIQUE (AK, RB03)", "Số điện thoại của chi nhánh; khóa thay thế"),
    ("GioMoCua", "< GioDongCua (RB01)", "Giờ mở cửa; chi nhánh không mở qua nửa đêm"),
    ("GioDongCua", "", "Giờ đóng cửa"),
])
t("LOAI_DICH_VU", "Danh mục loại dịch vụ/tiện ích dùng chung cho dịch vụ của chi nhánh, loại gói và loại phòng: Gym, Yoga, GroupX, PT 1-1, Spa, Sauna, Cửa hàng. Thực thể thường, thay đổi hiếm.", [
    ("MaLoai", "", "Mã loại dịch vụ, khóa chính"),
    ("TenLoai", "UNIQUE (AK, RB03)", "Tên loại, ví dụ Gym, Yoga, PT 1-1, Spa; khóa thay thế"),
    ("MoTa", "", "Mô tả ngắn của loại dịch vụ; NULL nếu chưa có"),
])
t("CHI_NHANH_DICH_VU", "Dịch vụ/tiện ích mà từng chi nhánh cung cấp (quan hệ N–N có thuộc tính giữa CHI_NHANH “cung cấp” và LOAI_DICH_VU “được cung cấp”).", [
    ("MaCN", "", "Chi nhánh cung cấp dịch vụ"),
    ("MaLoai", "", "Loại dịch vụ được cung cấp"),
    ("TrangThai", "IN ('Hoạt động','Tạm ngưng') (RB02)", "Trạng thái cung cấp tại chi nhánh (tập giá trị do nhóm đề xuất, ERD không nêu)"),
])
t("PHONG", "Phòng/khu vực tập của chi nhánh. Tổng SucChua các phòng đang hoạt động là mẫu số của tỷ lệ lấp đầy (RB27).", [
    ("MaPhong", "UNIQUE (MaPhong, MaCN)", "Mã phòng, khóa chính; cặp (MaPhong, MaCN) là đích của khóa ngoại phức hợp từ CHECK_IN (RB17)"),
    ("MaCN", "", "Chi nhánh có phòng (“có phòng”, 1..N); với chi nhánh mới phải thêm ít nhất một phòng"),
    ("MaLoai", "", "Loại phòng (Gym/Yoga/GroupX…) (“loại phòng”); nên thuộc dịch vụ chi nhánh có (RB30, chờ xác nhận)"),
    ("TenPhong", "", "Tên phòng"),
    ("SucChua", "> 0 (RB02)", "Số người tối đa của phòng"),
    ("ConHoatDong", "1 = đang hoạt động", "Cờ phòng đang hoạt động; chỉ phòng hoạt động tính vào mẫu số lấp đầy"),
])
t("GOI_DICH_VU", "Gói dịch vụ có thể bán: gói Gym/Yoga theo tháng, gói PT 1-1 theo số buổi, vé Spa lẻ.", [
    ("MaGoi", "", "Mã gói, khóa chính"),
    ("TenGoi", "", "Tên gói"),
    ("MaLoai", "", "Loại dịch vụ của gói (“phân loại”): Gym / Yoga / PT 1-1 / Spa"),
    ("ThoiHanThang", "> 0 (RB02)", "Thời hạn hiệu lực (tháng), kể cả vé Spa lẻ; đề nêu 3, 6 hoặc 12 tháng"),
    ("SoBuoi", ">= 0 (RB02)", "Số buổi PT của gói; 0 nghĩa là gói không có buổi PT"),
    ("GiaTien", ">= 0 (RB02)", "Giá bán hiện hành (VNĐ); giá chốt được lưu ở CHI_TIET_HOA_DON.DonGia"),
    ("ConHieuLuc", "1 = còn được bán", "Cờ gói còn được bán"),
])
t("SAN_PHAM", "Sản phẩm bán lẻ tại cửa hàng của chi nhánh (thực phẩm bổ sung, phụ kiện tập luyện). Thực thể thường.", [
    ("MaSP", "", "Mã sản phẩm, khóa chính"),
    ("TenSP", "", "Tên sản phẩm"),
    ("GiaBan", ">= 0 (RB02)", "Giá bán hiện hành (VNĐ)"),
    ("Loai", "", "Nhóm sản phẩm: Whey protein, bình nước, thảm yoga…"),
    ("DonViTinh", "", "Đơn vị tính số lượng bán và tồn: hộp, chai, cái, gói…"),
    ("ConBan", "1 = còn kinh doanh", "Cờ sản phẩm còn được bán"),
])
t("TON_KHO", "Số lượng tồn của sản phẩm tại từng chi nhánh (quan hệ N–N có thuộc tính giữa SAN_PHAM “tồn kho” và CHI_NHANH “lưu kho”).", [
    ("MaCN", "", "Chi nhánh lưu kho"),
    ("MaSP", "", "Sản phẩm được lưu"),
    ("SoLuong", ">= 0 (RB02)", "Số lượng tồn theo DonViTinh; CHECK chặn bán vượt tồn"),
    ("NgayCapNhat", "", "Thời điểm cập nhật tồn gần nhất (bán, nhập hàng, kiểm kê)"),
])
t("HANG_HOI_VIEN", "Danh mục hạng thành viên (Silver, Gold, Platinum) kèm ngưỡng chi tiêu năm. Thực thể thường, 3 dòng.", [
    ("MaHang", "", "Mã hạng, khóa chính"),
    ("TenHang", "UNIQUE (AK, RB03)", "Tên hạng: Silver, Gold, Platinum"),
    ("NguongChiTieu", ">= 0 (RB02); UNIQUE (RB06)", "Tổng chi tiêu năm tối thiểu (VNĐ) để đạt hạng; Silver có ngưỡng 0"),
])
t("HOI_VIEN", "Hội viên (khách hàng). Thực thể thường; HoTen tách thành Ho, TenDem, Ten; Tuoi là thuộc tính dẫn xuất không lưu. Hạng và điểm nằm ở DIEM_LOYALTY, không nằm ở đây.", [
    ("MaHV", "", "Mã hội viên, khóa chính"),
    ("Ho", "", "Họ (thành phần của HoTen)"),
    ("TenDem", "", "Tên đệm (thành phần của HoTen); NULL nếu không có"),
    ("Ten", "", "Tên (thành phần của HoTen)"),
    ("SoDienThoai", "UNIQUE (AK, RB03)", "Số điện thoại, khóa thay thế"),
    ("Email", "unique filtered (AK, RB03)", "Email; NULL nếu hội viên không cung cấp, duy nhất khi có giá trị"),
    ("CCCD", "unique filtered (AK, RB03)", "Căn cước công dân gồm đúng 12 ký tự; NULL nếu chưa cung cấp (ví dụ khách nước ngoài), duy nhất khi có giá trị"),
    ("GioiTinh", "IN ('Nam','Nữ','Khác') (RB02)", "Giới tính"),
    ("NgaySinh", "<= NgayDangKy (RB02)", "Ngày sinh; Tuoi tính từ đây bằng view/hàm, không lưu"),
    ("NgayDangKy", "", "Ngày đăng ký hội viên"),
])
t("DIEM_LOYALTY", "Điểm thưởng và hạng của hội viên theo từng năm dương lịch (thực thể yếu của HOI_VIEN, liên kết “tích lũy”; “xếp hạng” tới HANG_HOI_VIEN). Mỗi hội viên mỗi năm một dòng; hạng hiện tại là MaHang của dòng năm hiện tại (RB04, RB05).", [
    ("MaHV", "", "Hội viên chủ (khóa của thực thể chủ)"),
    ("NamXet", "BETWEEN 2000 AND 2100 (RB02)", "Năm dương lịch xét hạng (khóa bộ phận)"),
    ("TongChiTieuNam", ">= 0 (RB02)", "Tổng ThanhToanThucTe các hóa đơn đã thanh toán trong năm (VNĐ); cập nhật tăng dần, không quét lại hóa đơn"),
    ("DiemThuong", ">= 0 (RB02)", "Điểm Loyalty của năm: cộng ⌊ThanhToanThucTe / 100.000⌋ mỗi hóa đơn (1 điểm = 100.000 VNĐ); tổng điểm hiện có là tổng DiemThuong các năm"),
    ("NgayCapNhat", "", "Thời điểm cập nhật gần nhất của dòng"),
    ("MaHang", "", "Hạng của năm NamXet, suy ra từ TongChiTieuNam và ngưỡng; lưu có chủ đích để đọc hạng bằng một lần tra khóa chính (vấn đề 4)"),
])
t("NHAN_VIEN", "Nhân viên (lớp cha của chuyên biệt hóa). ChucVu phân biệt 4 chức vụ; chỉ HUAN_LUYEN_VIEN có thuộc tính và liên kết riêng nên tách thành quan hệ con. MaCN là chi nhánh hiện tại.", [
    ("MaNV", "", "Mã nhân viên, khóa chính"),
    ("Ho", "", "Họ (thành phần của HoTen)"),
    ("TenDem", "", "Tên đệm; NULL nếu không có"),
    ("Ten", "", "Tên"),
    ("SoDienThoai", "unique filtered (AK, RB03)", "Số điện thoại; NULL nếu chưa có, duy nhất khi có giá trị"),
    ("ChucVu", "IN ('HLV','Lễ tân','Quản lý','Bán hàng') (RB02)", "Chức vụ; 'HLV' khi và chỉ khi có dòng ở HUAN_LUYEN_VIEN (RB26)"),
    ("LuongCoBan", ">= 0 (RB02)", "Lương cơ bản (VNĐ)"),
    ("MaCN", "", "Chi nhánh hiện tại (“làm việc tại”); khớp bản ghi đang mở của LICH_SU_DIEU_CHUYEN khi ConLamViec = 1 (RB24)"),
    ("NgayVaoLam", "", "Ngày vào làm; bằng NgayBatDau của bản ghi điều chuyển đầu tiên (RB23)"),
    ("ConLamViec", "1 = đang làm việc", "Cờ đang làm việc; 0 sau khi nghỉ việc"),
])
t("HUAN_LUYEN_VIEN", "Lớp con của NHAN_VIEN có ChucVu = 'HLV' (chuyên biệt hóa partial, một lớp con, d/o không áp dụng, ký hiệu U).", [
    ("MaHLV", "", "Nhân viên là HLV; vừa là khóa chính vừa là khóa ngoại tới NHAN_VIEN.MaNV"),
    ("ChuyenMon", "", "Chuyên môn: Gym, Yoga, HIIT…"),
    ("HoaHongMoiBuoi", ">= 0 (RB02)", "Hoa hồng cho mỗi buổi PT hoàn thành (VNĐ)"),
])
t("HLV_CHUNG_CHI", "Thuộc tính đa trị {ChungChi} của HUAN_LUYEN_VIEN tách thành quan hệ riêng (ERD không có thực thể riêng).", [
    ("MaHLV", "", "HLV sở hữu chứng chỉ"),
    ("ChungChi", "", "Tên chứng chỉ; mỗi HLV có nhiều chứng chỉ khác nhau"),
])
t("LICH_SU_DIEU_CHUYEN", "Quá trình công tác của nhân viên theo chi nhánh và khoảng thời gian (thực thể kết hợp NHAN_VIEN – CHI_NHANH; vấn đề 5). Mỗi nhân viên có ít nhất một bản ghi; bản ghi đang mở có NgayKetThuc IS NULL.", [
    ("MaDieuChuyen", "", "Mã bản ghi điều chuyển, khóa chính"),
    ("MaNV", "UNIQUE (MaNV, NgayBatDau)", "Nhân viên được điều chuyển (“được điều chuyển”)"),
    ("MaCN", "", "Chi nhánh đích của giai đoạn (“tiếp nhận”)"),
    ("NgayBatDau", "", "Ngày bắt đầu công tác tại chi nhánh (độ mịn theo ngày); bản ghi đầu bằng NgayVaoLam (RB23)"),
    ("NgayKetThuc", ">= NgayBatDau khi có (RB02)", "Ngày kết thúc (đóng hai đầu); NULL nghĩa là đang công tác tại chi nhánh này, tối đa một bản ghi mỗi nhân viên (RB23)"),
    ("LyDo", "", "Lý do điều chuyển; 'Vào làm' cho bản ghi đầu; NULL nếu không ghi"),
])
t("HOA_DON", "Hóa đơn bán gói và sản phẩm cho hội viên, do một nhân viên lập tại một chi nhánh. TongTienGoc và ThanhToanThucTe là thuộc tính dẫn xuất được lưu có chủ đích (RB09).", [
    ("MaHD", "", "Mã hóa đơn, khóa chính"),
    ("NgayLap", "", "Thời điểm lập hóa đơn; năm của NgayLap quyết định dòng DIEM_LOYALTY được cộng (RB04)"),
    ("MaNV", "", "Nhân viên lập (“lập”); phải đang công tác tại MaCN vào ngày lập (RB13)"),
    ("MaHV", "", "Hội viên thanh toán (“Thanh toán”); bản số ERD bắt buộc có hội viên"),
    ("MaCN", "", "Chi nhánh lập hóa đơn (“lập tại”)"),
    ("TongTienGoc", "= Σ ThanhTien (RB09)", "Dẫn xuất [x], lưu: tổng thành tiền các dòng trước giảm giá (VNĐ)"),
    ("GiamGia", "0 <= GiamGia <= TongTienGoc (RB09)", "Số tiền giảm giá (VNĐ)"),
    ("ThanhToanThucTe", "cột tính PERSISTED (RB09)", "Dẫn xuất [x], lưu: TongTienGoc − GiamGia, số tiền khách trả; đầu vào của điểm Loyalty và doanh thu"),
    ("HinhThucThanhToan", "IN ('Tiền mặt','VNPay','Thẻ') (RB02)", "Hình thức thanh toán"),
    ("TrangThai", "IN ('Đã thanh toán','Hủy') (RB02)", "Trạng thái hóa đơn; chỉ 'Đã thanh toán' tính vào doanh thu và Loyalty"),
])
t("CHI_TIET_HOA_DON", "Dòng chi tiết của hóa đơn (thực thể yếu của HOA_DON, liên kết “gồm”): mỗi dòng là một gói hoặc một sản phẩm. Dòng Gói có SoLuong = n sinh ra n bản ghi DANG_KY_GOI (RB08).", [
    ("MaHD", "", "Hóa đơn chủ (khóa của thực thể chủ)"),
    ("SoThuTu", "", "Số thứ tự dòng trong hóa đơn (khóa bộ phận); UNIQUE (MaHD, SoThuTu, MaGoi) làm đích khóa ngoại phức hợp của DANG_KY_GOI"),
    ("Loai", "IN ('Gói','Sản phẩm') (RB02)", "Loại dòng; quyết định MaGoi hay MaSP có giá trị (RB07)"),
    ("MaGoi", "NULL khi Loai = 'Sản phẩm' (RB07)", "Gói được bán (“gồm” với GOI_DICH_VU, 0..1)"),
    ("MaSP", "NULL khi Loai = 'Gói' (RB07)", "Sản phẩm được bán (“gồm” với SAN_PHAM, 0..1)"),
    ("SoLuong", "> 0 (RB02)", "Số lượng; với dòng Gói là số DANG_KY_GOI sinh ra (RB08), với dòng Sản phẩm là số đơn vị bán"),
    ("DonGia", ">= 0 (RB02, RB10)", "Giá chốt tại lúc bán (VNĐ), không đổi sau khi lập"),
    ("ThanhTien", "cột tính PERSISTED (RB10)", "Dẫn xuất [x], lưu: SoLuong × DonGia (VNĐ)"),
])
t("DANG_KY_GOI", "Gói hội viên đã mua (thực thể kết hợp HOI_VIEN – GOI_DICH_VU, đăng ký tại CHI_NHANH, xuất ra từ một dòng CHI_TIET_HOA_DON); cơ sở kiểm tra quyền check-in và đặt lịch PT.", [
    ("MaDK", "UNIQUE (MaDK, MaHV)", "Mã đăng ký, khóa chính; cặp (MaDK, MaHV) là đích của khóa ngoại phức hợp từ CHECK_IN và LICH_HEN_PT (RB17, RB18)"),
    ("MaHV", "", "Hội viên sở hữu gói (“đăng ký”); bằng HOA_DON.MaHV (RB12)"),
    ("MaGoi", "", "Gói đã mua (“được đăng ký”); dư thừa có chủ đích, phải trùng MaGoi của dòng chi tiết (RB08)"),
    ("MaCN", "", "Chi nhánh đăng ký (“đăng ký tại”); bằng HOA_DON.MaCN (RB12)"),
    ("MaHD", "", "Hóa đơn đã thanh toán gói này; một nửa khóa ngoại ghép (MaHD, SoThuTu) (“xuất ra”)"),
    ("SoThuTu", "", "Dòng chi tiết của hóa đơn sinh ra gói; nửa còn lại của khóa ngoại ghép"),
    ("NgayBatDau", "", "Ngày bắt đầu hiệu lực (mặc định ngày mua)"),
    ("NgayKetThuc", "> NgayBatDau (RB02)", "Dẫn xuất [x], lưu: NgayBatDau + ThoiHanThang tháng (RB11); dùng trong chỉ mục xác thực check-in"),
    ("TrangThai", "IN ('Hoạt động','Hết hạn','Hủy') (RB02)", "Trạng thái gói; không có bảo lưu"),
    ("BuoiConLai", ">= 0 (RB02)", "Số buổi PT còn lại; bằng SoBuoi của gói trừ số lịch đã hoàn thành (RB20); 0 với gói không có buổi PT"),
])
t("CHECK_IN", "Lượt check-in/check-out của hội viên tại một chi nhánh (thực thể kết hợp); bảng ghi nhiều nhất (≈420.000 dòng/tháng), ứng viên phân vùng theo ThoiGianVao ở giai đoạn 2.", [
    ("MaCheckIn", "", "Mã lượt check-in, khóa chính"),
    ("MaHV", "", "Hội viên (“check-in”); bằng hội viên của gói MaDK (RB17)"),
    ("MaCN", "", "Chi nhánh ghi nhận lượt (“ghi nhận tại”); bằng PHONG.MaCN khi có MaPhong (RB17), không buộc bằng chi nhánh đăng ký gói"),
    ("MaPhong", "NULL = không vào phòng cụ thể", "Phòng hội viên vào (“vào phòng”, 0..1)"),
    ("MaDK", "", "Gói dùng để vào (“được dùng”); chọn bởi xác thực (RB16)"),
    ("ThoiGianVao", "", "Thời điểm vào; ứng viên khóa phân vùng"),
    ("ThoiGianRa", "> ThoiGianVao khi có (RB02); unique filtered theo MaHV khi NULL (RB15)", "Thời điểm ra; NULL nếu chưa ra"),
    ("ThietBi", "", "Tên cửa/thiết bị quét, thuộc tính văn bản (không có thực thể THIET_BI); không tham gia xác thực"),
])
t("LICH_HEN_PT", "Lịch hẹn tập PT 1-1 (thực thể kết hợp HOI_VIEN – HUAN_LUYEN_VIEN – CHI_NHANH, thuộc một DANG_KY_GOI). Mỗi lịch dài 60 phút, bắt đầu tròn giờ (RB19).", [
    ("MaLichHen", "", "Mã lịch hẹn, khóa chính"),
    ("MaHV", "UNIQUE filtered (MaHV, NgayGioHen) WHERE TrangThai <> 'Hủy' (RB19)", "Hội viên đặt lịch (“đặt lịch”); bằng hội viên của gói MaDK (RB18)"),
    ("MaHLV", "UNIQUE filtered (MaHLV, NgayGioHen) WHERE TrangThai <> 'Hủy' (RB19)", "HLV phụ trách (“phụ trách”)"),
    ("MaCN", "", "Chi nhánh buổi tập (“diễn ra tại”); là chi nhánh HLV công tác vào ngày hẹn (RB21)"),
    ("MaDK", "", "Gói PT được dùng (“thuộc”); số lịch 'Đã đặt' không vượt BuoiConLai (RB20)"),
    ("NgayGioHen", "phút 00, giây 00 (RB19)", "Thời điểm bắt đầu buổi tập"),
    ("ThoiLuong", "= 60 (RB19)", "Thời lượng buổi tập (phút)"),
    ("TrangThai", "IN ('Đã đặt','Đã hoàn thành','Hủy') (RB02)", "Trạng thái lịch; 'Hủy' giải phóng giờ hẹn"),
])
t("DANH_GIA_PT", "Đánh giá của hội viên cho một buổi PT (liên kết 1 – (0..1) với LICH_HEN_PT, “được đánh giá”).", [
    ("MaDanhGia", "", "Mã đánh giá, khóa chính"),
    ("MaLichHen", "UNIQUE (AK, RB22)", "Buổi PT được đánh giá; chỉ lịch 'Đã hoàn thành', tối đa một đánh giá mỗi lịch"),
    ("Diem", "BETWEEN 1 AND 5 (RB02)", "Điểm đánh giá"),
    ("NhanXet", "", "Nhận xét tự do; NULL nếu hội viên chỉ chấm điểm"),
    ("NgayDanhGia", ">= NgayGioHen của lịch (RB22)", "Thời điểm đánh giá"),
])
t("THONG_KE_CHECKIN", "Bảng dẫn xuất từ CHECK_IN (không phải thực thể trên ERD), cập nhật bằng trigger/job; phục vụ báo cáo check-in theo khung giờ và tỷ lệ lấp đầy (vấn đề 3, RB27).", [
    ("MaCN", "", "Chi nhánh"),
    ("Ngay", "", "Ngày"),
    ("Gio", "0–23", "Giờ trong ngày"),
    ("SoLuotVao", "", "Số lượt check-in có ThoiGianVao trong giờ này"),
    ("SoLuotRa", "", "Số lượt có ThoiGianRa trong giờ này; người có mặt = Σ (SoLuotVao − SoLuotRa) cộng dồn (RB27)"),
])
t("DOANH_THU_NGAY", "Bảng dẫn xuất từ HOA_DON có TrangThai = 'Đã thanh toán' (không phải thực thể trên ERD); phục vụ báo cáo doanh thu theo ngày/tháng/quý/năm (vấn đề 3, RB28).", [
    ("MaCN", "", "Chi nhánh"),
    ("Ngay", "", "Ngày lập hóa đơn"),
    ("TongTien", "", "Tổng ThanhToanThucTe của các hóa đơn đã thanh toán trong ngày (VNĐ)"),
    ("SoHoaDon", "", "Số hóa đơn đã thanh toán trong ngày"),
])
