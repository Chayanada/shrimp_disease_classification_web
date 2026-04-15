import cv2
import sqlite3
import uuid
import os
import numpy as np
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
from fastapi.responses import StreamingResponse
from ultralytics import YOLO
from collections import OrderedDict

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
DB_PATH       = "shrimp.db"
STATIC_DIR    = "static/realtime"
IOU_THRESHOLD = 0.35

MODEL_S1_PATH = r"C:\Users\Chayanada\Desktop\shrimp_project\runs\detect\stage1_final\weights\best.pt"
S2_PATH       = r"C:\Users\Chayanada\Desktop\shrimp_project\runs\classify\efficientnet_b0_best.pth"
CLASS_NAMES   = ["Healthy", "WSSV", "YHV"]

os.makedirs(STATIC_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# โหลด Models
# ─────────────────────────────────────────────
model_s1 = YOLO(MODEL_S1_PATH)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def _load_s2():
    m = models.efficientnet_b0(weights=None)
    m.classifier[1] = nn.Linear(m.classifier[1].in_features, len(CLASS_NAMES))
    ckpt = torch.load(S2_PATH, map_location=device)
    sd   = ckpt.get("model_state_dict", ckpt)
    new_sd = OrderedDict((k[7:] if k.startswith("module.") else k, v) for k, v in sd.items())
    m.load_state_dict(new_sd)
    m.to(device).eval()
    return m

model_s2 = _load_s2()

preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

# ─────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────
def init_realtime_db():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS realtime_detections (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id      TEXT    NOT NULL,
            camera_id       TEXT    NOT NULL,
            captured_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
            track_id        TEXT    NOT NULL,
            disease_label   TEXT    NOT NULL,
            confidence      REAL    NOT NULL,
            is_diseased     INTEGER NOT NULL DEFAULT 0,
            bbox_x1         REAL,
            bbox_y1         REAL,
            bbox_x2         REAL,
            bbox_y2         REAL,
            frame_width     INTEGER,
            frame_height    INTEGER,
            crop_image_path TEXT,
            notes           TEXT DEFAULT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_rt_camera    ON realtime_detections(camera_id);
        CREATE INDEX IF NOT EXISTS idx_rt_label     ON realtime_detections(disease_label);
        CREATE INDEX IF NOT EXISTS idx_rt_captured  ON realtime_detections(captured_at);
        CREATE INDEX IF NOT EXISTS idx_rt_session   ON realtime_detections(session_id);
    """)
    conn.commit()
    conn.close()
    print("✅ realtime_detections table ready")

init_realtime_db()

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def _iou(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1 = max(ax1, bx1); iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2); iy2 = min(ay2, by2)
    inter = max(0, ix2 - ix1) * max(0, iy2 - iy1)
    if inter == 0: return 0.0
    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)
    return inter / (area_a + area_b - inter)

def _classify_crop(crop_bgr):
    rgb    = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
    tensor = preprocess(Image.fromarray(rgb)).unsqueeze(0).to(device)
    with torch.no_grad():
        out  = model_s2(tensor)
        prob = torch.softmax(out, dim=1)[0]
        idx  = prob.argmax().item()
    return CLASS_NAMES[idx], round(prob[idx].item(), 4)

# ─────────────────────────────────────────────
# Stream Generator
# ─────────────────────────────────────────────
def generate_frames(camera_source, camera_id: str = "CAM-01"):
    cap        = cv2.VideoCapture(int(camera_source) if str(camera_source).isdigit() else camera_source)
    session_id = str(uuid.uuid4())

    # ✅ เปลี่ยน: เก็บทั้ง box + label + conf ไว้ด้วยกัน
    # prev_boxes: { tid: {"box": [x1,y1,x2,y2], "label": str, "conf": float} }
    prev_boxes: dict[str, dict] = {}

    COLORS = {"Healthy": (0, 220, 120), "WSSV": (0, 60, 255), "YHV": (0, 220, 255)}

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            h, w = frame.shape[:2]

            # ── Stage 1: YOLO detect ──
            results = model_s1.predict(frame, conf=0.25, imgsz=512, verbose=False)
            boxes   = results[0].boxes

            if boxes is None or len(boxes) == 0:
                prev_boxes = {}
                ret, buf = cv2.imencode(".jpg", frame)
                yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n"
                continue

            curr_raw = [list(map(int, b.xyxy[0])) for b in boxes]

            # ── IoU matching กับเฟรมก่อน ──
            new_boxes: dict[str, dict] = {}
            unmatched_raw = list(range(len(curr_raw)))

            for tid, data in prev_boxes.items():
                old_box = data["box"]
                best_idx, best_iou = -1, IOU_THRESHOLD
                for i in unmatched_raw:
                    iou = _iou(old_box, curr_raw[i])
                    if iou > best_iou:
                        best_iou = iou; best_idx = i
                if best_idx >= 0:
                    # ✅ carry forward label เดิม ไม่ classify ซ้ำ
                    new_boxes[tid] = {
                        "box":   curr_raw[best_idx],
                        "label": data["label"],
                        "conf":  data["conf"],
                    }
                    unmatched_raw.remove(best_idx)

            # ── กุ้งใหม่ที่ไม่ match → classify ครั้งเดียว ──
            if unmatched_raw:
                conn = sqlite3.connect(DB_PATH)
                rows = []

                for i in unmatched_raw:
                    x1, y1, x2, y2 = curr_raw[i]
                    crop = frame[max(0, y1):y2, max(0, x1):x2]
                    if crop.size == 0:
                        continue

                    label, conf = _classify_crop(crop)   # ✅ classify แค่ครั้งเดียว
                    tid = str(uuid.uuid4())[:8]

                    new_boxes[tid] = {"box": curr_raw[i], "label": label, "conf": conf}

                    # บันทึก crop
                    crop_fn   = f"{session_id}_{tid}.jpg"
                    crop_path = os.path.join(STATIC_DIR, crop_fn)
                    cv2.imwrite(crop_path, crop)
                    crop_url  = f"http://127.0.0.1:8000/static/realtime/{crop_fn}"

                    rows.append((
                        session_id, camera_id,
                        tid, label, conf, 0 if label == "Healthy" else 1,
                        x1/w, y1/h, x2/w, y2/h,
                        w, h, crop_url
                    ))

                if rows:
                    conn.executemany("""
                        INSERT INTO realtime_detections
                        (session_id, camera_id, track_id, disease_label, confidence, is_diseased,
                         bbox_x1, bbox_y1, bbox_x2, bbox_y2, frame_width, frame_height, crop_image_path)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """, rows)
                    conn.commit()
                conn.close()

            prev_boxes = new_boxes

            # ── วาด bbox — ✅ ใช้ label จาก new_boxes โดยตรง ไม่ classify ซ้ำ ──
            annotated = frame.copy()
            for tid, data in new_boxes.items():
                x1, y1, x2, y2 = data["box"]
                label, conf     = data["label"], data["conf"]
                color = COLORS.get(label, (200, 200, 200))
                cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
                txt = f"{label} {int(conf * 100)}%"
                (tw, th), _ = cv2.getTextSize(txt, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
                cv2.rectangle(annotated, (x1, y1 - 22), (x1 + tw + 6, y1), color, -1)
                cv2.putText(annotated, txt, (x1 + 3, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1)

            ret, buf = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 80])
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n"

    finally:
        cap.release()

# ─────────────────────────────────────────────
# FastAPI endpoint helper
# ─────────────────────────────────────────────
def get_video_stream(camera_source, camera_id: str = "CAM-01"):
    return StreamingResponse(
        generate_frames(camera_source, camera_id),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

# ─────────────────────────────────────────────
# Summary query
# ─────────────────────────────────────────────
def get_realtime_summary(camera_id: str = None, limit: int = 50, fresh_seconds: int = 30):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    conditions = ["captured_at >= datetime('now', ?, 'localtime')"]
    params: list = [f"-{fresh_seconds} seconds"]

    if camera_id:
        conditions.append("camera_id = ?")
        params.append(camera_id)

    q = (
        "SELECT * FROM realtime_detections"
        " WHERE " + " AND ".join(conditions) +
        " ORDER BY captured_at DESC LIMIT ?"
    )
    params.append(limit)

    rows = [dict(r) for r in conn.execute(q, params).fetchall()]
    conn.close()
    return rows