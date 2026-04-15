# from fastapi import FastAPI, File, UploadFile, Form, Query
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles

# from auth import UserSchema, register_logic, login_logic
# from realtime import get_video_stream, get_realtime_summary
# import detector

# app = FastAPI()

# app.mount("/static", StaticFiles(directory="static"), name="static")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.post("/register")
# async def register(user: UserSchema):
#     return register_logic(user)

# @app.post("/login")
# async def login(user: UserSchema):
#     return login_logic(user)

# @app.post("/upload_detection")
# async def upload_detection(username: str = Form(...), file: UploadFile = File(...)):
#     content = await file.read()
#     return detector.process_detection(username, content)

# @app.get("/history")
# def get_history():
#     return {"message": "รอทำ API สำหรับดึงประวัติภายหลัง"}

# # ── Realtime stream ──────────────────────────────────────
# # ตัวอย่างการเรียกใช้:
# #   /video_feed?source=0            (webcam index 0)
# #   /video_feed?source=http://IP:PORT/video_feed&camera_id=CAM-01
# @app.get("/video_feed")
# async def video_feed(
#     source:    str = Query("0",       description="Camera source: index หรือ URL"),
#     camera_id: str = Query("CAM-01",  description="ชื่อกล้อง สำหรับบันทึก DB"),
# ):
#     return get_video_stream(source, camera_id)

# # ── Realtime summary (สำหรับ Dashboard) ─────────────────
# @app.get("/realtime_summary")
# def realtime_summary(camera_id: str = None, limit: int = 50, fresh_seconds: int = 30):
#     # คืนเฉพาะข้อมูลที่ Pi บันทึกใหม่ใน fresh_seconds วินาทีที่ผ่านมา
#     # ถ้า Pi ไม่ได้รัน → คืน [] → frontend แสดง "รอสัญญาณ" โดยอัตโนมัติ
#     return get_realtime_summary(camera_id, limit, fresh_seconds)

# @app.get("/")
# def read_root():
#     return {"message": "KungKamKram Export API is running"}

# @app.get("/dashboard_summary")
# def dashboard_summary():
#     """
#     รวมข้อมูลทุกอย่างที่ Dashboard ต้องการใน 1 call
#     คืน:
#       classification  - สถิติจาก table detections
#       realtime        - สถิติจาก table realtime_detections (today)
#       recent_classify - 5 รายการล่าสุดจาก detections
#       recent_realtime - 5 alert ล่าสุดจาก realtime_detections (is_diseased=1)
#     """
#     import sqlite3
#     from datetime import date
#     conn = sqlite3.connect("shrimp.db")
#     conn.row_factory = sqlite3.Row
#     today = date.today().isoformat()

#     # ── Classification stats (จาก table detections) ──────────────────────
#     cls_row = conn.execute("""
#         SELECT
#             COUNT(*)                                            AS total_scans,
#             SUM(CASE WHEN (wssv_count+yhv_count) > 0
#                      THEN 1 ELSE 0 END)                        AS infected_scans,
#             SUM(CASE WHEN healthy_count > 0
#                           AND (wssv_count+yhv_count) = 0
#                      THEN 1 ELSE 0 END)                        AS healthy_scans,
#             SUM(healthy_count)                                  AS total_healthy,
#             SUM(wssv_count)                                     AS total_wssv,
#             SUM(yhv_count)                                      AS total_yhv
#         FROM detections
#     """).fetchone()

#     top_cls = conn.execute("""
#         SELECT disease_label, COUNT(*) AS cnt FROM (
#             SELECT CASE
#                 WHEN wssv_count >= yhv_count AND wssv_count > 0 THEN 'WSSV'
#                 WHEN yhv_count  >  wssv_count                   THEN 'YHV'
#                 ELSE 'Healthy' END AS disease_label
#             FROM detections
#         ) GROUP BY disease_label ORDER BY cnt DESC LIMIT 1
#     """).fetchone()

#     # ── Realtime stats today (จาก table realtime_detections) ─────────────
#     rt_row = conn.execute("""
#         SELECT
#             COUNT(*)                                        AS total_detections,
#             SUM(CASE WHEN is_diseased=1 THEN 1 ELSE 0 END) AS diseased,
#             SUM(CASE WHEN disease_label='Healthy' THEN 1 ELSE 0 END) AS healthy,
#             SUM(CASE WHEN disease_label='WSSV'    THEN 1 ELSE 0 END) AS wssv,
#             SUM(CASE WHEN disease_label='YHV'     THEN 1 ELSE 0 END) AS yhv,
#             COUNT(DISTINCT camera_id)                       AS active_cameras,
#             COUNT(DISTINCT session_id)                      AS sessions
#         FROM realtime_detections
#         WHERE DATE(captured_at) = ?
#     """, (today,)).fetchone()

#     # ── Recent classifications (5 ล่าสุด) ────────────────────────────────
#     recent_cls = [dict(r) for r in conn.execute("""
#         SELECT id, username, image_path,
#                healthy_count, wssv_count, yhv_count, created_at
#         FROM detections ORDER BY created_at DESC LIMIT 5
#     """).fetchall()]

#     # ── Recent realtime disease alerts (5 ล่าสุด is_diseased=1) ──────────
#     recent_rt = [dict(r) for r in conn.execute("""
#         SELECT camera_id, disease_label, confidence, captured_at, crop_image_path
#         FROM realtime_detections
#         WHERE is_diseased = 1
#         ORDER BY captured_at DESC LIMIT 5
#     """).fetchall()]

#     conn.close()

#     return {
#         "classification": {
#             "total_scans":    cls_row["total_scans"]    or 0,
#             "infected_scans": cls_row["infected_scans"] or 0,
#             "healthy_scans":  cls_row["healthy_scans"] or 0,
#             "total_healthy":  cls_row["total_healthy"]  or 0,
#             "total_wssv":     cls_row["total_wssv"]     or 0,
#             "total_yhv":      cls_row["total_yhv"]      or 0,
#             "top_disease":    top_cls["disease_label"]  if top_cls else "—",
#         },
#         "realtime": {
#             "total_detections": rt_row["total_detections"] or 0,
#             "diseased":         rt_row["diseased"]         or 0,
#             "healthy":          rt_row["healthy"]          or 0,
#             "wssv":             rt_row["wssv"]             or 0,
#             "yhv":              rt_row["yhv"]              or 0,
#             "active_cameras":   rt_row["active_cameras"]   or 0,
#             "sessions":         rt_row["sessions"]         or 0,
#         },
#         "recent_classify": recent_cls,
#         "recent_realtime": recent_rt,
#     }



from fastapi import FastAPI, File, UploadFile, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from auth import UserSchema, register_logic, login_logic
from realtime import get_video_stream, get_realtime_summary
import detector

import os
import sqlite3
from datetime import date

try:
    import psutil
except ImportError:
    psutil = None


app = FastAPI()

if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register")
async def register(user: UserSchema):
    return register_logic(user)

@app.post("/login")
async def login(user: UserSchema):
    return login_logic(user)

@app.post("/upload_detection")
async def upload_detection(username: str = Form(...), file: UploadFile = File(...)):
    content = await file.read()
    return detector.process_detection(username, content)

@app.get("/history")
def get_history():
    return {"message": "รอทำ API สำหรับดึงประวัติภายหลัง"}

@app.get("/video_feed")
async def video_feed(
    source: str = Query("0", description="Camera source: index หรือ URL"),
    camera_id: str = Query("CAM-01", description="ชื่อกล้อง สำหรับบันทึก DB"),
):
    return get_video_stream(source, camera_id)

@app.get("/realtime_summary")
def realtime_summary(camera_id: str = None, limit: int = 50, fresh_seconds: int = 30):
    return get_realtime_summary(camera_id, limit, fresh_seconds)

@app.get("/node_status")
def node_status():
    cpu = 0.0
    memory = 0.0
    temp = 0.0

    if psutil is not None:
        try:
            cpu = psutil.cpu_percent(interval=0.2)
        except Exception:
            cpu = 0.0

        try:
            memory = psutil.virtual_memory().percent
        except Exception:
            memory = 0.0

        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for _, entries in temps.items():
                    if entries:
                        temp = float(entries[0].current)
                        break
        except Exception:
            temp = 0.0

    if temp == 0.0:
        thermal_candidates = [
            "/sys/class/thermal/thermal_zone0/temp",
            "/sys/class/hwmon/hwmon0/temp1_input",
        ]
        for path in thermal_candidates:
            try:
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        raw = f.read().strip()
                    temp = float(raw) / 1000.0
                    break
            except Exception:
                pass

    return {
        "status": "success",
        "cpu": round(float(cpu), 1),
        "memory": round(float(memory), 1),
        "temp": round(float(temp), 1),
    }

@app.get("/")
def read_root():
    return {"message": "KungKamKram Export API is running"}

@app.get("/dashboard_summary")
def dashboard_summary():
    conn = sqlite3.connect("shrimp.db")
    conn.row_factory = sqlite3.Row
    today = date.today().isoformat()

    def safe_int(value):
        return int(value or 0)

    try:
        cls_row = conn.execute("""
            SELECT
                COUNT(*) AS total_scans,
                SUM(CASE WHEN (wssv_count + yhv_count) > 0 THEN 1 ELSE 0 END) AS infected_scans,
                SUM(CASE WHEN healthy_count > 0 AND (wssv_count + yhv_count) = 0 THEN 1 ELSE 0 END) AS healthy_scans,
                SUM(healthy_count) AS total_healthy,
                SUM(wssv_count) AS total_wssv,
                SUM(yhv_count) AS total_yhv
            FROM detections
        """).fetchone()

        top_cls = conn.execute("""
            SELECT disease_label, COUNT(*) AS cnt
            FROM (
                SELECT CASE
                    WHEN wssv_count >= yhv_count AND wssv_count > 0 THEN 'WSSV'
                    WHEN yhv_count > wssv_count THEN 'YHV'
                    ELSE 'Healthy'
                END AS disease_label
                FROM detections
            )
            GROUP BY disease_label
            ORDER BY cnt DESC
            LIMIT 1
        """).fetchone()

        rt_row = conn.execute("""
            SELECT
                COUNT(*) AS total_detections,
                SUM(CASE WHEN is_diseased = 1 THEN 1 ELSE 0 END) AS diseased,
                SUM(CASE WHEN disease_label = 'Healthy' THEN 1 ELSE 0 END) AS healthy,
                SUM(CASE WHEN disease_label = 'WSSV' THEN 1 ELSE 0 END) AS wssv,
                SUM(CASE WHEN disease_label = 'YHV' THEN 1 ELSE 0 END) AS yhv,
                COUNT(DISTINCT camera_id) AS active_cameras,
                COUNT(DISTINCT session_id) AS sessions
            FROM realtime_detections
            WHERE DATE(captured_at) = ?
        """, (today,)).fetchone()

        recent_cls = [dict(r) for r in conn.execute("""
            SELECT
                id,
                username,
                image_path,
                healthy_count,
                wssv_count,
                yhv_count,
                created_at
            FROM detections
            ORDER BY created_at DESC
            LIMIT 5
        """).fetchall()]

        recent_rt = [dict(r) for r in conn.execute("""
            SELECT
                camera_id,
                disease_label,
                confidence,
                captured_at
            FROM realtime_detections
            WHERE is_diseased = 1
            ORDER BY captured_at DESC
            LIMIT 5
        """).fetchall()]

        classification = {
            "total_scans": safe_int(cls_row["total_scans"]) if cls_row else 0,
            "infected_scans": safe_int(cls_row["infected_scans"]) if cls_row else 0,
            "healthy_scans": safe_int(cls_row["healthy_scans"]) if cls_row else 0,
            "total_healthy": safe_int(cls_row["total_healthy"]) if cls_row else 0,
            "total_wssv": safe_int(cls_row["total_wssv"]) if cls_row else 0,
            "total_yhv": safe_int(cls_row["total_yhv"]) if cls_row else 0,
            "top_disease": top_cls["disease_label"] if top_cls else "—",
        }

        realtime = {
            "total_detections": safe_int(rt_row["total_detections"]) if rt_row else 0,
            "diseased": safe_int(rt_row["diseased"]) if rt_row else 0,
            "healthy": safe_int(rt_row["healthy"]) if rt_row else 0,
            "wssv": safe_int(rt_row["wssv"]) if rt_row else 0,
            "yhv": safe_int(rt_row["yhv"]) if rt_row else 0,
            "active_cameras": safe_int(rt_row["active_cameras"]) if rt_row else 0,
            "sessions": safe_int(rt_row["sessions"]) if rt_row else 0,
        }

        return {
            "classification": classification,
            "realtime": realtime,
            "recent_classify": recent_cls,
            "recent_realtime": recent_rt,
        }

    except sqlite3.OperationalError:
        return {
            "classification": {
                "total_scans": 0,
                "infected_scans": 0,
                "healthy_scans": 0,
                "total_healthy": 0,
                "total_wssv": 0,
                "total_yhv": 0,
                "top_disease": "—",
            },
            "realtime": {
                "total_detections": 0,
                "diseased": 0,
                "healthy": 0,
                "wssv": 0,
                "yhv": 0,
                "active_cameras": 0,
                "sessions": 0,
            },
            "recent_classify": [],
            "recent_realtime": [],
        }
    finally:
        conn.close()