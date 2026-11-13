# Backend - FitLife Hub API

Hệ thống API Backend xây dựng trên **Python (FastAPI)** kết nối cơ sở dữ liệu **SQL Server** qua `pyodbc`.
Backend **chỉ gọi stored procedure** (mỗi chức năng = 1 stored procedure) và trả kết quả dạng JSON, kèm thời gian thực thi (ms) và số logical reads.

## Yêu cầu môi trường
- Python 3.10 trở lên
- SQL Server 2019/2022 (bản Developer hoặc Enterprise) đã nạp CSDL `FitLifeHub` và stored procedure
- ODBC Driver 18 for SQL Server

## Cấu trúc

```
Backend/
  main.py          Khai báo FastAPI app, các route /api/*, phục vụ frontend đã build
  db.py            Lớp truy cập DB (pyodbc): chỉ EXEC stored procedure, có chế độ STUB
  functions.py     Danh sách 29 chức năng: stored procedure + tham số của từng chức năng
  requirements.txt
  .env.example     Mẫu cấu hình (copy thành .env)
```

## Cài đặt và chạy môi trường ảo (Local Development)

1. Di chuyển vào thư mục `Source/Backend`:
   ```bash
   cd Source/Backend
   ```

2. Tạo và kích hoạt môi trường ảo:
   ```bash
   # Windows PowerShell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # Linux/macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Cài đặt thư viện:
   ```bash
   pip install -r requirements.txt
   ```

4. Cấu hình kết nối CSDL bằng file `.env` (xem bảng biến bên dưới):
   ```bash
   # Windows PowerShell
   Copy-Item .env.example .env

   # Linux/macOS
   cp .env.example .env
   ```
   Mở `.env` và chỉnh `DB_SERVER`, cách đăng nhập (`DB_TRUSTED=1` hoặc `DB_USER`/`DB_PASSWORD`).
   Để test trên DB thật, giữ `FITLIFE_STUB=0`.
   Biến đặt sẵn trong terminal vẫn được ưu tiên hơn giá trị trong `.env`.

5. Khởi động server:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   (Hoặc đứng ở thư mục gốc repo: `uvicorn main:app --app-dir Source/Backend --port 8000`)

6. Kiểm tra:
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Healthcheck: [http://localhost:8000/api/health](http://localhost:8000/api/health)

## Biến môi trường

| Biến | Mặc định | Ý nghĩa |
|------|----------|---------|
| `DB_SERVER` | `localhost` | Tên máy chủ SQL Server (đúng như ô Server name trong SSMS, ví dụ `localhost\SQLEXPRESS`) |
| `DB_NAME` | `FitLifeHub` | Tên CSDL |
| `DB_TRUSTED` | (không đặt) | Đặt `1` để dùng Windows Authentication, khi đó không cần `DB_USER`/`DB_PASSWORD` |
| `DB_USER` | `sa` | Tài khoản SQL (khi không dùng `DB_TRUSTED`) |
| `DB_PASSWORD` | (rỗng) | Mật khẩu tài khoản SQL |
| `DB_DRIVER` | `ODBC Driver 18 for SQL Server` | Tên ODBC driver |
| `FITLIFE_STUB` | (không đặt) | `0`: chạy thật, kết nối SQL Server. `1`: chế độ STUB, không đọc DB, chỉ trả về thông báo STUB (xem mục "Chế độ STUB") |
| `CORS_ORIGINS` | (rỗng) | Thêm nguồn được phép gọi API, cách nhau dấu phẩy (mặc định đã cho phép `http://localhost:5173`) |

> `DB_TRUSTED` và `FITLIFE_STUB` chỉ bật khi đặt đúng `1`.
> File `.env` đã nằm trong `.gitignore`, không commit mật khẩu lên repo.

## API

| Method | Đường dẫn | Mô tả |
|--------|-----------|-------|
| GET | `/api/health` | Kiểm tra server, cho biết có đang ở chế độ STUB không |
| GET | `/api/functions` | Danh sách chức năng và tham số (frontend dùng để dựng form) |
| POST | `/api/call/{fid}` | Gọi stored procedure của chức năng `fid`, body JSON `{"TenThamSo": "giá trị"}` |

Kết quả của `/api/call/{fid}`:
```json
{ "proc": "sp_TimHoiVien", "ms": 12.3, "logical_reads": 45, "result_sets": [{ "cols": ["..."], "rows": [["..."]] }] }
```
Lỗi từ stored procedure/trigger được rút gọn và trả về HTTP 400 với thông báo trong `detail`.

## Chế độ STUB

Chế độ STUB chỉ dùng để xem thử giao diện khi máy chưa cài SQL Server. Khi `FITLIFE_STUB=1`, backend không kết nối DB và không chạy stored procedure; mỗi lần gọi chỉ trả về bảng thông báo `STUB - chua ket noi SQL Server` cùng danh sách tham số đã nhập. Dữ liệu trong DB không được dùng.

Khi đã nạp dữ liệu và muốn chạy thật, giữ `FITLIFE_STUB=0` (hoặc không đặt biến này).

Để dùng STUB, đặt `FITLIFE_STUB=1` trong `.env`, rồi chạy:
```bash
uvicorn main:app --port 8000
```

## Phục vụ cùng frontend

Nếu đã build frontend (`npm run build` trong `Source/Frontend`), backend tự phục vụ thư mục `Source/Frontend/dist`
tại [http://localhost:8000/](http://localhost:8000/).
