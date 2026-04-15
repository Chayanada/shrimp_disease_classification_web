from ultralytics import YOLO
from pathlib import Path
import cv2

# ========================
# CONFIG
# ========================

MODEL_PATH = "runs/detect/stage1_final/weights/best.pt"

INPUT_DIR = Path("datasets/stage2_classify/raw")
OUTPUT_DIR = Path("datasets/stage2_classify/raw_cropped")

CLASSES = ["healthy", "WSSV", "YHV"]

CONF = 0.40
MIN_SIZE = 80  # crop ต้องกว้าง/สูงอย่างน้อย 80 px

# ========================

model = YOLO(MODEL_PATH)

for cls in CLASSES:
    input_folder = INPUT_DIR / cls
    output_folder = OUTPUT_DIR / cls
    excluded_folder = OUTPUT_DIR / "excluded"

    output_folder.mkdir(parents=True, exist_ok=True)
    excluded_folder.mkdir(parents=True, exist_ok=True)

    # รับเฉพาะไฟล์ภาพ
    images = []
    for ext in ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp"]:
        images.extend(input_folder.glob(ext))

    print(f"\nProcessing class: {cls} ({len(images)} images)")

    for img_path in images:
        img = cv2.imread(str(img_path))

        if img is None:
            print(f"[WARN] Cannot read image: {img_path}")
            continue

        h, w = img.shape[:2]

        # predict
        results = model(img, conf=CONF, verbose=False)[0]

        if results.boxes is None or len(results.boxes) == 0:
            # shrimp not detected
            save_path = excluded_folder / img_path.name
            cv2.imwrite(str(save_path), img)
            continue

        boxes = results.boxes.xyxy.cpu().numpy()

        shrimp_idx = 0

        for box in boxes:
            x1, y1, x2, y2 = box[:4]

            # ใช้ bbox จริงจาก model โดยไม่เพิ่ม margin
            x1 = max(0, int(x1))
            y1 = max(0, int(y1))
            x2 = min(w, int(x2))
            y2 = min(h, int(y2))

            if x2 <= x1 or y2 <= y1:
                continue

            crop = img[y1:y2, x1:x2]
            ch, cw = crop.shape[:2]

            # ถ้าเล็กเกิน -> ไม่ใช้
            if cw < MIN_SIZE or ch < MIN_SIZE:
                continue

            shrimp_idx += 1
            save_name = f"{img_path.stem}_shrimp{shrimp_idx}.jpg"
            save_path = output_folder / save_name

            cv2.imwrite(str(save_path), crop)

        # ถ้า detect ได้แต่ crop ใช้งานไม่ได้เลยสักตัว
        if shrimp_idx == 0:
            save_path = excluded_folder / img_path.name
            cv2.imwrite(str(save_path), img)

print("\nDONE cropping shrimp dataset")