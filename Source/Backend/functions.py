# TODO: functions.py (backend FastAPI)
"""Khai bao 29 chuc nang: moi chuc nang = 1 stored procedure + danh sach tham so.

=====================================================================
HUONG DAN: THEM MOT STORED PROCEDURE MOI VAO HE THONG
=====================================================================
Backend khong co code rieng cho tung SP. Chi can 2 buoc:
  (1) Cai SP vao SQL Server (file Source/Database/StoredProcedures/*.sql)
  (2) Them 1 dict(...) vao cuoi list FUNCS ben duoi  -> xong, khong sua file nao khac.

Cau truc:
  FUNCS   = list cac dict. 1 dict = 1 chuc nang = 1 stored procedure.
  BY_ID   = {id: dict} tao tu FUNCS, de main.py tra cuu nhanh theo {fid}.
  F(...)  = ham viet tat tao 1 dict mo ta 1 THAM SO cua SP (1 o nhap tren form).

Cach dich tu SQL sang dict (vi du):

  SQL:
    CREATE PROCEDURE dbo.sp_CheckIn
        @MaHV CHAR(8),                  -- bat buoc
        @MaPhong CHAR(8) = NULL,        -- co "= NULL" => khong bat buoc
        @ThietBi VARCHAR(50)

  PYTHON:
    dict(id="checkin", group="Check-in", title="Check-in", proc="sp_CheckIn", fields=[
        F("MaHV", "Mã HV"),
        F("MaPhong", "Phòng", req=False),
        F("ThietBi", "Thiết bị")])

Y nghia cac key cua dict chuc nang:
  id      Tu dat, ngan gon, KHONG trung. La {fid} trong  POST /api/call/{fid}.
  group   Tu dat. Ten nhom de gom menu tren giao dien.
  title   Tu dat. Ten hien thi cua chuc nang.
  proc    PHAI KHOP ten SP trong SQL, bo tien to "dbo." (db.py tu them).
  fields  List cac F(...), moi F ung voi dung 1 tham so @Xxx cua SP.

Y nghia tham so cua F(name, label, typ, default, req, help):
  name     PHAI KHOP ten tham so SP, bo dau "@", dung hoa/thuong (@MaHV -> "MaHV").
           Day la key trong JSON gui len va ten trong  EXEC sp @MaHV=?.
           Sai chinh ta => SQL bao loi "@xxx is not a parameter".
  label    Nhan tieng Viet hien tren form (nguoi dung doc). Khong anh huong SQL.
  typ      Kieu o nhap (xem ben duoi). Mac dinh "text".
  default  Gia tri dien san tren form.
  req      True = bat buoc nhap. Tham so SP co "= NULL" thi dat req=False.
  help     Ghi chu nho duoi o nhap.
  (Luu y: ten bien la "typ", se thanh key "type" trong dict, de khoi trung ham type() cua Python.)

Chon typ theo kieu du lieu SQL:
  CHAR / VARCHAR / NVARCHAR   -> "text"            (mac dinh, khong can ghi)
  INT / BIGINT / DECIMAL      -> "number"
  DATE                        -> "date"
  DATETIME                    -> "datetime-local"
  tham so nhan chuoi JSON     -> "json"            (vd @DongJson cua sp_LapHoaDon)
  chi duoc chon vai gia tri   -> "select:A|B|C"    (vd "select:M|F|O")

Meo:
  - Tham so SP co gia tri mac dinh (= NULL) co the BO QUA khong khai bao trong fields;
    khi do khong duoc truyen va SP tu dung gia tri mac dinh cua no.
  - Truong de trong ("") duoc _norm() doi thanh None => NULL trong SQL.
  - SP chi ghi (khong SELECT) van goi duoc; SP co SELECT thi cac result set
    duoc tra ve cho frontend hien thanh bang.
=====================================================================
"""
import json

# kieu truong: text | date | datetime-local | number | json | select:<a|b|c>
def F(name, label, typ="text", default="", req=True, help=""):
    """Tao dict mo ta 1 tham so SP. name = ten tham so SQL (khong co @), label = nhan hien thi."""
    return dict(name=name, label=label, type=typ, default=default, req=req, help=help)

HINH_THUC = "select:Tiền mặt|VNPay|Thẻ"
FUNCS = [
    # Example cho sp_DangKyHoiVien
    # dict(id="dangky", group="Hội viên", title="Đăng ký hội viên", proc="sp_DangKyHoiVien", 
    # fields=[
    #    F("Ho", "Họ"), F("TenDem", "Tên đệm", req=False), F("Ten", "Tên"), F("SoDienThoai", "SĐT"),
    #    F("Email", "Email", req=False), F("CCCD", "CCCD (12 số)"), F("GioiTinh", "Giới tính", "select:M|F|O"),
    #    F("NgaySinh", "Ngày sinh", "date", "2000-01-01")])
]
BY_ID = {f["id"]: f for f in FUNCS}


def _norm(f, raw):
    if raw in (None, ""):
        return None
    if f["type"] == "number":
        return int(raw)
    if f["type"] == "datetime-local":
        return raw.replace("T", " ") + ":00" if len(raw) == 16 else raw.replace("T", " ")
    if f["type"] == "json":
        json.loads(raw)      # bao loi som neu JSON sai
    return raw
