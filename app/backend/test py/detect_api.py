from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
import numpy as np
import cv2
import base64

app = FastAPI()

# อนุญาตให้ Vite (localhost:5173) เรียก API ได้
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ เปลี่ยน path ให้ตรงกับของคุณ
# ถ้าเทรนเสร็จแล้ว ใช้ best.pt จะดีที่สุด
MODEL_PATH = r"C:\Users\Chayanada\Desktop\shrimp_project\runs\detect\stage1_final\weights\best.pt"
model = YOLO(MODEL_PATH)

@app.get("/health")
def health():
    return {"ok": True, "model": MODEL_PATH}

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    # อ่านไฟล์รูป -> numpy
    data = await file.read()
    nparr = np.frombuffer(data, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # รันโมเดล
    results = model.predict(img_bgr, conf=0.25, imgsz=512, device=0, verbose=False)
    r = results[0]

    # จำนวนกุ้ง = จำนวน box
    count = int(len(r.boxes)) if r.boxes is not None else 0

    # ดึง bbox (xyxy)
    boxes = []
    if r.boxes is not None and len(r.boxes) > 0:
        xyxy = r.boxes.xyxy.cpu().numpy()
        conf = r.boxes.conf.cpu().numpy()
        cls = r.boxes.cls.cpu().numpy()
        for (x1, y1, x2, y2), c, cl in zip(xyxy, conf, cls):
            boxes.append({
                "x1": float(x1), "y1": float(y1),
                "x2": float(x2), "y2": float(y2),
                "conf": float(c),
                "class": int(cl)
            })

    # รูปที่วาดกรอบแล้ว
    plotted = r.plot()  # BGR uint8
    ok, buf = cv2.imencode(".jpg", plotted)
    b64 = base64.b64encode(buf.tobytes()).decode("utf-8")

    return {
        "count": count,
        "boxes": boxes,
        "image_base64": b64
    }


# from fastapi import FastAPI, UploadFile, File
# from fastapi.middleware.cors import CORSMiddleware
# import numpy as np
# import cv2
# import onnxruntime as ort
# import base64
# import math

# app = FastAPI()

# # CORS ให้ Vite เรียกได้
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# MODEL_PATH = r"C:\Users\Chayanada\Desktop\shrimp_project\runs\detect\stage1_final\weights\best.onnx"
# IMG_SIZE = 640
# CONF_THRES = 0.25
# IOU_THRES = 0.7

# # ใช้ CPU provider ชัวร์ๆ
# sess = ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])
# inp_name = sess.get_inputs()[0].name  # "images"

# def iou(box, boxes):
#     xx1 = np.maximum(box[0], boxes[:, 0])
#     yy1 = np.maximum(box[1], boxes[:, 1])
#     xx2 = np.minimum(box[2], boxes[:, 2])
#     yy2 = np.minimum(box[3], boxes[:, 3])
#     inter = np.maximum(0, xx2 - xx1) * np.maximum(0, yy2 - yy1)
#     area1 = (box[2] - box[0]) * (box[3] - box[1])
#     area2 = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
#     return inter / (area1 + area2 - inter + 1e-6)

# def nms(boxes, scores, iou_thres=0.45):
#     idxs = scores.argsort()[::-1]
#     keep = []
#     while idxs.size > 0:
#         i = idxs[0]
#         keep.append(i)
#         if idxs.size == 1:
#             break
#         rest = idxs[1:]
#         ious = iou(boxes[i], boxes[rest])
#         idxs = rest[ious <= iou_thres]
#     return keep

# def estimate_len_px(w, h):
#     long_side = max(w, h)
#     short_side = min(w, h) + 1e-6
#     ratio = long_side / short_side
#     if ratio > 2.0:
#         return float(long_side), "H"
#     return math.sqrt(float(w*w + h*h)) * 0.8, "O"

# @app.get("/health")
# def health():
#     return {"ok": True, "model": MODEL_PATH}

# @app.post("/detect")
# async def detect(file: UploadFile = File(...)):
#     data = await file.read()
#     img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
#     if img is None:
#         return {"ok": False, "error": "Invalid image"}

#     H, W = img.shape[:2]

#     # preprocess -> (1,3,640,640)
#     x = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
#     x = x.astype(np.float32) / 255.0
#     x = np.transpose(x, (2, 0, 1))[None, ...]

#     out = sess.run(None, {inp_name: x})[0][0]  # (300,6)
#     # out: [xc,yc,w,h,conf,cls]
#     conf = out[:, 4]
#     keep = conf >= CONF_THRES
#     out = out[keep]

#     boxes_out = []
#     lengths = []

#     if out.shape[0] > 0:
#         xc, yc, bw, bh, cf, cls = out.T

#         # xywh(640) -> xyxy(original)
#         x1 = (xc - bw / 2) * (W / IMG_SIZE)
#         y1 = (yc - bh / 2) * (H / IMG_SIZE)
#         x2 = (xc + bw / 2) * (W / IMG_SIZE)
#         y2 = (yc + bh / 2) * (H / IMG_SIZE)

#         boxes = np.stack([x1, y1, x2, y2], axis=1)
#         boxes[:, 0] = np.clip(boxes[:, 0], 0, W - 1)
#         boxes[:, 1] = np.clip(boxes[:, 1], 0, H - 1)
#         boxes[:, 2] = np.clip(boxes[:, 2], 0, W - 1)
#         boxes[:, 3] = np.clip(boxes[:, 3], 0, H - 1)

#         scores = cf.astype(np.float32)
#         keep_idx = nms(boxes, scores, IOU_THRES)

#         for i in keep_idx:
#             x1, y1, x2, y2 = boxes[i].astype(int)
#             w = x2 - x1
#             h = y2 - y1
#             length_px, mode = estimate_len_px(w, h)

#             boxes_out.append([int(x1), int(y1), int(x2), int(y2), float(scores[i])])
#             lengths.append({"length_px": float(length_px), "mode": mode})

#             cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
#             cv2.putText(img, f"{scores[i]:.2f} {mode} len:{int(length_px)}px",
#                         (x1, max(0, y1 - 8)),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

#     ok, buf = cv2.imencode(".jpg", img)
#     b64 = base64.b64encode(buf).decode("utf-8")

#     return {
#         "ok": True,
#         "count": len(boxes_out),
#         "boxes": boxes_out,
#         "lengths": lengths,
#         "image_b64": b64
#     }