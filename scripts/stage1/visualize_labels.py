from pathlib import Path
import random
import cv2

DATASET_ROOT = Path(r"C:\Users\Chayanada\Desktop\shrimp_project\datasets\stage1_detect\sources\v4")
SPLIT = "train"     # train / valid / test
N = 20              # จำนวนรูปที่จะสุ่มดู
IMG_EXTS = [".jpg", ".jpeg", ".png"]

img_dir = DATASET_ROOT / SPLIT / "images"
lbl_dir = DATASET_ROOT / SPLIT / "labels"

imgs = [p for p in img_dir.iterdir() if p.suffix.lower() in IMG_EXTS]
random.shuffle(imgs)
imgs = imgs[:N]

def yolo_to_xyxy(xc, yc, w, h, W, H):
    x1 = int((xc - w/2) * W)
    y1 = int((yc - h/2) * H)
    x2 = int((xc + w/2) * W)
    y2 = int((yc + h/2) * H)
    return x1, y1, x2, y2

for img_path in imgs:
    label_path = lbl_dir / (img_path.stem + ".txt")
    img = cv2.imread(str(img_path))
    if img is None:
        print("อ่านภาพไม่ได้:", img_path)
        continue

    H, W = img.shape[:2]

    if label_path.exists():
        lines = label_path.read_text(encoding="utf-8").splitlines()
        for line in lines:
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) != 5:
                print("Label format แปลก:", label_path, "=>", line)
                continue
            cls, xc, yc, w, h = parts
            cls = int(cls)
            xc, yc, w, h = map(float, [xc, yc, w, h])

            x1, y1, x2, y2 = yolo_to_xyxy(xc, yc, w, h, W, H)

            # clip กันหลุดภาพ
            x1 = max(0, min(W-1, x1))
            y1 = max(0, min(H-1, y1))
            x2 = max(0, min(W-1, x2))
            y2 = max(0, min(H-1, y2))

            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, f"cls:{cls}", (x1, max(0, y1-5)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    else:
        cv2.putText(img, "NO LABEL", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

    cv2.imshow("bbox check", img)
    key = cv2.waitKey(0)  # กดปุ่มเพื่อไปภาพถัดไป
    if key == 27:         # ESC ออก
        break

cv2.destroyAllWindows()