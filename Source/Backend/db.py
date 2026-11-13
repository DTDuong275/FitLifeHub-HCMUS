"""Lop truy cap DB: CHI goi stored procedure (yeu cau de bai). Co che do STUB de chay thu khong can SQL Server."""
import os
import time
import re

from dotenv import load_dotenv

# Doc file .env (neu co) o thu muc Backend; bien da dat san trong terminal van duoc uu tien.
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

STUB =os.environ.get("FITLIFE_STUB") == "1"


def conn_str():
    # DB_TRUSTED=1: dang nhap bang tai khoan Windows (Windows Authentication), khong can DB_USER/DB_PASSWORD
    if os.environ.get("DB_TRUSTED") == "1":
        auth = "Trusted_Connection=yes"
    else:
        auth = f"UID={os.environ.get('DB_USER', 'sa')};PWD={os.environ.get('DB_PASSWORD', '')}"
    return (f"DRIVER={{{os.environ.get('DB_DRIVER', 'ODBC Driver 18 for SQL Server')}}};"
            f"SERVER={os.environ.get('DB_SERVER', 'localhost')};DATABASE={os.environ.get('DB_NAME', 'FitLifeHub')};"
            f"{auth};TrustServerCertificate=yes")


def call_proc(proc, params):
    """params: dict ten->gia tri (None bo qua). Tra ve (list result-set, thoi_gian_ms, logical_reads)."""
    if STUB:
        return _stub(proc, params)
    import pyodbc
    names = [k for k, v in params.items() if v not in (None, "")]
    sql = "SET NOCOUNT ON; EXEC dbo.%s %s" % (proc, ", ".join(f"@{k}=?" for k in names))
    args = [params[k] for k in names]
    conn = pyodbc.connect(conn_str(), autocommit=True)
    try:
        cur = conn.cursor()
        cur.execute("SET STATISTICS IO ON")
        t = time.perf_counter()
        cur.execute(sql, args)
        sets = []
        while True:
            if cur.description:
                cols = [d[0] for d in cur.description]
                sets.append({"cols": cols, "rows": [list(r) for r in cur.fetchmany(500)]})
            if not cur.nextset():
                break
        ms = (time.perf_counter() - t) * 1000
        reads = sum(int(x) for m in getattr(cur, "messages", []) for x in re.findall(r"logical reads (\d+)", m[1]))
        return sets, round(ms, 1), reads
    finally:
        conn.close()


def _stub(proc, params):
    return ([{"cols": ["Ok", "Msg", "Proc"], "rows": [[True, "STUB - chua ket noi SQL Server", proc]]},
             {"cols": ["Tham so", "Gia tri"], "rows": [[k, v] for k, v in params.items()]}], 1.0, 0)
