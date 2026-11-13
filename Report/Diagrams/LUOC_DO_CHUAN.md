# Lược đồ quan hệ chuẩn – FitLife Hub (SQL Server)

Nguồn chuẩn: ảnh ERD `CSDLA_v3.png` (19 thực thể). Tài liệu này là **tài liệu gốc cho các bước sau** (dạng chuẩn, vật lý, báo cáo).
Các khối "tự động" (lược đồ, bảng FK, thống kê, nhật ký kiểm tra) do `sinh_tai_lieu.py` sinh từ `schema.py`, cùng nguồn với hình vẽ nên không thể lệch nhau.

## 0. Tóm tắt

- **Đối chiếu ảnh ERD với bản mô tả**: không có chỗ nào lệch về thực thể, thuộc tính, bản số, tên gọi. Chỗ duy nhất cần sửa là nhãn `ChucVu = 'PT'` trên ERD thành `'HLV'` (E8, đã chốt).
- **Sơ đồ cũ (`luoc_do_quan_he.png`) về cơ bản đúng**: cùng 20 quan hệ, cùng 33 khóa ngoại, đúng hướng mũi tên. Khác biệt thật nằm ở 5 chỗ tên/khóa (mục 2: SoBuoi, MaHLV ×3, MaCN) cộng với việc hình cũ không thể hiện UNIQUE, thuộc tính dẫn xuất, kiểu dữ liệu, NULL. Phần còn lại là bố cục (70 giao cắt ở hình cũ; hình tổng mới 62, ba hình mô-đun mỗi hình ≤ 3).
- **Không cần sửa ERD** để đáp ứng vấn đề 1–5. Mục 7 chỉ có 2 đề xuất, đều không bắt buộc.
- Tất cả lựa chọn của tôi nằm ở mục 8 (bảng "Quyết định cần xác nhận"), việc cần bạn xem trước là D1, D4, D6, D12, D13.

## 1. Bước 1 – Dẫn xuất ERD → quan hệ

| Thành phần ERD | Quy tắc | Kết quả |
|---|---|---|
| 14 thực thể thường (CHI_NHANH, LOAI_DICH_VU, PHONG, GOI_DICH_VU, SAN_PHAM, HANG_HOI_VIEN, HOI_VIEN, DANG_KY_GOI, HOA_DON, NHAN_VIEN, LICH_SU_DIEU_CHUYEN, LICH_HEN_PT, DANH_GIA_PT, CHECK_IN) | 1 thực thể = 1 quan hệ | 14 quan hệ |
| DiaChi(SoNha, Duong, Quan, ThanhPho); HoTen(Ho, TenDem, Ten) ở HOI_VIEN và NHAN_VIEN | thuộc tính tổng hợp tách thành phần | 4 + 3 + 3 cột, không còn cột DiaChi/HoTen |
| CHI_NHANH_DICH_VU, TON_KHO (N-N có thuộc tính) | bảng khóa ghép + thuộc tính | PK (MaCN, MaLoai) và (MaCN, MaSP); 4 FK |
| DIEM_LOYALTY, CHI_TIET_HOA_DON (thực thể yếu) | khóa chủ + khóa bộ phận | PK (MaHV, NamXet) và (MaHD, SoThuTu); FK nằm trong PK |
| HUAN_LUYEN_VIEN (chuyên biệt hóa, ký hiệu U) | bảng con, PK = FK tới lớp cha | PK (MaHLV) = FK → NHAN_VIEN.MaNV |
| {ChungChi} đa trị | bảng riêng | HLV_CHUNG_CHI, PK (MaHLV, ChungChi) |
| 24 liên kết 1-N còn lại | FK ở phía N | 24 FK |
| DANH_GIA_PT – LICH_HEN_PT, 1 – (0..1) | FK + UNIQUE ở phía 0..1 | DANH_GIA_PT.MaLichHen FK + UNIQUE |
| **Tổng** | | **20 quan hệ, 33 FK** = 4 (N-N) + 2 (yếu) + 1 (U) + 1 (đa trị) + 1 (1-(0..1)) + 24 (1-N) |

## 2. Bước 2 – Khác biệt giữa sơ đồ hiện tại và lược đồ đúng theo ERD

So sánh `luoc_do_quan_he.png` (sinh từ `ve_luoc_do.py`) với ERD. Các phần **không** liệt kê dưới đây là khớp: 20 bảng, 33 FK, hướng mũi tên (từ FK đến PK), FK ghép (MaHD, SoThuTu) của DANG_KY_GOI gộp một đường, PK+FK của TON_KHO/CHI_NHANH_DICH_VU/DIEM_LOYALTY/CHI_TIET_HOA_DON, thành phần của DiaChi/HoTen, không có cột Tuoi, không có bảo lưu/KHUNG_GIO/THIET_BI.

| # | Vị trí | Hiện tại | Đúng theo ERD | Lý do |
|--:|---|---|---|---|
| 1 | GOI_DICH_VU, cột số buổi | `SoBuoiPT` | `SoBuoi` | ERD đặt tên SoBuoi; "PT" lấy từ chữ trong đề, không có trên ERD |
| 2 | HUAN_LUYEN_VIEN, khóa chính | `MaNV` (PK+FK) | `MaHLV` (PK+FK → NHAN_VIEN.MaNV) | E8 và quy tắc chuyên biệt hóa của bước 1: đổi mọi MaPT/MaNV của bảng con thành MaHLV |
| 3 | HLV_CHUNG_CHI | PK (`MaNV`, ChungChi); FK `MaNV` → HUAN_LUYEN_VIEN.`MaNV` | PK (`MaHLV`, ChungChi); FK `MaHLV` → HUAN_LUYEN_VIEN.`MaHLV` | Hệ quả của dòng 2; thuộc tính đa trị của HLV nên khóa theo MaHLV |
| 4 | LICH_HEN_PT, cột HLV | `MaPT` → HUAN_LUYEN_VIEN.`MaNV` | `MaHLV` → HUAN_LUYEN_VIEN.`MaHLV` | E8 (đổi MaPT thành MaHLV); mối liên kết "phụ trách" nối HUAN_LUYEN_VIEN |
| 5 | NHAN_VIEN, FK chi nhánh | `MaCN_HienTai` | `MaCN` | Mối liên kết "làm việc tại" 1-N đặt FK ở NHAN_VIEN; cùng tên khóa chủ như mọi bảng khác. Ý "hiện tại" ghi trong ràng buộc E6. *Chờ xác nhận D1, quay lại tên cũ chỉ là đổi một cột* |
| 6 | DANH_GIA_PT.MaLichHen | FK thường, hình không thể hiện UNIQUE | FK **+ UNIQUE** (NOT NULL), đánh dấu ◆ | Liên kết "được đánh giá" là 1 – (0..1): mỗi lịch tối đa một đánh giá |
| 7 | Cột AK/UNIQUE trên hình | không đánh dấu | ◆ cho TenLoai, TenHang, SoDienThoai, Email, CCCD, MaLichHen | ERD có (AK); SQL Server cần UNIQUE (filtered cho cột NULL) |
| 8 | Thuộc tính dẫn xuất [x] | TongTienGoc, ThanhToanThucTe, ThanhTien, NgayKetThuc vẽ như cột thường | vẽ `[tên]` và nêu cột nào lưu, cách duy trì | E5; ERD ký hiệu [x] |
| 9 | Thứ tự cột | SAN_PHAM: TenSP, Loai, DonViTinh, GiaBan, ConBan; DIEM_LOYALTY: MaHang trước NgayCapNhat | thứ tự ERD (TenSP, GiaBan, Loai, DonViTinh, ConBan); cột FK thêm sau khóa chính | chỉ thẩm mỹ, để đối chiếu từng dòng với ERD |
| 10 | Thông tin kiểu dữ liệu, NULL, CHECK, chỉ mục | không có (hình chỉ có tên cột) | đủ ở lược đồ văn bản (mục 4) | yêu cầu bước 4a |
| 11 | Nhãn trên ERD (không phải trên sơ đồ quan hệ) | `ChucVu = 'PT'` | `ChucVu = 'HLV'` | E8 |
| 12 | Bố cục | 70 giao cắt, 101 khúc gấp, nhiều đường dài băng ngang các hàng | xem mục 5 | bước 4b |

## 3. Bước 3 – Xử lý E1–E10 ở mức lược đồ

Không thêm cột nào ngoài ERD (chỉ thêm FK để biểu diễn mối liên kết). Mọi cơ chế bên dưới là ràng buộc/chỉ mục/trigger ở mức logic–vật lý.

| Điểm | Ở mức lược đồ (cột, khóa) | Ràng buộc / cơ chế cần cài ở bước sau |
|---|---|---|
| **E1** Hạng theo năm dương lịch | `DIEM_LOYALTY(MaHV PK+FK, NamXet PK, TongChiTieuNam, DiemThuong, NgayCapNhat, MaHang FK NOT NULL)`. `HOI_VIEN` không có cột hạng. `HANG_HOI_VIEN.NguongChiTieu` (Silver = 0) và UNIQUE(NguongChiTieu) để chi tiêu → hạng xác định | Thanh toán = **1 `UPDATE` theo khóa chính** `(MaHV, NamXet = YEAR(NgayLap))` `WITH (UPDLOCK, HOLDLOCK)`: cộng chi tiêu, cộng `FLOOR(ThanhToanThucTe/100000)` điểm, gán `MaHang` = hạng có ngưỡng lớn nhất ≤ tổng mới. Job 1/1 tạo sẵn dòng năm mới (Silver, 0); hội viên mới có dòng khi đăng ký. Hủy hóa đơn: trừ ngược đúng dòng năm lập hóa đơn, tính lại hạng, CHECK ≥ 0 chặn âm. **Hạng hiện tại** = `MaHang` của dòng `NamXet = YEAR(GETDATE())`. *Giả định: "trong năm" = năm dương lịch; "12 tháng qua" ở vấn đề 4 là cách tính của hệ thống cũ.* Dự phòng nếu giảng viên đòi 12 tháng trượt: đổi `NamXet` thành `NamThang`, hạng = tổng tối đa 12 dòng tháng |
| **E2** Overbooking | `LICH_HEN_PT(MaLichHen, MaHV, MaHLV, MaCN, MaDK, NgayGioHen, ThoiLuong, TrangThai)` | Xem E7: `ThoiLuong = 60`, bắt đầu tròn giờ ⇒ chồng khoảng ⇔ trùng `NgayGioHen`, nên **unique filtered index** là đủ, không cần trigger kiểm tra chồng khoảng. Nếu sau này ThoiLuong thành tập giá trị (30/60/90) thì phải thêm trigger kiểm tra `NgayGioHen < ketthuc_khac AND ketthuc > NgayGioHen` với UPDLOCK. Giải thích trong báo cáo |
| **E3** Dư thừa có chủ đích | Giữ nguyên các cột theo ERD | Bảng E3 bên dưới: 4 trong 7 dư thừa thực thi **khai báo** bằng FK phức hợp (vật lý), 3 còn lại bằng trigger |
| **E4** CHI_TIET_HOA_DON | PK `(MaHD, SoThuTu)`; `Loai`, `MaGoi NULL`, `MaSP NULL`; `DANG_KY_GOI.(MaHD, SoThuTu)` FK ghép NOT NULL | `CK_CT_XOR`: `Loai = N'Gói'` ⇔ `MaGoi` có giá trị và `MaSP` NULL (ngược lại cho sản phẩm). Vì FK vật lý của DANG_KY_GOI gồm cả `MaGoi` (NOT NULL) nên dòng sản phẩm (MaGoi NULL) **không thể** được DANG_KY_GOI tham chiếu: khai báo, không cần trigger. Số DANG_KY_GOI của một dòng Gói = `SoLuong`: trigger AFTER INSERT chặn vượt `SoLuong`; thủ tục lập hóa đơn sinh đủ `SoLuong` dòng trong cùng giao dịch và kiểm tra bằng nhau trước COMMIT (CHECK không đếm được dòng khác) |
| **E5** Thuộc tính dẫn xuất | Bảng E5 bên dưới | Bảng E5 |
| **E6** Lịch sử điều chuyển | `LICH_SU_DIEU_CHUYEN(MaDieuChuyen, MaNV, MaCN, NgayBatDau, NgayKetThuc NULL, LyDo NULL)`; `NHAN_VIEN.MaCN` là chi nhánh hiện tại | (a) `UNIQUE (MaNV, NgayBatDau)`; (b) `UNIQUE (MaNV) WHERE NgayKetThuc IS NULL` ⇒ tối đa một bản ghi đang mở; (c) trigger: các khoảng của một NV liên tiếp, không chồng, `NgayBatDau` đầu = `NgayVaoLam` (bản ghi đầu tạo khi vào làm, LyDo = N'Vào làm'); (d) trigger: `ConLamViec = 1` ⇒ `NHAN_VIEN.MaCN` = `MaCN` của bản ghi đang mở; nghỉ việc ⇒ đóng bản ghi. **Hoa hồng PT theo chi nhánh từng giai đoạn**: `LICH_HEN_PT` (Đã hoàn thành) JOIN `LICH_SU_DIEU_CHUYEN ON MaNV = MaHLV AND CAST(NgayGioHen AS date) BETWEEN NgayBatDau AND ISNULL(NgayKetThuc, '9999-12-31')`, nhóm theo `LICH_SU_DIEU_CHUYEN.MaCN`, nhân `HoaHongMoiBuoi`; chỉ mục `(MaNV, NgayBatDau) INCLUDE (NgayKetThuc, MaCN)`; thủ tục đặt lịch kiểm tra `LICH_HEN_PT.MaCN` = chi nhánh của HLV tại `NgayGioHen` |
| **E7** (đã chốt) | Không có `NgayBaoLuu`, `KHUNG_GIO`, `THIET_BI`. `DANG_KY_GOI.TrangThai ∈ {Hoạt động, Hết hạn, Hủy}`. `CHECK_IN.ThietBi` là chuỗi. `DANG_KY_GOI.NgayKetThuc` lưu | `CK ThoiLuong = 60`, `CK` phút 00 giây 00; `UNIQUE (MaHLV, NgayGioHen)` và `UNIQUE (MaHV, NgayGioHen)` đều `WHERE TrangThai <> N'Hủy'`; thủ tục đặt lịch bắt lỗi 2601/2627 trả "khung giờ đã có người đặt", kiểm tra số lịch `Đã đặt ≤ BuoiConLai` với `UPDLOCK` trên DANG_KY_GOI, kiểm tra HLV công tác tại chi nhánh vào `NgayGioHen` (E6) |
| **E8** (đã chốt) | `ChucVu` dùng `N'HLV'`; `HUAN_LUYEN_VIEN.MaHLV` PK+FK | Chuyên biệt hóa **partial, một lớp con, d/o không áp dụng** (không vẽ tam giác d). Trigger: `ChucVu = N'HLV'` ⇔ có dòng trong HUAN_LUYEN_VIEN; đổi `ChucVu` khỏi HLV bị chặn nếu còn lịch hẹn/lịch sử |
| **E9** Tỷ lệ lấp đầy | Bảng dẫn xuất (không vẽ): `THONG_KE_CHECKIN(MaCN, Ngay, Gio, SoLuotVao, SoLuotRa)`, `DOANH_THU_NGAY(MaCN, Ngay, TongTien, SoHoaDon)` | "Lượt vào" ≠ "người đang có mặt". Người có mặt cuối giờ h = `SUM(SoLuotVao − SoLuotRa)` cộng dồn từ đầu ngày đến h (hoặc đếm trực tiếp `ThoiGianVao <= t < ThoiGianRa`). Tỷ lệ lấp đầy = số đó / `SUM(SucChua)` của PHONG `ConHoatDong = 1` ở chi nhánh. Bảng cũ chỉ có `SoLuot`, tôi đổi thành hai cột vào/ra (D11). Job cuối ngày tự đóng lượt chưa check-out lúc đóng cửa để cộng dồn không rò sang ngày sau |
| **E10** Xác thực < 50 ms | `CHECK_IN.ThietBi` là chuỗi: **không** tham gia xác thực, không cần chỉ mục | Truy vấn xác thực chỉ theo `MaHV` (mã trên thẻ/QR) nên chỉ mục là `DANG_KY_GOI (MaHV, TrangThai, NgayBatDau, NgayKetThuc) INCLUDE (MaDK, MaCN, BuoiConLai)`: một seek ra đúng gói còn hạn. Ghi log: `INSERT` vào CHECK_IN chỉ cần PK. `UNIQUE (MaHV) WHERE ThoiGianRa IS NULL` ⇒ mỗi hội viên tối đa một lượt chưa check-out, chặn quét trùng. *Lưu ý vật lý*: nếu CHECK_IN phân vùng theo `ThoiGianVao`, unique filtered index này không chứa cột phân vùng nên không aligned (không SWITCH được partition); xem D16 |

### E3 – Dư thừa có chủ đích và cách đồng nhất

| Dư thừa | Cách thực thi | Loại |
|---|---|---|
| CHECK_IN.MaHV = DANG_KY_GOI.MaHV | FK `(MaDK, MaHV)` → DANG_KY_GOI, cần `UNIQUE (MaDK, MaHV)` | khai báo |
| LICH_HEN_PT.MaHV = DANG_KY_GOI.MaHV | FK `(MaDK, MaHV)` → DANG_KY_GOI | khai báo |
| CHECK_IN.MaCN = PHONG.MaCN khi có phòng | FK `(MaPhong, MaCN)` → PHONG, cần `UNIQUE (MaPhong, MaCN)`; `MaPhong` NULL thì SQL Server bỏ qua kiểm tra (đúng ý) | khai báo |
| DANG_KY_GOI.MaGoi = CHI_TIET_HOA_DON.MaGoi | FK `(MaHD, SoThuTu, MaGoi)` → CHI_TIET_HOA_DON, cần `UNIQUE (MaHD, SoThuTu, MaGoi)` | khai báo |
| DANG_KY_GOI.MaHV = HOA_DON.MaHV; DANG_KY_GOI.MaCN = HOA_DON.MaCN | trigger AFTER INSERT/UPDATE (nối qua CHI_TIET_HOA_DON → HOA_DON) | trigger |
| HOA_DON.MaCN = chi nhánh của HOA_DON.MaNV tại NgayLap | trigger tra LICH_SU_DIEU_CHUYEN | trigger |
| NHAN_VIEN.MaCN = MaCN của bản ghi đang mở ở LICH_SU_DIEU_CHUYEN | trigger (E6) | trigger |

CHECK_IN.MaCN **không** buộc bằng DANG_KY_GOI.MaCN, vì đề cho hội viên tập "tại bất kỳ chi nhánh nào".
Các FK phức hợp vật lý thay cho FK đơn cùng quan hệ ở hình, nên không thêm mũi tên.

### E5 – Thuộc tính dẫn xuất: cột nào lưu

| Thuộc tính | Lưu? | Cách duy trì | Lý do (dạng chuẩn / hiệu năng) |
|---|---|---|---|
| `[ThanhTien]` (CTHD) = SoLuong × DonGia | Có | cột tính `PERSISTED` | cùng dòng, DBMS tự duy trì ⇒ không thể lệch; dùng lại trong tổng doanh thu |
| `[TongTienGoc]` (HOA_DON) = Σ ThanhTien | Có | cột thường; thủ tục lập hóa đơn ghi, trigger trên CHI_TIET_HOA_DON kiểm tra khớp | vượt quan hệ nên không dùng cột tính được; báo cáo doanh thu (vấn đề 3) khỏi join CTHD. Vi phạm 3NF có chủ đích |
| `[ThanhToanThucTe]` (HOA_DON) = TongTienGoc − GiamGia | Có | cột tính `PERSISTED`, `CHECK GiamGia ≤ TongTienGoc` | đầu vào của điểm loyalty và doanh thu, cần đọc nhanh/đánh chỉ mục; DBMS tự duy trì |
| `[NgayKetThuc]` (DANG_KY_GOI) = NgayBatDau + ThoiHanThang tháng | Có | cột thường; trigger/thủ tục đăng ký ghi và kiểm tra | phụ thuộc GOI_DICH_VU.ThoiHanThang nên không là cột tính; cần trong chỉ mục xác thực check-in (vấn đề 1); GOI_DICH_VU đổi thời hạn sau này không ảnh hưởng gói đã bán |
| `[Tuoi]` (HOI_VIEN) | **Không** | view / hàm từ `NgaySinh` | phụ thuộc ngày hiện tại nên không thể PERSISTED; lưu sẽ sai theo thời gian |

### Dạng chuẩn

Tất cả quan hệ đạt **BCNF**, trừ các vi phạm 3NF dưới đây, đều có chủ đích và đều có ràng buộc đồng nhất:

| Quan hệ | Phụ thuộc hàm vi phạm | Lý do giữ |
|---|---|---|
| HOA_DON | ThanhToanThucTe ← TongTienGoc, GiamGia | cột tính PERSISTED (E5) |
| CHI_TIET_HOA_DON | ThanhTien ← SoLuong, DonGia; Loai ↔ (MaGoi hay MaSP có giá trị) | cột tính PERSISTED; ERD có thuộc tính Loai, giữ đồng bộ bằng `CK_CT_XOR` |
| DANG_KY_GOI | (MaHD, SoThuTu) → MaGoi, MaHV, MaCN (không là siêu khóa vì một dòng có SoLuong gói); (NgayBatDau, MaGoi) → NgayKetThuc | E3, E5 |
| CHECK_IN | MaDK → MaHV; MaPhong → MaCN | E3: truy vấn xác thực/lấp đầy không phải join |
| LICH_HEN_PT | MaDK → MaHV | E3 |
| DIEM_LOYALTY | TongChiTieuNam → MaHang (qua ngưỡng ở HANG_HOI_VIEN) | E1: mục đích chính của thiết kế (vấn đề 4) |
| NHAN_VIEN | MaCN trùng bản ghi mở của LICH_SU_DIEU_CHUYEN | E6: dư thừa giữa hai bảng, không phải PTH trong một quan hệ |

## 4. Bước 4a – Lược đồ chuẩn

Quy ước: <u>PK gạch dưới</u>, <i>FK in nghiêng</i>, <u><i>PK+FK vừa gạch vừa nghiêng</i></u>, `[x]` = dẫn xuất có lưu, kiểu SQL Server, NULL / NOT NULL. Mỗi dòng "FK" tương ứng đúng một mũi tên trên hình.

<!--BEGIN:STATS-->
| Chỉ số | Giá trị |
|---|--:|
| Quan hệ (bảng) | 20 |
| Cột | 127 |
| Khóa chính | 20 (cột PK: 25; PK ghép: 5 – CHI_NHANH_DICH_VU, TON_KHO, DIEM_LOYALTY, CHI_TIET_HOA_DON, HLV_CHUNG_CHI) |
| Khóa ngoại (= số mũi tên trên hình tổng) | 33 (cột FK: 34; FK ghép: 1 – DANG_KY_GOI) |
| Cột cho phép NULL | 13 |
| Ràng buộc CHECK | 33 |
| UNIQUE / unique filtered index khai báo | 13 (trong đó filtered: 7) |
<!--END:STATS-->

<!--BEGIN:SCHEMA-->

**Phân hệ: Danh mục & chi nhánh**

- **LOAI_DICH_VU**(<u>MaLoai</u> SMALLINT NOT NULL, TenLoai NVARCHAR(50) NOT NULL, MoTa NVARCHAR(255) NULL)
  - Khóa thay thế: TenLoai
- **CHI_NHANH**(<u>MaCN</u> SMALLINT NOT NULL, TenCN NVARCHAR(100) NOT NULL, SoNha NVARCHAR(30) NOT NULL, Duong NVARCHAR(100) NOT NULL, Quan NVARCHAR(50) NOT NULL, ThanhPho NVARCHAR(50) NOT NULL, SoDienThoai VARCHAR(15) NOT NULL, GioMoCua TIME(0) NOT NULL, GioDongCua TIME(0) NOT NULL)
  - Khóa thay thế: SoDienThoai
  - CHECK `CK_CN_Gio: GioMoCua < GioDongCua (giả định chi nhánh không mở qua nửa đêm)`
  - Ghi chú: DiaChi (tổng hợp) tách thành SoNha, Duong, Quan, ThanhPho
- **CHI_NHANH_DICH_VU**(<u><i>MaCN</i></u> SMALLINT NOT NULL, <u><i>MaLoai</i></u> SMALLINT NOT NULL, TrangThai NVARCHAR(20) NOT NULL)
  - FK: CHI_NHANH_DICH_VU.MaCN -> CHI_NHANH.MaCN &nbsp;*(cung cấp)*
  - FK: CHI_NHANH_DICH_VU.MaLoai -> LOAI_DICH_VU.MaLoai &nbsp;*(được cung cấp)*
  - CHECK `CK_CNDV_TrangThai: TrangThai IN (N'Hoạt động', N'Tạm ngưng')  [giá trị do nhóm đề xuất]`
  - Ghi chú: N-N có thuộc tính: khóa ghép (MaCN, MaLoai)
- **PHONG**(<u>MaPhong</u> INT NOT NULL, <i>MaCN</i> SMALLINT NOT NULL, <i>MaLoai</i> SMALLINT NOT NULL, TenPhong NVARCHAR(100) NOT NULL, SucChua SMALLINT NOT NULL, ConHoatDong BIT NOT NULL)
  - FK: PHONG.MaCN -> CHI_NHANH.MaCN &nbsp;*(có phòng)*
  - FK: PHONG.MaLoai -> LOAI_DICH_VU.MaLoai &nbsp;*(loại phòng)*
  - CHECK `CK_PHONG_SucChua: SucChua > 0`
  - Chỉ mục/UNIQUE `UQ_PHONG_Phong_CN: UNIQUE (MaPhong, MaCN)  -- chỉ để làm đích của FK phức hợp từ CHECK_IN (E3)`

**Phân hệ: Gói dịch vụ & hóa đơn**

- **GOI_DICH_VU**(<u>MaGoi</u> INT NOT NULL, TenGoi NVARCHAR(100) NOT NULL, <i>MaLoai</i> SMALLINT NOT NULL, ThoiHanThang SMALLINT NOT NULL, SoBuoi SMALLINT NOT NULL, GiaTien DECIMAL(12,0) NOT NULL, ConHieuLuc BIT NOT NULL)
  - FK: GOI_DICH_VU.MaLoai -> LOAI_DICH_VU.MaLoai &nbsp;*(phân loại)*
  - CHECK `CK_GOI_ThoiHan: ThoiHanThang > 0`
  - CHECK `CK_GOI_SoBuoi: SoBuoi >= 0   (0 = gói không có buổi PT)`
  - CHECK `CK_GOI_Gia: GiaTien >= 0`

**Phân hệ: Sản phẩm & tồn kho**

- **SAN_PHAM**(<u>MaSP</u> INT NOT NULL, TenSP NVARCHAR(150) NOT NULL, GiaBan DECIMAL(12,0) NOT NULL, Loai NVARCHAR(50) NOT NULL, DonViTinh NVARCHAR(20) NOT NULL, ConBan BIT NOT NULL)
  - CHECK `CK_SP_Gia: GiaBan >= 0`
- **TON_KHO**(<u><i>MaCN</i></u> SMALLINT NOT NULL, <u><i>MaSP</i></u> INT NOT NULL, SoLuong INT NOT NULL, NgayCapNhat DATETIME2(0) NOT NULL)
  - FK: TON_KHO.MaSP -> SAN_PHAM.MaSP &nbsp;*(tồn kho)*
  - FK: TON_KHO.MaCN -> CHI_NHANH.MaCN &nbsp;*(lưu kho)*
  - CHECK `CK_TK_SoLuong: SoLuong >= 0`
  - Ghi chú: N-N có thuộc tính: khóa ghép (MaCN, MaSP) – MaCN đứng trước vì truy vấn thường theo chi nhánh

**Phân hệ: Hội viên & loyalty**

- **HANG_HOI_VIEN**(<u>MaHang</u> SMALLINT NOT NULL, TenHang NVARCHAR(20) NOT NULL, NguongChiTieu DECIMAL(15,0) NOT NULL)
  - Khóa thay thế: TenHang
  - CHECK `CK_HANG_Nguong: NguongChiTieu >= 0`
  - Chỉ mục/UNIQUE `UQ_HANG_Nguong: UNIQUE (NguongChiTieu)  [đề xuất: để ánh xạ chi tiêu -> hạng xác định]`
- **HOI_VIEN**(<u>MaHV</u> INT NOT NULL, Ho NVARCHAR(50) NOT NULL, TenDem NVARCHAR(50) NULL, Ten NVARCHAR(50) NOT NULL, SoDienThoai VARCHAR(15) NOT NULL, Email VARCHAR(100) NULL, CCCD CHAR(12) NULL, GioiTinh NVARCHAR(3) NOT NULL, NgaySinh DATE NOT NULL, NgayDangKy DATE NOT NULL)
  - Khóa thay thế: SoDienThoai; Email (filtered); CCCD (filtered)
  - CHECK `CK_HV_GioiTinh: GioiTinh IN (N'Nam', N'Nữ', N'Khác')`
  - CHECK `CK_HV_NgaySinh: NgaySinh <= NgayDangKy`
  - Chỉ mục/UNIQUE `UQ_HV_Email: UNIQUE (Email) WHERE Email IS NOT NULL`
  - Chỉ mục/UNIQUE `UQ_HV_CCCD: UNIQUE (CCCD) WHERE CCCD IS NOT NULL`
  - Ghi chú: HoTen (tổng hợp) tách thành Ho, TenDem, Ten
  - Ghi chú: [Tuoi] KHÔNG lưu (xem E5): tính bằng view/hàm từ NgaySinh
- **DIEM_LOYALTY**(<u><i>MaHV</i></u> INT NOT NULL, <u>NamXet</u> SMALLINT NOT NULL, TongChiTieuNam DECIMAL(15,0) NOT NULL, DiemThuong INT NOT NULL, NgayCapNhat DATETIME2(0) NOT NULL, <i>MaHang</i> SMALLINT NOT NULL)
  - FK: DIEM_LOYALTY.MaHV -> HOI_VIEN.MaHV &nbsp;*(tích lũy)*
  - FK: DIEM_LOYALTY.MaHang -> HANG_HOI_VIEN.MaHang &nbsp;*(xếp hạng)*
  - CHECK `CK_DL_ChiTieu: TongChiTieuNam >= 0`
  - CHECK `CK_DL_Diem: DiemThuong >= 0`
  - CHECK `CK_DL_Nam: NamXet BETWEEN 2000 AND 2100`
  - Ghi chú: Thực thể yếu của HOI_VIEN: khóa (MaHV, NamXet)
  - Ghi chú: Hạng hiện tại = MaHang của dòng NamXet = YEAR(GETDATE()); HOI_VIEN không có cột hạng (E1)

**Phân hệ: Gói dịch vụ & hóa đơn**

- **HOA_DON**(<u>MaHD</u> BIGINT NOT NULL, NgayLap DATETIME2(0) NOT NULL, <i>MaNV</i> INT NOT NULL, <i>MaHV</i> INT NOT NULL, <i>MaCN</i> SMALLINT NOT NULL, [TongTienGoc] DECIMAL(15,0) NOT NULL, GiamGia DECIMAL(15,0) NOT NULL, [ThanhToanThucTe] DECIMAL(15,0) NOT NULL, HinhThucThanhToan NVARCHAR(20) NOT NULL, TrangThai NVARCHAR(20) NOT NULL)
  - FK: HOA_DON.MaNV -> NHAN_VIEN.MaNV &nbsp;*(lập)*
  - FK: HOA_DON.MaHV -> HOI_VIEN.MaHV &nbsp;*(Thanh toán)*
  - FK: HOA_DON.MaCN -> CHI_NHANH.MaCN &nbsp;*(lập tại)*
  - CHECK `CK_HD_HinhThuc: HinhThucThanhToan IN (N'Tiền mặt', N'VNPay', N'Thẻ')`
  - CHECK `CK_HD_TrangThai: TrangThai IN (N'Đã thanh toán', N'Hủy')`
  - CHECK `CK_HD_GiamGia: GiamGia >= 0 AND GiamGia <= TongTienGoc`
  - Ghi chú: TongTienGoc: cột thường, thủ tục lập hóa đơn ghi = SUM(ThanhTien); trigger kiểm tra khớp (E5)
  - Ghi chú: ThanhToanThucTe: cột tính PERSISTED = TongTienGoc - GiamGia (E5)
- **CHI_TIET_HOA_DON**(<u><i>MaHD</i></u> BIGINT NOT NULL, <u>SoThuTu</u> SMALLINT NOT NULL, Loai NVARCHAR(10) NOT NULL, <i>MaGoi</i> INT NULL, <i>MaSP</i> INT NULL, SoLuong INT NOT NULL, DonGia DECIMAL(12,0) NOT NULL, [ThanhTien] DECIMAL(15,0) NOT NULL)
  - FK: CHI_TIET_HOA_DON.MaHD -> HOA_DON.MaHD &nbsp;*(gồm (HOA_DON))*
  - FK: CHI_TIET_HOA_DON.MaGoi -> GOI_DICH_VU.MaGoi &nbsp;*(gồm (GOI_DICH_VU))*
  - FK: CHI_TIET_HOA_DON.MaSP -> SAN_PHAM.MaSP &nbsp;*(gồm (SAN_PHAM))*
  - CHECK `CK_CT_Loai: Loai IN (N'Gói', N'Sản phẩm')`
  - CHECK `CK_CT_XOR: (Loai = N'Gói' AND MaGoi IS NOT NULL AND MaSP IS NULL) OR (Loai = N'Sản phẩm' AND MaSP IS NOT NULL AND MaGoi IS NULL)`
  - CHECK `CK_CT_SoLuong: SoLuong > 0`
  - CHECK `CK_CT_DonGia: DonGia >= 0`
  - Chỉ mục/UNIQUE `UQ_CT_HD_STT_Goi: UNIQUE (MaHD, SoThuTu, MaGoi)  -- đích của FK phức hợp từ DANG_KY_GOI (E3)`
  - Ghi chú: Thực thể yếu của HOA_DON: khóa (MaHD, SoThuTu)
  - Ghi chú: ThanhTien: cột tính PERSISTED = SoLuong * DonGia (E5)
  - Ghi chú: DonGia là giá chốt tại thời điểm bán (không dẫn xuất từ GiaBan/GiaTien hiện tại)
- **DANG_KY_GOI**(<u>MaDK</u> BIGINT NOT NULL, <i>MaHV</i> INT NOT NULL, <i>MaGoi</i> INT NOT NULL, <i>MaCN</i> SMALLINT NOT NULL, <i>MaHD</i> BIGINT NOT NULL, <i>SoThuTu</i> SMALLINT NOT NULL, NgayBatDau DATE NOT NULL, [NgayKetThuc] DATE NOT NULL, TrangThai NVARCHAR(20) NOT NULL, BuoiConLai SMALLINT NOT NULL)
  - FK: DANG_KY_GOI.MaHV -> HOI_VIEN.MaHV &nbsp;*(đăng ký)*
  - FK: DANG_KY_GOI.MaGoi -> GOI_DICH_VU.MaGoi &nbsp;*(được đăng ký)*
  - FK: DANG_KY_GOI.MaCN -> CHI_NHANH.MaCN &nbsp;*(đăng ký tại)*
  - FK: (DANG_KY_GOI.MaHD, DANG_KY_GOI.SoThuTu) -> CHI_TIET_HOA_DON.(MaHD, SoThuTu) &nbsp;*(xuất ra)*
  - CHECK `CK_DK_TrangThai: TrangThai IN (N'Hoạt động', N'Hết hạn', N'Hủy')`
  - CHECK `CK_DK_Ngay: NgayKetThuc > NgayBatDau`
  - CHECK `CK_DK_Buoi: BuoiConLai >= 0`
  - Chỉ mục/UNIQUE `UQ_DK_DK_HV: UNIQUE (MaDK, MaHV)  -- đích của FK phức hợp từ CHECK_IN, LICH_HEN_PT (E3)`
  - Chỉ mục/UNIQUE `IX_DK_XacThuc: (MaHV, TrangThai, NgayBatDau, NgayKetThuc) INCLUDE (MaDK, MaCN, BuoiConLai)  -- E10`
  - Ghi chú: FK ghép (MaHD, SoThuTu) -> CHI_TIET_HOA_DON; số dòng DANG_KY_GOI của một dòng chi tiết = SoLuong (E4)
  - Ghi chú: NgayKetThuc = DATEADD(MONTH, GOI_DICH_VU.ThoiHanThang, NgayBatDau): lưu có chủ đích (E5, E7)
  - Ghi chú: Không có bảo lưu (E7)

**Phân hệ: Nhân sự**

- **NHAN_VIEN**(<u>MaNV</u> INT NOT NULL, Ho NVARCHAR(50) NOT NULL, TenDem NVARCHAR(50) NULL, Ten NVARCHAR(50) NOT NULL, SoDienThoai VARCHAR(15) NULL, ChucVu NVARCHAR(20) NOT NULL, LuongCoBan DECIMAL(12,0) NOT NULL, <i>MaCN</i> SMALLINT NOT NULL, NgayVaoLam DATE NOT NULL, ConLamViec BIT NOT NULL)
  - Khóa thay thế: SoDienThoai (filtered)
  - FK: NHAN_VIEN.MaCN -> CHI_NHANH.MaCN &nbsp;*(làm việc tại)*
  - CHECK `CK_NV_ChucVu: ChucVu IN (N'HLV', N'Lễ tân', N'Quản lý', N'Bán hàng')`
  - CHECK `CK_NV_Luong: LuongCoBan >= 0`
  - Chỉ mục/UNIQUE `UQ_NV_SDT: UNIQUE (SoDienThoai) WHERE SoDienThoai IS NOT NULL`
  - Ghi chú: MaCN = chi nhánh hiện tại (quan hệ 'làm việc tại'); phải bằng MaCN của bản ghi đang mở trong LICH_SU_DIEU_CHUYEN (E6)
- **HUAN_LUYEN_VIEN**(<u><i>MaHLV</i></u> INT NOT NULL, ChuyenMon NVARCHAR(100) NOT NULL, HoaHongMoiBuoi DECIMAL(12,0) NOT NULL)
  - FK: HUAN_LUYEN_VIEN.MaHLV -> NHAN_VIEN.MaNV &nbsp;*(U (chuyên biệt hóa))*
  - CHECK `CK_HLV_HoaHong: HoaHongMoiBuoi >= 0`
  - Ghi chú: Chuyên biệt hóa partial, một lớp con (d/o không áp dụng); MaHLV vừa PK vừa FK -> NHAN_VIEN.MaNV
  - Ghi chú: Ràng buộc: NHAN_VIEN.ChucVu = N'HLV' <=> có dòng ở đây (trigger, E8)
- **HLV_CHUNG_CHI**(<u><i>MaHLV</i></u> INT NOT NULL, <u>ChungChi</u> NVARCHAR(150) NOT NULL)
  - FK: HLV_CHUNG_CHI.MaHLV -> HUAN_LUYEN_VIEN.MaHLV &nbsp;*({ChungChi} đa trị)*
  - Ghi chú: Thuộc tính đa trị {ChungChi} của HUAN_LUYEN_VIEN: khóa ghép (MaHLV, ChungChi)
- **LICH_SU_DIEU_CHUYEN**(<u>MaDieuChuyen</u> INT NOT NULL, <i>MaNV</i> INT NOT NULL, <i>MaCN</i> SMALLINT NOT NULL, NgayBatDau DATE NOT NULL, NgayKetThuc DATE NULL, LyDo NVARCHAR(255) NULL)
  - Khóa thay thế: (MaNV, NgayBatDau)
  - FK: LICH_SU_DIEU_CHUYEN.MaNV -> NHAN_VIEN.MaNV &nbsp;*(được điều chuyển)*
  - FK: LICH_SU_DIEU_CHUYEN.MaCN -> CHI_NHANH.MaCN &nbsp;*(tiếp nhận)*
  - CHECK `CK_LS_Ngay: NgayKetThuc IS NULL OR NgayKetThuc >= NgayBatDau`
  - Chỉ mục/UNIQUE `UQ_LS_NV_Bat: UNIQUE (MaNV, NgayBatDau)`
  - Chỉ mục/UNIQUE `UQ_LS_NV_Mo: UNIQUE (MaNV) WHERE NgayKetThuc IS NULL  -- tối đa một bản ghi đang mở (E6)`
  - Chỉ mục/UNIQUE `IX_LS_TraCuu: (MaNV, NgayBatDau) INCLUDE (NgayKetThuc, MaCN)  -- tra chi nhánh tại thời điểm t`
  - Ghi chú: Khoảng [NgayBatDau, NgayKetThuc] đóng hai đầu, NULL = đang công tác; các khoảng của một NV liên tiếp, không chồng (trigger); bản ghi đầu tiên tạo khi vào làm (NgayBatDau = NgayVaoLam)

**Phân hệ: Vận hành (check-in, PT)**

- **LICH_HEN_PT**(<u>MaLichHen</u> BIGINT NOT NULL, <i>MaHV</i> INT NOT NULL, <i>MaHLV</i> INT NOT NULL, <i>MaCN</i> SMALLINT NOT NULL, <i>MaDK</i> BIGINT NOT NULL, NgayGioHen DATETIME2(0) NOT NULL, ThoiLuong SMALLINT NOT NULL, TrangThai NVARCHAR(20) NOT NULL)
  - FK: LICH_HEN_PT.MaCN -> CHI_NHANH.MaCN &nbsp;*(diễn ra tại)*
  - FK: LICH_HEN_PT.MaHLV -> HUAN_LUYEN_VIEN.MaHLV &nbsp;*(phụ trách)*
  - FK: LICH_HEN_PT.MaHV -> HOI_VIEN.MaHV &nbsp;*(đặt lịch)*
  - FK: LICH_HEN_PT.MaDK -> DANG_KY_GOI.MaDK &nbsp;*(thuộc)*
  - CHECK `CK_LH_ThoiLuong: ThoiLuong = 60   (phút)`
  - CHECK `CK_LH_Gio: DATEPART(MINUTE, NgayGioHen) = 0 AND DATEPART(SECOND, NgayGioHen) = 0`
  - CHECK `CK_LH_TrangThai: TrangThai IN (N'Đã đặt', N'Đã hoàn thành', N'Hủy')`
  - Chỉ mục/UNIQUE `UQ_LH_HLV_Gio: UNIQUE (MaHLV, NgayGioHen) WHERE TrangThai <> N'Hủy'  -- E2/E7`
  - Chỉ mục/UNIQUE `UQ_LH_HV_Gio: UNIQUE (MaHV, NgayGioHen) WHERE TrangThai <> N'Hủy'  -- E2/E7`
  - Ghi chú: Mọi lịch dài 60 phút, bắt đầu tròn giờ => hai lịch chồng nhau khi và chỉ khi trùng NgayGioHen, nên unique filtered index chặn tuyệt đối overbooking (E2/E7)
- **DANH_GIA_PT**(<u>MaDanhGia</u> BIGINT NOT NULL, <i>MaLichHen</i> BIGINT NOT NULL, Diem TINYINT NOT NULL, NhanXet NVARCHAR(500) NULL, NgayDanhGia DATETIME2(0) NOT NULL)
  - Khóa thay thế: MaLichHen
  - FK: DANH_GIA_PT.MaLichHen -> LICH_HEN_PT.MaLichHen &nbsp;*(được đánh giá)*
  - CHECK `CK_DG_Diem: Diem BETWEEN 1 AND 5`
  - Chỉ mục/UNIQUE `UQ_DG_LichHen: UNIQUE (MaLichHen)  -- quan hệ 1 - (0..1) với LICH_HEN_PT`
  - Ghi chú: Chỉ đánh giá được lịch có TrangThai = N'Đã hoàn thành' (trigger)
- **CHECK_IN**(<u>MaCheckIn</u> BIGINT NOT NULL, <i>MaHV</i> INT NOT NULL, <i>MaCN</i> SMALLINT NOT NULL, <i>MaPhong</i> INT NULL, <i>MaDK</i> BIGINT NOT NULL, ThoiGianVao DATETIME2(0) NOT NULL, ThoiGianRa DATETIME2(0) NULL, ThietBi NVARCHAR(50) NOT NULL)
  - FK: CHECK_IN.MaHV -> HOI_VIEN.MaHV &nbsp;*(check-in)*
  - FK: CHECK_IN.MaCN -> CHI_NHANH.MaCN &nbsp;*(ghi nhận tại)*
  - FK: CHECK_IN.MaPhong -> PHONG.MaPhong &nbsp;*(vào phòng)*
  - FK: CHECK_IN.MaDK -> DANG_KY_GOI.MaDK &nbsp;*(được dùng)*
  - CHECK `CK_CI_Ra: ThoiGianRa IS NULL OR ThoiGianRa > ThoiGianVao`
  - Chỉ mục/UNIQUE `UQ_CI_DangCoMat: UNIQUE (MaHV) WHERE ThoiGianRa IS NULL  -- tối đa một lượt chưa check-out (E10)`
  - Ghi chú: ThietBi là chuỗi (cửa/thiết bị), không có thực thể THIET_BI; không tham gia xác thực, không cần chỉ mục
<!--END:SCHEMA-->

### Danh sách 33 khóa ngoại và FK phức hợp vật lý

<!--BEGIN:FKTABLE-->
| # | Khóa ngoại (bảng.cột) | Tham chiếu | Quan hệ trên ERD | NULL? | Bản số / ghi chú |
|--:|---|---|---|---|---|
| 1 | CHI_NHANH_DICH_VU.MaCN | CHI_NHANH.MaCN | cung cấp | NOT NULL | N – 1 |
| 2 | CHI_NHANH_DICH_VU.MaLoai | LOAI_DICH_VU.MaLoai | được cung cấp | NOT NULL | N – 1 |
| 3 | PHONG.MaCN | CHI_NHANH.MaCN | có phòng | NOT NULL | N – 1 |
| 4 | PHONG.MaLoai | LOAI_DICH_VU.MaLoai | loại phòng | NOT NULL | N – 1 |
| 5 | GOI_DICH_VU.MaLoai | LOAI_DICH_VU.MaLoai | phân loại | NOT NULL | N – 1 |
| 6 | TON_KHO.MaSP | SAN_PHAM.MaSP | tồn kho | NOT NULL | N – 1 |
| 7 | TON_KHO.MaCN | CHI_NHANH.MaCN | lưu kho | NOT NULL | N – 1 |
| 8 | DIEM_LOYALTY.MaHV | HOI_VIEN.MaHV | tích lũy | NOT NULL | 1 – N: thực thể yếu, FK nằm trong PK |
| 9 | DIEM_LOYALTY.MaHang | HANG_HOI_VIEN.MaHang | xếp hạng | NOT NULL | N – 1 |
| 10 | HOA_DON.MaNV | NHAN_VIEN.MaNV | lập | NOT NULL | N – 1 |
| 11 | HOA_DON.MaHV | HOI_VIEN.MaHV | Thanh toán | NOT NULL | N – 1 |
| 12 | HOA_DON.MaCN | CHI_NHANH.MaCN | lập tại | NOT NULL | N – 1 |
| 13 | CHI_TIET_HOA_DON.MaHD | HOA_DON.MaHD | gồm (HOA_DON) | NOT NULL | 1 – N: thực thể yếu, FK nằm trong PK |
| 14 | CHI_TIET_HOA_DON.MaGoi | GOI_DICH_VU.MaGoi | gồm (GOI_DICH_VU) | NULL | N – (0..1): phía FK tùy chọn |
| 15 | CHI_TIET_HOA_DON.MaSP | SAN_PHAM.MaSP | gồm (SAN_PHAM) | NULL | N – (0..1): phía FK tùy chọn |
| 16 | DANG_KY_GOI.MaHV | HOI_VIEN.MaHV | đăng ký | NOT NULL | N – 1 |
| 17 | DANG_KY_GOI.MaGoi | GOI_DICH_VU.MaGoi | được đăng ký | NOT NULL | N – 1 |
| 18 | DANG_KY_GOI.MaCN | CHI_NHANH.MaCN | đăng ký tại | NOT NULL | N – 1 |
| 19 | DANG_KY_GOI.(MaHD, SoThuTu) | CHI_TIET_HOA_DON.(MaHD, SoThuTu) | xuất ra | NOT NULL | N – 1 |
| 20 | NHAN_VIEN.MaCN | CHI_NHANH.MaCN | làm việc tại | NOT NULL | N – 1 |
| 21 | HUAN_LUYEN_VIEN.MaHLV | NHAN_VIEN.MaNV | U (chuyên biệt hóa) | NOT NULL | 1 – (0..1): chuyên biệt hóa, FK là PK |
| 22 | HLV_CHUNG_CHI.MaHLV | HUAN_LUYEN_VIEN.MaHLV | {ChungChi} đa trị | NOT NULL | 1 – N: đa trị |
| 23 | LICH_SU_DIEU_CHUYEN.MaNV | NHAN_VIEN.MaNV | được điều chuyển | NOT NULL | N – 1 |
| 24 | LICH_SU_DIEU_CHUYEN.MaCN | CHI_NHANH.MaCN | tiếp nhận | NOT NULL | N – 1 |
| 25 | LICH_HEN_PT.MaCN | CHI_NHANH.MaCN | diễn ra tại | NOT NULL | N – 1 |
| 26 | LICH_HEN_PT.MaHLV | HUAN_LUYEN_VIEN.MaHLV | phụ trách | NOT NULL | N – 1 |
| 27 | LICH_HEN_PT.MaHV | HOI_VIEN.MaHV | đặt lịch | NOT NULL | N – 1 |
| 28 | LICH_HEN_PT.MaDK | DANG_KY_GOI.MaDK | thuộc | NOT NULL | N – 1 |
| 29 | DANH_GIA_PT.MaLichHen | LICH_HEN_PT.MaLichHen | được đánh giá | NOT NULL | 1 – (0..1): FK + UNIQUE |
| 30 | CHECK_IN.MaHV | HOI_VIEN.MaHV | check-in | NOT NULL | N – 1 |
| 31 | CHECK_IN.MaCN | CHI_NHANH.MaCN | ghi nhận tại | NOT NULL | N – 1 |
| 32 | CHECK_IN.MaPhong | PHONG.MaPhong | vào phòng | NULL | N – (0..1): phía FK tùy chọn |
| 33 | CHECK_IN.MaDK | DANG_KY_GOI.MaDK | được dùng | NOT NULL | N – 1 |

**FK phức hợp thực thi ở mức vật lý (E3)** – mỗi dòng thay cho FK đơn cùng quan hệ ở bảng trên, nên không thêm mũi tên nào trên hình:

| Bảng | FK phức hợp | Tham chiếu (cần UNIQUE ở bảng đích) | Mục đích |
|---|---|---|---|
| DANG_KY_GOI | (MaHD, SoThuTu, MaGoi) | CHI_TIET_HOA_DON(MaHD, SoThuTu, MaGoi) | DANG_KY_GOI.MaGoi phải trùng gói ở dòng chi tiết |
| CHECK_IN | (MaDK, MaHV) | DANG_KY_GOI(MaDK, MaHV) | CHECK_IN.MaHV = DANG_KY_GOI.MaHV |
| LICH_HEN_PT | (MaDK, MaHV) | DANG_KY_GOI(MaDK, MaHV) | LICH_HEN_PT.MaHV = DANG_KY_GOI.MaHV |
| CHECK_IN | (MaPhong, MaCN) | PHONG(MaPhong, MaCN) | CHECK_IN.MaCN = PHONG.MaCN khi có phòng (MaPhong NULL thì FK không kiểm tra) |
<!--END:FKTABLE-->

### Bảng dẫn xuất mức logic (không thuộc ERD, không vẽ trên hình, giữ theo yêu cầu)

<!--BEGIN:DERIVED-->
- **THONG_KE_CHECKIN**(<u><i>MaCN</i></u> SMALLINT NOT NULL, <u>Ngay</u> DATE NOT NULL, <u>Gio</u> TINYINT NOT NULL, SoLuotVao INT NOT NULL, SoLuotRa INT NOT NULL)  — FK: THONG_KE_CHECKIN.MaCN -> CHI_NHANH.MaCN
- **DOANH_THU_NGAY**(<u><i>MaCN</i></u> SMALLINT NOT NULL, <u>Ngay</u> DATE NOT NULL, TongTien DECIMAL(15,0) NOT NULL, SoHoaDon INT NOT NULL)  — FK: DOANH_THU_NGAY.MaCN -> CHI_NHANH.MaCN
<!--END:DERIVED-->

Cập nhật bằng trigger/job từ CHECK_IN và HOA_DON (`TrangThai = N'Đã thanh toán'`; hủy hóa đơn trừ ngược theo ngày lập).

## 5. Bước 4b – Sơ đồ quan hệ

| File | Nội dung |
|---|---|
| `luoc_do_tong.png` | hình tổng, 20 bảng, 33 mũi tên (4000 px rộng) |
| `luoc_do_mo_dun_1.png` | Danh mục, chi nhánh, sản phẩm & tồn kho: 7 bảng, 7 mũi tên |
| `luoc_do_mo_dun_2.png` | Hội viên, loyalty, gói đăng ký & hóa đơn: 6 bảng, 12 mũi tên (+4 bảng nhạt) |
| `luoc_do_mo_dun_3.png` | Nhân sự, lịch hẹn PT & check-in: 7 bảng, 14 mũi tên (+4 bảng nhạt) |
| `luoc_do_quan_he_v4.drawio` | nguồn chỉnh sửa được, 4 trang (mở bằng diagrams.net) |
| `schema.py` | **nguồn duy nhất** của lược đồ (cột, kiểu, NULL, FK, CHECK, chỉ mục) |
| `ve_luoc_do_v4.py`, `layouts.py`, `tim_bo_cuc2.py` | vẽ hình (định tuyến vuông góc), bố cục, tìm bố cục; chạy `python ve_luoc_do_v4.py` để vẽ lại cả 4 hình + `.drawio` + `ve_ket_qua.json` |
| `kiem_tra_luoc_do.py`, `ket_qua_kiem_tra.txt` | bảng kiểm tự động và kết quả (mục 6) |
| `sinh_tai_lieu.py` | sinh các khối lược đồ/FK/thống kê trong file này từ `schema.py` |

Giữ phong cách cũ: hộp bảng (ô tên + ô cột), PK gạch liền, FK gạch đứt, PK+FK liền + đứt, mũi tên từ FK đến PK tô màu theo phân hệ, FK ghép gộp một đường, có chú giải. Thêm: ◆ khóa thay thế/UNIQUE, `[x]` dẫn xuất.
Bảng nhạt nét đứt trong hình mô-đun là bảng thuộc mô-đun khác (chỉ hiện khóa chính được tham chiếu) để mỗi FK vẫn có mũi tên.

**Số liệu bố cục** (đo bằng cùng một bộ định tuyến, đơn vị là ô lưới giao nhau giữa đường ngang và đường dọc):

| Hình | Giao cắt | Khúc gấp |
|---|--:|--:|
| Sơ đồ cũ `luoc_do_quan_he.png` (20 bảng) | 70 | 101 |
| Hình tổng mới `luoc_do_tong.png` (20 bảng) | 62 | 100 |
| Hình 1 (7 bảng) | 2 | 16 |
| Hình 2 (6 bảng + 4 nhạt) | 3 | 24 |
| Hình 3 (7 bảng + 4 nhạt) | 3 | 27 |

Nhận xét trung thực: **hình tổng chỉ bớt được khoảng 11% giao cắt** (70 → 62). Lý do cấu trúc: CHI_NHANH (9 FK đến) và HOI_VIEN (5 FK đến) là hai "trục" nên đường từ nhiều bảng ở các hàng dưới phải đi xa qua các hàng giữa. Muốn đọc sạch thì dùng **ba hình mô-đun** (tối đa 3 giao cắt mỗi hình, cộng lại 8 so với 70; số này chưa tính đến việc mỗi hình có thêm vài bảng nhạt); hình tổng dùng để thấy toàn cảnh. Bố cục hình tổng và hình 2, 3 được chọn bằng tìm kiếm tự động (`tim_bo_cuc2.py`, leo đồi chấm bằng chính bộ định tuyến), hình 1 xếp tay.

Ghi chú về file .drawio: đường nối được lưu với các điểm gấp khúc cố định, đầu mút gắn vào ô FK và ô PK; khi bạn kéo bảng, đường sẽ không tự định tuyến lại. Gạch chân đứt của cột FK có thể không hiện trong diagrams.net (thuộc tính `text-decoration-style` có thể bị lược bỏ), khi đó cột FK chỉ hiện gạch liền; PNG là bản chuẩn.

## 6. Bước 4c – Bảng kiểm tự động

Chạy `python kiem_tra_luoc_do.py`. Script đọc `schema.py`, `ve_ket_qua.json` (các ô, đường, đầu mũi tên thực sự đã vẽ ra, với tọa độ) và đọc lại XML của `.drawio`; không tin vào danh sách FK khi vẽ. Phần so sánh PNG dựa trên tọa độ các primitive đã vẽ, không phải nhận dạng ảnh. Tôi đã xem bằng mắt cả 4 hình sau khi xuất (không soi từng pixel), nhưng bảng kiểm không thay được việc bạn nhìn lại. Tôi cũng đã thử âm tính: cố ý bỏ một đường, lệch một đầu mũi tên và đổi một kiểu gạch chân trong dữ liệu hình thì script báo 4 lỗi; khôi phục lại thì đạt toàn bộ.

<!--BEGIN:CHECKLOG-->
```text
1. LƯỢC ĐỒ CHUẨN (schema.py)
  Số bảng = 20 | số cột = 127 | số khóa chính = 20 (cột PK = 25, trong đó 5 PK ghép) | số khóa ngoại = 33 (cột FK = 34)
  [ĐẠT] 20 quan hệ = 19 thực thể ERD + HLV_CHUNG_CHI
  [ĐẠT] mỗi bảng có đúng một khóa chính (có ít nhất 1 cột PK)
  [ĐẠT] mọi FK: cột tồn tại, đích là khóa chính, kiểu dữ liệu trùng khớp []
  [ĐẠT] mọi cột có cờ F đều thuộc một FK []
  [ĐẠT] không có FK trùng lặp
  [ĐẠT] cột PK+FK đều có FK
  [ĐẠT] khóa chính đều NOT NULL
  [ĐẠT] cột UNIQUE cho phép NULL đều có unique filtered index WHERE ... IS NOT NULL []
  [ĐẠT] 4 FK phức hợp vật lý (E3) đều trỏ tới bảng/cột tồn tại
  [ĐẠT] FK vật lý: cột tồn tại
  [ĐẠT] 2 bảng dẫn xuất mức logic có khai báo (không vẽ)

2. HÌNH VẼ (ve_ket_qua.json) so với lược đồ
  Hình TONG (luoc_do_tong.png, 4000 x 2368 px)
  [ĐẠT] tập bảng trên hình = 20 bảng mong đợi
  [ĐẠT] cột, thứ tự cột, kiểu gạch chân (PK/FK/PK+FK) của từng bảng khớp lược đồ
  [ĐẠT] đếm trên hình: 127 cột (lược đồ 127), 25 cột PK (lược đồ 25), 34 cột FK
  [ĐẠT] mỗi FK có đúng một đường nối: 33 FK, 33 đường vẽ, thiếu [], thừa/trùng []
  [ĐẠT] mọi đường: bắt đầu trên ô FK, mũi tên chạm ô PK, vuông góc, không xuyên bảng []
     [số liệu] giao cắt giữa các đường = 62 | số khúc gấp = 100
  [ĐẠT] chiều rộng ảnh >= 3000 px (4000)
  Hình M1 (luoc_do_mo_dun_1.png, 3400 x 1208 px)
  [ĐẠT] tập bảng trên hình = 7 bảng mong đợi
  [ĐẠT] cột, thứ tự cột, kiểu gạch chân (PK/FK/PK+FK) của từng bảng khớp lược đồ
  [ĐẠT] đếm trên hình: 38 cột (lược đồ 38), 9 cột PK (lược đồ 9), 7 cột FK
  [ĐẠT] mỗi FK có đúng một đường nối: 7 FK, 7 đường vẽ, thiếu [], thừa/trùng []
  [ĐẠT] mọi đường: bắt đầu trên ô FK, mũi tên chạm ô PK, vuông góc, không xuyên bảng []
     [số liệu] giao cắt giữa các đường = 2 | số khúc gấp = 16
  [ĐẠT] chiều rộng ảnh >= 3000 px (3400)
  Hình M2 (luoc_do_mo_dun_2.png, 3400 x 1728 px)
  [ĐẠT] tập bảng trên hình = 10 bảng mong đợi
  [ĐẠT] cột, thứ tự cột, kiểu gạch chân (PK/FK/PK+FK) của từng bảng khớp lược đồ
  [ĐẠT] đếm trên hình: 47 cột (lược đồ 47), 8 cột PK (lược đồ 8), 13 cột FK
  [ĐẠT] mỗi FK có đúng một đường nối: 12 FK, 12 đường vẽ, thiếu [], thừa/trùng []
  [ĐẠT] mọi đường: bắt đầu trên ô FK, mũi tên chạm ô PK, vuông góc, không xuyên bảng []
     [số liệu] giao cắt giữa các đường = 3 | số khúc gấp = 24
  [ĐẠT] chiều rộng ảnh >= 3000 px (3400)
  Hình M3 (luoc_do_mo_dun_3.png, 3400 x 1728 px)
  [ĐẠT] tập bảng trên hình = 11 bảng mong đợi
  [ĐẠT] cột, thứ tự cột, kiểu gạch chân (PK/FK/PK+FK) của từng bảng khớp lược đồ
  [ĐẠT] đếm trên hình: 42 cột (lược đồ 42), 8 cột PK (lược đồ 8), 14 cột FK
  [ĐẠT] mỗi FK có đúng một đường nối: 14 FK, 14 đường vẽ, thiếu [], thừa/trùng []
  [ĐẠT] mọi đường: bắt đầu trên ô FK, mũi tên chạm ô PK, vuông góc, không xuyên bảng []
     [số liệu] giao cắt giữa các đường = 3 | số khúc gấp = 27
  [ĐẠT] chiều rộng ảnh >= 3000 px (3400)
  [ĐẠT] ba hình mô-đun cộng lại phủ đúng 33 FK, mỗi FK đúng một lần (tổng = 33)
  [ĐẠT] ba mô-đun phân hoạch đúng 20 bảng

3. FILE .drawio (đọc lại XML, không dùng dữ liệu vẽ)
  [ĐẠT] 4 trang: ['M1', 'M2', 'M3', 'TONG']
  [ĐẠT] trang TONG: 33 đường nối (cell nguồn FK -> cell đích PK) = 33 FK của lược đồ
  [ĐẠT] trang M1: 7 đường nối (cell nguồn FK -> cell đích PK) = 7 FK của lược đồ
  [ĐẠT] trang M2: 12 đường nối (cell nguồn FK -> cell đích PK) = 12 FK của lược đồ
  [ĐẠT] trang M3: 14 đường nối (cell nguồn FK -> cell đích PK) = 14 FK của lược đồ

KẾT QUẢ: ĐẠT TOÀN BỘ (0 mục lỗi)
```
<!--END:CHECKLOG-->

## 7. Đề xuất thay đổi ERD (chờ duyệt, không tự sửa)

Không có thay đổi bắt buộc: mọi yêu cầu của vấn đề 1–5 giải quyết được ở mức ràng buộc/chỉ mục/trigger/bảng dẫn xuất. Hai đề xuất, đều không bắt buộc:

| # | Nội dung | Lý do | Phương án nhỏ nhất |
|--:|---|---|---|
| P1 | Nhãn ISA `ChucVu = 'PT'` → `'HLV'` | Cùng giá trị CHECK của ChucVu và tên bảng/cột (E8). Đã chốt, ghi lại để sửa trên ảnh ERD | đổi chữ trên ERD, không đổi cấu trúc |
| P2 | Liên kết "Thanh toán" HOI_VIEN – HOA_DON có HOI_VIEN bắt buộc (`MaHV NOT NULL`) | Cửa hàng bán sản phẩm lẻ cho khách vãng lai (đề: cửa hàng bán thực phẩm bổ sung/phụ kiện) sẽ không có hội viên để gắn. Đề chỉ ghi "hội viên" trên hóa đơn nên tôi giữ theo ERD | nếu muốn bán cho khách vãng lai: đổi phía HOI_VIEN thành 0..1, tức `HOA_DON.MaHV NULL` + CHECK "hóa đơn có dòng Gói thì MaHV NOT NULL". Mặc định **không đổi** |

## 8. Bảng "Quyết định cần xác nhận"

| # | Vấn đề | Lựa chọn mặc định của tôi | Phương án khác / ảnh hưởng |
|--:|---|---|---|
| D1 | Tên FK chi nhánh của NHAN_VIEN | `MaCN` (nhất quán với mọi bảng; ghi "hiện tại" trong ràng buộc E6) | giữ `MaCN_HienTai` như hình cũ: đổi 1 cột |
| D2 | Tên bảng/khóa đa trị | `HLV_CHUNG_CHI(MaHLV, ChungChi NVARCHAR(150))`, PK ghép | tên khác tùy nhóm |
| D3 | DANH_GIA_PT.MaLichHen | FK + UNIQUE + NOT NULL, `MaDanhGia` là PK riêng (không dùng MaLichHen làm PK) | dùng MaLichHen làm PK luôn (bỏ MaDanhGia) trái ERD |
| D4 | NULL / NOT NULL (ERD không nêu) | **NOT NULL**: SoDienThoai hội viên, Ho, Ten, GioiTinh, NgaySinh, ThietBi, mọi FK trừ hai FK dưới. **NULL**: TenDem, Email, CCCD, SoDienThoai nhân viên (⇒ unique filtered), MaPhong (0..1 theo ERD), MaGoi/MaSP ở CTHD (XOR), NgayKetThuc ở LICH_SU_DIEU_CHUYEN (đang công tác), ThoiGianRa, MoTa, NhanXet, LyDo | bắt CCCD NOT NULL nếu nhóm muốn mọi hội viên có CCCD (khách nước ngoài sẽ không đăng ký được) |
| D5 | Thuộc tính dẫn xuất (E5) | lưu TongTienGoc, ThanhToanThucTe, ThanhTien, NgayKetThuc; không lưu Tuoi | bảng E5 |
| D6 | Giá trị tập hợp mà đề/ERD không nêu | CNDV.TrangThai ∈ {Hoạt động, Tạm ngưng}; HOA_DON.TrangThai ∈ {Đã thanh toán, Hủy} (theo DBML cũ); ChucVu ∈ {HLV, Lễ tân, Quản lý, Bán hàng} (theo DBML cũ; đề viết "Quản lý chi nhánh", "Nhân viên bán hàng"); GioiTinh ∈ {Nam, Nữ, Khác} | thêm "Chờ thanh toán" cho VNPay không đồng bộ |
| D7 | GOI_DICH_VU.SoBuoi, ThoiHanThang | `SoBuoi NOT NULL`, 0 = không có buổi PT (đề: "nếu có"); `ThoiHanThang > 0` (vé Spa lẻ coi là 1 tháng) | `SoBuoi NULL` cho "không có" (phải xử lý NULL khi trừ BuoiConLai) |
| D8 | Thứ tự cột PK ghép TON_KHO | `(MaCN, MaSP)` (truy vấn tồn kho theo chi nhánh); hình cũ là (MaSP, MaCN) | không ảnh hưởng đúng/sai, chỉ ảnh hưởng chỉ mục |
| D9 | Ràng buộc thêm ngoài ERD | `UNIQUE (NguongChiTieu)` ở HANG_HOI_VIEN; `UNIQUE (MaNV, NgayBatDau)` ở LICH_SU_DIEU_CHUYEN | bỏ nếu muốn đúng từng chữ ERD; hai ràng buộc này không thêm cột |
| D10 | FK phức hợp vật lý (E3) | dùng 4 FK phức hợp thay FK đơn; thêm 3 UNIQUE phụ ở PHONG, DANG_KY_GOI, CHI_TIET_HOA_DON | chỉ dùng trigger (chậm hơn, dễ lỗi) |
| D11 | THONG_KE_CHECKIN | đổi `SoLuot` thành `SoLuotVao`, `SoLuotRa` để tính người có mặt; lấp đầy theo chi nhánh với SucChua hiện tại của phòng hoạt động; job tự check-out lúc đóng cửa | thêm `MaPhong` nếu cần lấp đầy theo từng phòng (CHECK_IN.MaPhong có thể NULL nên chỉ đủ cho phần có phòng) |
| D12 | Hệ quả nghiệp vụ của E1 | hạng reset về Silver mỗi 1/1 (chi tiêu năm mới = 0) | hội viên Platinum năm trước rớt hạng đầu năm; nếu không muốn, cần quy tắc "giữ hạng" (cần ERD/lược đồ mở rộng) hoặc dùng phương án dự phòng 12 tháng trượt |
| D13 | HOA_DON bắt buộc có hội viên và nhân viên | `MaHV`, `MaNV` NOT NULL theo bản số ERD | xem P2 |
| D14 | Độ mịn thời gian | LICH_SU_DIEU_CHUYEN dùng `DATE`, khoảng đóng hai đầu; điều chuyển giữa ngày không được hỗ trợ. Lịch hẹn thuộc chi nhánh của HLV vào **ngày** của NgayGioHen | dùng DATETIME2 nếu cần điều chuyển trong ngày |
| D15 | Giờ hẹn nằm trong giờ mở cửa | kiểm trong thủ tục đặt lịch (cần tra CHI_NHANH), không dùng CHECK | trigger |
| D16 | Phân vùng CHECK_IN và unique filtered index | ghi nhận rủi ro: index `UNIQUE (MaHV) WHERE ThoiGianRa IS NULL` không aligned với phân vùng theo ThoiGianVao | thay bằng kiểm tra trong thủ tục check-in với UPDLOCK; quyết định ở bước vật lý |
| D17 | Kiểu dữ liệu | `SMALLINT` cho MaCN/MaLoai/MaHang (12 chi nhánh, ít loại), `INT` cho MaHV/MaNV/MaSP/MaGoi/MaPhong, `BIGINT` cho bảng lớn (MaHD, MaDK, MaCheckIn, MaLichHen, MaDanhGia); tiền `DECIMAL(n,0)` (VNĐ không lẻ) | đổi hàng loạt nếu muốn đơn giản hơn |
| D18 | Chia mô-đun cho hình | M1: danh mục/chi nhánh/sản phẩm (7 bảng); M2: hội viên/loyalty/gói/hóa đơn (6); M3: nhân sự/vận hành (7) | chia khác nếu muốn |
| D19 | ISA | HUAN_LUYEN_VIEN.ChuyenMon, HoaHongMoiBuoi NOT NULL | cho NULL nếu HLV mới chưa có chuyên môn |
