# import onnxruntime as ort

# MODEL_PATH = r"runs/detect/detect12k_balanced/weights/best.pt"
# sess = ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])

# print("Input:", [(i.name, i.shape, i.type) for i in sess.get_inputs()])
# print("Output:", [(o.name, o.shape, o.type) for o in sess.get_outputs()])
# print("ONNX loaded OK ✅")

from ultralytics import YOLO

# 1. โหลดโมเดล .pt ต้นฉบับ
model = YOLO(r"runs/detect/detect12k_balanced/weights/best.pt")

# 2. สั่ง Export เป็น format onnx
# dynamic=True ช่วยให้รองรับขนาดภาพที่หลากหลาย (เผื่อไว้)
path_saved = model.export(format="onnx", imgsz=640, dynamic=True)

print(f"Export สำเร็จแล้ว! ไฟล์อยู่ที่: {path_saved}")