"""FitLife Hub - Backend FastAPI (chi tra JSON). Moi chuc nang = 1 stored procedure.

Neu da build frontend (Source/Frontend/dist) thi backend phuc vu luon giao dien tai http://localhost:8000/
"""
import os
import re

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

import db
from functions import FUNCS, BY_ID, _norm

app = FastAPI(title="FitLife Hub API", description="Demo test")

# Cho phep frontend dev (Vite, cong 5173) goi API. Co the them nguon khac bang bien moi truong CORS_ORIGINS (cach nhau dau phay).
origins = ["http://localhost:5173", "http://127.0.0.1:5173"] + \
          [o for o in os.environ.get("CORS_ORIGINS", "").split(",") if o]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"])


def clean_error(e: Exception) -> str:
    """Loi pyodbc co tien to [42000] [Microsoft][ODBC Driver ...][SQL Server]; chi giu phan thong bao cua SP/trigger."""
    msg = str(e)
    parts = re.findall(r"\[SQL Server\](.*)", msg, flags=re.S)
    msg = parts[-1] if parts else msg
    msg = re.sub(r"\s*\(\d+\)(\s*\(SQL\w+\))?.*$", "", msg, flags=re.S)     # bo "(50011) (SQLExecDirectW)')"
    return msg.strip(" '\"),")


@app.get("/api/health", tags=["api"])
def health():
    return {"ok": True, "stub": db.STUB}


@app.get("/api/functions", tags=["api"], summary="Danh sach chuc nang va tham so")
def list_functions():
    return [{"id": f["id"], "group": f["group"], "title": f["title"], "proc": f["proc"],
             "fields": [{"name": x["name"], "label": x["label"], "type": x["type"], "default": x["default"],
                         "required": x["req"], "help": x["help"]} for x in f["fields"]]}
            for f in FUNCS]


@app.post("/api/call/{fid}", tags=["api"], summary="Goi stored procedure cua mot chuc nang")
def call_function(fid: str, body: dict):
    """body: {"TenThamSo": "gia tri", ...}. Tra ve cac result set, thoi gian (ms) va logical reads."""
    f = BY_ID.get(fid)
    if not f:
        raise HTTPException(status_code=404, detail="Khong co chuc nang nay")
    try:
        params = {fld["name"]: _norm(fld, "" if body.get(fld["name"]) is None else str(body[fld["name"]]))
                  for fld in f["fields"]}
        sets, ms, reads = db.call_proc(f["proc"], params)    # ham dong bo -> FastAPI chay trong luong rieng
    except Exception as e:
        raise HTTPException(status_code=400, detail=clean_error(e))
    return {"proc": f["proc"], "ms": ms, "logical_reads": reads, "result_sets": sets}


# Phuc vu frontend da build (npm run build) -> chay mot lenh, mot cong. Phai dat SAU cac route /api.
DIST = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Frontend", "dist"))
if os.path.isdir(DIST):
    app.mount("/", StaticFiles(directory=DIST, html=True), name="frontend")

