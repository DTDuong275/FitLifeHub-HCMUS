# Ghi chú bàn giao BaoCao_GD1_FitLifeHub_v3.docx

Nguồn: ERD `CSDLA_v3.png` (chuẩn), `LUOC_DO_CHUAN.md`, `FitLifeHub.v2.dbml`, đề `2627-CSDLNC-DA.CLC.pdf`. File v2 không bị sửa (đã so mã MD5 trước/sau). v3 được dựng bằng script từ bản sao của v2 (`BaoCao_v3_scripts/`), khung/kiểu bảng/font/đánh số mục giữ như v2.

## 0. Đối chiếu ảnh ERD với bản mô tả

Ảnh ERD (bản đầu) khác bản mô tả ở **một** chỗ, cộng một nhãn cần sửa theo quyết định E8. **Cả hai đã được sửa trong `CSDLA_v3.drawio` / `CSDLA_v3.png` (xem mục 2 và 5)**:

| # | Chỗ khác | Bản mô tả | Ảnh ERD | Xử lý |
|--:|---|---|---|---|
| 1 | Liên kết “xuất ra” (CHI_TIET_HOA_DON – DANG_KY_GOI) | 1 dòng chi tiết – **0..N** gói | CHI_TIET_HOA_DON **1..1** – DANG_KY_GOI **0..1** (đã phóng to ảnh kiểm tra) | Đã sửa ERD thành 0..N (P1). Báo cáo 3.1 dòng 18: CHI_TIET_HOA_DON 1..1 – DANG_KY_GOI 0..N; khóa ngoại ghép (MaHD, SoThuTu) không có UNIQUE (RB08) |
| 2 | Nhãn chuyên biệt hóa (không phải chỗ lệch ảnh–mô tả) | `ChucVu = 'PT'` | `ChucVu = 'PT'` | Đã sửa nhãn thành `'HLV'` (P2) |

Ngoài ra `LUOC_DO_CHUAN.md` mục 0 ghi “không lệch bản số”; điểm 1 ở trên là chỗ bước trước chưa bắt được.

## 1. Thay đổi so với v2

| Mục | v2 | v3 | Lý do |
|---|---|---|---|
| Bìa, mục lục | Có trang trắng thứ 2 (đoạn trống + tiêu đề rỗng chứa ngắt trang); không có mục lục | Bỏ hai đoạn đó; trang 2 là MỤC LỤC (trường TOC cấp 1–2, 24 dòng, số trang đã khớp, cập nhật bằng F9); nội dung bìa giữ nguyên | Lỗi bố cục của v2; Q5 |
| Tổng quan | “≈120 nhân viên” trong khi 1 + 2–3 + 2–3 + 8–10 = 13–17 người/chi nhánh (156–204) và CN03 dùng ≈10 HLV/chi nhánh | ≈180 nhân viên (≈15/chi nhánh), ≈120 HLV; “≈30%” lượt ngoài cao điểm sửa thành ≈29% (4.000/14.000); thêm 2 giả định: hạng theo năm dương lịch (E1), không có bảo lưu/khung giờ/thiết bị (E7) | Kiểm lại phép tính; E1, E7 |
| QT1 | Đăng ký + bảo lưu; HOI_VIEN.MaHang, DiemTichLuy; gói không có số lượng, DANG_KY_GOI.DonGia; LICH_SU_HANG, CHI_TIEU_THANG | Bỏ bảo lưu; tạo DIEM_LOYALTY năm hiện tại khi đăng ký; dòng CHI_TIET_HOA_DON loại Gói sinh SoLuong bản ghi DANG_KY_GOI (khóa ghép MaHD, SoThuTu); FEFO | ERD, E1, E4, E7 |
| QT2 | THIET_BI/MaTB; CHECK_IN không có MaDK | ThietBi là chuỗi; CHECK_IN có MaPhong (0..1), MaDK; xác thực bằng seek IX_DK_XacThuc; mỗi hội viên một lượt chưa check-out; job đóng lượt lúc đóng cửa | ERD, E9, E10 |
| QT3 | NgayTap + KHUNG_GIO; LICH_HEN_PT không có MaHV | NgayGioHen + ThoiLuong = 60; unique filtered index cả HLV lẫn hội viên; UPDLOCK trên DANG_KY_GOI; bắt lỗi 2601/2627; kiểm tra HLV công tác tại chi nhánh vào NgayGioHen | ERD, E2, E7 |
| QT4 | CT_HOADON_SP | Dòng CHI_TIET_HOA_DON loại Sản phẩm; TON_KHO.SoLuong, CHECK ≥ 0 chặn bán vượt tồn | ERD |
| QT5 | Loyalty 12 tháng trượt: CHI_TIEU_THANG + LICH_SU_HANG + trigger 3 bước + job đầu tháng | Một UPDATE theo khóa chính DIEM_LOYALTY (MaHV, NamXet) UPDLOCK/HOLDLOCK; job 1/1; tiền hóa đơn theo TongTienGoc/GiamGia/ThanhToanThucTe; hủy hóa đơn trừ ngược năm lập | ERD, E1, E5 |
| QT6 | LICH_SU_CONG_TAC, chi nhánh hiện tại không lưu ở NHAN_VIEN | LICH_SU_DIEU_CHUYEN + NHAN_VIEN.MaCN (RB23, RB24); hoa hồng theo chi nhánh từng giai đoạn (RB25); RB29 chờ xác nhận | ERD, E6 |
| QT7 | Lấp đầy = số lượt vào / SucChua | Lấp đầy = số người đang có mặt (cộng dồn SoLuotVao − SoLuotRa) / SucChua phòng hoạt động; phân bố hạng đọc từ DIEM_LOYALTY | E9 (sửa lỗi v2) |
| Bảng tần suất | 30 chức năng; 4 Cao / 12 Trung bình / 14 Thấp | 30 chức năng; 4 / 12 / 14 (tính lại từ bảng). Sửa mô tả theo ERD; CN11 “4–5 hóa đơn/phút” → ≈1,6/phút (750 × 50% / 240 phút); CN22 ≈300 → ≈430 (12 × 36); CN16 bỏ thiết bị/khung giờ; CN29 “xét lại hạng đầu tháng” → job tạo dòng Loyalty 1/1 (1 lần/năm); CN30 “bảo lưu” → job đóng lượt check-in chưa check-out | Phép tính, quy trình đổi |
| 3.1 | 22 thực thể, 33 liên kết (v2) | 19 thực thể (10 thường + 1 lớp con + 4 kết hợp + 2 N–N có thuộc tính + 2 yếu), 32 liên kết (31 + 1 chuyên biệt hóa) đếm từ drawio, min..max từng phía; “xuất ra” là 0..N sau khi sửa ERD | ERD gốc, P1 |
| 3.2 | Tam giác ISA có “d”, [C]/[D]/[M] | Ký hiệu U (partial, một lớp con, d/o không áp dụng), (…), [x], {x}, (AK), thực thể yếu, màu hộp | E8, ERD gốc |
| 3.3 | ERD v2 + 3 hình mô-đun ERD cũ | ERD `CSDLA_v3.png` (đã sửa, xuất lại ×3 độ phân giải: 4806 × 6541 px); mô-đun ERD cũ xóa. Bước 1 chỉ tạo mô-đun của lược đồ quan hệ nên đặt ở 4.2 | ERD gốc |
| 3.4 | 19 dòng, mã RB28.. theo bản cũ | 29 dòng, mỗi dòng một mã RB, chỉ ràng buộc ERD không biểu diễn được (RB14 không đưa vào vì ERD đã có 1..N) | Yêu cầu bước này |
| 4.1 | 25 quan hệ | Quy tắc theo ERD này; bảng dẫn xuất tính (E5); đếm 19 → 20 → 22 quan hệ, 32 → 33 → 35 khóa ngoại | ERD, E5 |
| 4.2 | 25 quan hệ, chỉ tên cột | 22 quan hệ dán từ lược đồ chuẩn (PK gạch chân, FK nghiêng, [x]); bảng 35 khóa ngoại; bảng 4 khóa ngoại phức hợp; 3 hình mô-đun (trang ngang) | Lược đồ chuẩn, E3 |
| 4.3–4.4 | 21 BCNF + 4 2NF | 22 quan hệ: 16 BCNF (HLV_CHUNG_CHI đạt 4NF) + **6** 2NF (DIEM_LOYALTY, HOA_DON, CHI_TIET_HOA_DON, DANG_KY_GOI, CHECK_IN, LICH_HEN_PT); bảng 7 dư thừa E3 | E1, E3, E5 |
| 4.5 | RB01–RB31 theo thiết kế cũ | RB01–RB30 trùng mã/tên với danh mục trong DBML; mỗi RB có Loại, Bối cảnh, Nội dung, Cài đặt, bảng Thêm/Xóa/Sửa | Khớp DBML |
| 4.6 | 25 bảng, kiểu INT/IDENTITY/DEFAULT | 22 bảng, 136 cột: kiểu, NULL, PK/FK, miền giá trị, mã RB, ý nghĩa từng cột; kiểu lấy từ DBML (SMALLINT/INT/BIGINT, không IDENTITY/DEFAULT như lược đồ chuẩn) | Khớp DBML |
| Lỗi v2 đã sửa | Lấp đầy theo số lượt; UNIQUE trên cột NULL; mô tả dạng ENUM; hình mô-đun thiếu “lập”; trùng lịch hội viên coi như chỉ mục | Người có mặt; unique filtered index (RB03); CHECK (RB02); khóa ngoại HOA_DON.MaNV → NHAN_VIEN (“lập”) có trong hình mô-đun 2 và bảng 35 khóa ngoại; unique filtered (MaHV, NgayGioHen) + UPDLOCK | Mục 9 của yêu cầu |
| Mục 5 | — | Bảng đối chiếu cập nhật số liệu. Khối “Thành viên và đánh giá đóng góp” và dòng tên công cụ **giữ nguyên chỗ trống** | Yêu cầu bước này |

## 2. Đề xuất thay đổi ERD (P1, P2 đã thực hiện theo yêu cầu của bạn; P3 giữ nguyên)

| # | Nội dung | Lý do | Phương án nhỏ nhất | Bắt buộc? |
|--:|---|---|---|---|
| P1 ✅ ĐÃ LÀM | Liên kết “xuất ra”: đổi ký hiệu phía DANG_KY_GOI từ 0..1 thành 0..N | Một dòng Gói có SoLuong = n sinh n DANG_KY_GOI (E4); 0..1 chỉ đúng khi n ≤ 1 | Chỉ đổi đầu cạnh, không đổi cấu trúc/thuộc tính. Cách khác: giữ ERD và ép SoLuong = 1 cho dòng Gói (mua 2 gói = 2 dòng) | Nên làm để ERD khớp logic; logic hiện tại đã chứa được 0..N |
| P2 ✅ ĐÃ LÀM | Nhãn `ChucVu = 'PT'` → `'HLV'` | Cùng giá trị CHECK và tên MaHLV (E8, đã chốt) | Đổi chữ trên ảnh | Đã chốt |
| P3 | “Thanh toán”: HOI_VIEN 1..1 → 0..1 | Bán lẻ sản phẩm cho khách vãng lai không có hội viên | `HOA_DON.MaHV NULL` + CHECK “hóa đơn có dòng Gói thì MaHV NOT NULL” | Không, mặc định giữ nguyên |

## 3. Quyết định cần xác nhận

| # | Vấn đề | Lựa chọn mặc định của tôi | Phương án khác / ảnh hưởng |
|--:|---|---|---|
| Q1 ✅ | “xuất ra” hình 0..1 vs mô tả 0..N | Đã sửa ERD thành 0..N; báo cáo và logic khớp | — |
| Q2 ✅ | Mã RB | Dùng nguyên danh mục RB01–RB30 của DBML. Theo yêu cầu của bạn **RB29, RB30 không cài**: báo cáo giữ chúng ở trạng thái “đề xuất, chờ xác nhận” (4.5 và 3.4), không có trigger/chỉ mục tương ứng | Xóa hẳn RB29/RB30 khỏi báo cáo nếu muốn gọn |
| Q3 | Phân loại thực thể | Theo màu/hình trong ảnh: xanh lá góc vuông = thực thể kết hợp (DANG_KY_GOI, CHECK_IN, LICH_HEN_PT, LICH_SU_DIEU_CHUYEN); xanh lá bo góc = N–N có thuộc tính; cam viền đôi = yếu; HUAN_LUYEN_VIEN = lớp con. v2 coi CHECK_IN, LICH_HEN_PT là thực thể thường | Nếu nhóm hiểu khác, chỉ đổi chữ ở 3.1/3.2 |
| Q4 | Quy mô nhân sự | ≈180 nhân viên, ≈120 HLV; sửa CN11 (≈1,6 hóa đơn/phút), CN22 (≈430 lượt/ngày) vì v2 không khớp phép tính | Giữ số v2 nếu muốn, nhưng sẽ mâu thuẫn |
| Q5 ✅ | Mục lục | Đã thêm trang MỤC LỤC (trường TOC cấp 1–2) | — |
| Q6 | Điểm Loyalty | DiemThuong theo từng năm; tổng điểm hiện có = SUM các năm; ERD không có cơ chế tiêu điểm | Cần thêm thuộc tính/ thực thể nếu có đổi điểm |
| Q7 | Chọn gói khi check-in | CHECK_IN.MaDK NOT NULL nên chọn gói hợp lệ có NgayKetThuc sớm nhất (FEFO) | Cho hội viên chọn gói |
| Q8 ✅ | Mã RB cho trừ tồn kho / hủy hóa đơn | Không thêm RB31. Đã sửa Note trong `FitLifeHub.v2.dbml`: RB12 (thêm “hủy hóa đơn ⇒ hủy gói”) và TON_KHO (trừ tồn bằng UPDATE có điều kiện, hoàn lại khi hủy); DBML vẫn hợp lệ (@dbml/core: 22 bảng, 35 ref) | — |
| Q9 | Bản số tối thiểu 1 của “có phòng”, “làm việc tại” | Không cài (SQL Server không có ràng buộc trì hoãn; chi nhánh mới tạo trước phòng/nhân viên); chỉ RB14 (hóa đơn) và RB23 (nhân viên có ≥ 1 bản ghi điều chuyển) được cài | Kiểm tra trong thủ tục mở chi nhánh |
| Q10 | Chồng khoảng lịch PT (E2) | Theo E7: ThoiLuong = 60 + giờ tròn ⇒ unique filtered index đủ, không trigger chồng khoảng; nêu rõ phải thêm trigger nếu ThoiLuong nhận nhiều giá trị | Thêm trigger + tập ThoiLuong ngay |
| Q11 | Dạng chuẩn | 6 quan hệ chỉ 2NF; thêm FD (MaNV, NgayLap) → MaCN ở HOA_DON và (MaHLV, NgayGioHen) → MaCN ở LICH_HEN_PT (hệ quả RB13, RB21); NHAN_VIEN xếp BCNF vì dư thừa với LICH_SU_DIEU_CHUYEN là giữa hai quan hệ | Xếp NHAN_VIEN vào nhóm 2NF/3NF nếu giảng viên coi khác |
| Q12 | CCCD | CHAR(12), không CHECK “12 chữ số” (lược đồ chuẩn không có); GioiTinh, NgaySinh NOT NULL | Thêm CHECK; cho NULL |
| Q13 ✅ | Hình | 3 hình mô-đun lược đồ quan hệ ở 4.2 trên trang ngang; không đưa hình tổng 20 bảng. ERD đã xuất lại ×3 độ phân giải nên chữ rõ hơn bản 1572 px | Đưa thêm hình tổng |
| Q14 | Tập giá trị đề không nêu | CHI_NHANH_DICH_VU.TrangThai {Hoạt động, Tạm ngưng}; HOA_DON.TrangThai {Đã thanh toán, Hủy}; ChucVu {HLV, Lễ tân, Quản lý, Bán hàng}; GioiTinh {Nam, Nữ, Khác} | Theo D6 của lược đồ chuẩn |
| Q15 | Làm theo ba phần | Tôi chạy liền cả ba phần rồi mới gửi; bản nháp phần 1 (mục 1–3) và phần 2 (mục 4.1–4.4) lưu ở `BaoCao_v3_ban_nhap/` | Nếu muốn duyệt từng phần, các quyết định ở phần 1–2 vẫn đổi được rồi dựng lại |

## 3b. Các tệp đã thay đổi ở lượt sửa này

| Tệp | Thay đổi |
|---|---|
| `CSDLA_v3.drawio` | “xuất ra”: đầu cạnh DANG_KY_GOI ERzeroToOne → ERzeroToMany; nhãn `ChucVu = 'HLV'` |
| `CSDLA_v3.png` | Xuất lại từ drawio bằng bộ xem draw.io + Edge ở ×3 (4806 × 6541 px) |
| `CSDLA_v3_ban_goc/` | Bản gốc (drawio, png) trước khi sửa |
| `AdvDB-FitLifeHub/CSDLA_v3.drawio`, `.png` | Chép bản mới để không lệch với bản ngoài |
| `FitLifeHub.v2.dbml` | Note RB12 và TON_KHO; dòng danh mục RB12 ở đầu file. Bản trước khi sửa: `LuocDoQuanHe/FitLifeHub.v2.dbml.bak_truoc_Q8` |
| `BaoCao_GD1_FitLifeHub_v3.docx` | Dựng lại: ERD mới, bản số “xuất ra” 0..N, mục lục |

## 4. Kết quả tự kiểm tra (`BaoCao_v3_scripts/check_v3.py`, 60 mục đạt, 0 lỗi)

- Đếm: 19 thực thể (10 + 1 + 4 + 2 + 2), 32 mối liên kết (31 + 1), 22 quan hệ (19 + HLV_CHUNG_CHI + 2 dẫn xuất), 136 cột, 33 khóa ngoại ERD (+ 2 dẫn xuất = 35), 30 RB, 7 QT, 30 chức năng (4/12/14); mọi chỗ nêu số trong văn bản khớp nhau và khớp dữ liệu đếm từ chính các bảng của tài liệu.
- Mọi bảng/cột/kiểu/NULL/PK ở 4.2 và 4.6 khớp DBML hai chiều; 35 khóa ngoại khớp đúng chiều; PK gạch chân, FK in nghiêng đúng.
- Mọi mã RB được tham chiếu đều có tiêu đề ở 4.5; mọi RB đều được trỏ tới ít nhất một lần ngoài 4.5; 3.4 mỗi dòng có mã RB.
- Không còn tên bảng/cột của thiết kế cũ (chỉ còn nhắc phủ định “không có THIET_BI/KHUNG_GIO” và phương án dự phòng 12 tháng trượt).
- Mở bằng Word (không phải LibreOffice) và xuất PDF: 75 trang (v2: 62), không chữ/bảng tràn lề, không trang trắng, đủ 5 hình (logo, ERD, 3 hình mô-đun); mục lục 24 dòng khớp số trang thật; XSD của docx đạt.
- Chưa làm được: so từng ô với bản in trên giấy. Khi mở file trong Word, nếu thêm/bớt nội dung thì bấm chuột phải vào mục lục → Cập nhật trường để cập nhật số trang.
