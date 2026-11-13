# FitLife Hub

Hệ thống quản lý chuỗi 12 phòng tập FitLife Hub. Đồ án CSC12002 Cơ sở dữ liệu nâng cao (2627.ADB.01), giai đoạn 2: thiết kế vật lý, partition, index, bảng tổng hợp, trigger, stored procedure, ứng dụng web demo và thí nghiệm hiệu năng trước/sau tối ưu.

- Nhóm: ……  Lớp: ……  Trường ĐH Khoa học Tự nhiên – ĐHQG-HCM
- Bảng theo dõi tiến độ (Jira/Trello/GitHub Projects): ……

## Cấu trúc thư mục

```text
AdvDB-FitLifeHub/
├── Report/     # báo cáo, sơ đồ ERD, ảnh chụp
├── Source/
│   ├── Database/   # SQL Server: schema, sinh dữ liệu, trigger, stored procedure, index, benchmark
│   ├── Backend/    # FastAPI: chỉ gọi stored procedure, trả JSON
│   └── Frontend/   # React + Vite: giao diện
└── requirements.txt   # thư viện Python dùng chung (sinh dữ liệu, benchmark)
```

Chi tiết `Source/Database/`:

```text
InitDatabase/       01_schema_baseline.sql        tạo CSDL + 20 bảng (trạng thái TRƯỚC)
GeneratingData/     generate_data.py, validate_dataset.py   sinh dữ liệu (>= 70.000 dòng/bảng lớn)
Triggers/           02_triggers_and_summary.sql   bảng tổng hợp + trigger
StoredProcedures/   03_stored_procedures.sql      thủ tục nghiệp vụ và báo cáo
Validation/         04_validate_data.sql          kiểm tra khóa ngoại, ràng buộc RB
Indexes/            06_optimize_partition_index.sql (trạng thái SAU), 07_rollback_to_baseline.sql
Benchmark/          05_benchmark_queries.sql, benchmark.py, concurrency_test.py, Results/
```

## Yêu cầu

- Python 3.10 trở lên
- Node.js 18 trở lên
- SQL Server 2019/2022 bản **Developer** hoặc Enterprise (Express không hỗ trợ partition)
- ODBC Driver 18 for SQL Server

## Cài đặt và chạy

Chạy theo thứ tự: môi trường Python, database, backend, frontend. Các lệnh chạy ở thư mục gốc repo, trừ khi ghi khác.

### 1. Môi trường Python

Tạo môi trường ảo ở thư mục gốc repo và cài thư viện cho các script sinh dữ liệu, benchmark.

#### Linux / macOS

```bash
python3 -m venv .venv                 # tạo môi trường ảo, tách thư viện khỏi hệ thống
source .venv/bin/activate             # bật môi trường ảo
pip install -r requirements.txt       # cài thư viện
```

#### Windows (PowerShell)

```powershell
python -m venv .venv                  # tạo môi trường ảo, tách thư viện khỏi hệ thống
.\.venv\Scripts\Activate.ps1          # bật môi trường ảo
pip install -r requirements.txt       # cài thư viện
```

> [!NOTE]
> Đầu dòng lệnh có `(.venv)` là đã bật môi trường ảo; mỗi lần mở terminal mới phải bật lại. Nếu PowerShell chặn chạy script, chạy `Set-ExecutionPolicy -Scope Process RemoteSigned` rồi bật lại. Với CMD dùng `.venv\Scripts\activate.bat`.

### 2. Database

Chạy script tạo CSDL và 20 bảng bằng SSMS, hoặc `sqlcmd`:

```bash
sqlcmd -S localhost -E -I -f 65001 -i Source/Database/InitDatabase/01_schema_baseline.sql
```

Sinh và nạp dữ liệu. `<máy chủ>` là đúng tên ở ô Server name khi mở SSMS (ví dụ `localhost` hoặc `'localhost\SQLEXPRESS'`). Dùng cùng một cách đăng nhập cho mọi bước bên dưới:

```bash
# Windows Authentication (không cần mật khẩu)
python Source/Database/GeneratingData/generate_data.py --server <máy chủ> --trusted --scale 1.0

# Tài khoản SQL
python Source/Database/GeneratingData/generate_data.py --server <máy chủ> --user sa --password <mật khẩu> --scale 1.0
```

Kiểm tra nhanh không cần DB: thêm `--selftest --scale 0.2`.

Sau khi nạp dữ liệu, chạy lần lượt trong SSMS:

1. `Source/Database/Triggers/02_triggers_and_summary.sql` (phải chạy SAU khi nạp dữ liệu)
2. `Source/Database/StoredProcedures/03_stored_procedures.sql`
3. `Source/Database/Validation/04_validate_data.sql`


### 3. Backend

Chạy trong thư mục `Source/Backend/`, với môi trường ảo đang bật.

#### Linux / macOS

```bash
cd Source/Backend
cp .env.example .env                  # tạo file cấu hình
uvicorn main:app --port 8000          # chạy server
```

#### Windows (PowerShell)

```powershell
cd Source/Backend
copy .env.example .env                # tạo file cấu hình
uvicorn main:app --port 8000          # chạy server
```

> [!NOTE]
> Sửa `DB_SERVER` trong `Source/Backend/.env` cho khớp máy chủ SQL Server. Dùng Windows Authentication thì giữ `DB_TRUSTED=1`; dùng tài khoản SQL thì đặt `DB_USER` và `DB_PASSWORD`. Giữ `FITLIFE_STUB=0` khi chạy thật; `FITLIFE_STUB=1` chỉ để xem thử giao diện khi chưa có SQL Server (backend không đọc DB, chỉ trả về thông báo STUB). File `.env` không được commit.

Swagger UI: http://localhost:8000/docs

### 4. Frontend

Mở terminal khác, chạy trong thư mục `Source/Frontend/`. Lệnh giống nhau trên Linux, macOS và Windows.

```bash
cd Source/Frontend
npm install              # cài thư viện (lần đầu)
npm run dev              # chạy dev server
```

Mở http://localhost:5173 (Vite chuyển tiếp `/api` sang cổng 8000 nên không bị lỗi CORS).

Chạy gọn một cổng khi demo: build frontend, rồi chỉ cần chạy backend và mở http://localhost:8000 (backend tự phục vụ `Source/Frontend/dist`).

```bash
npm run build            # build bản production
```

> [!NOTE]
> Ô "Vai trò" trên giao diện chỉ lọc menu cho dễ thao tác, không phải phân quyền (CSDL chưa có bảng tài khoản).

## Thí nghiệm hiệu năng

Chạy ở thư mục gốc repo, với môi trường ảo đang bật.

```bash
# 1. Đo TRƯỚC tối ưu
python Source/Database/Benchmark/benchmark.py --server <máy chủ> --trusted --label truoc --out Source/Database/Benchmark/Results/benchmark_truoc.csv

# 2. Chạy Source/Database/Indexes/06_optimize_partition_index.sql trong SSMS, rồi đo SAU
python Source/Database/Benchmark/benchmark.py --server <máy chủ> --trusted --label sau --out Source/Database/Benchmark/Results/benchmark_sau.csv

# 3. Thử truy cập đồng thời
python Source/Database/Benchmark/concurrency_test.py --server <máy chủ> --trusted --mode naive
python Source/Database/Benchmark/concurrency_test.py --server <máy chủ> --trusted --mode safe
```

Muốn làm lại thí nghiệm: chạy `Source/Database/Indexes/07_rollback_to_baseline.sql` để quay về trạng thái trước tối ưu.

