from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# =========================
# CONFIG
# =========================
BASE_DIR = Path("datasets/stage2_classify/sources/dv3")
OUT_DIR = Path("datasets/stage2_classify/debug_vis_dv3")
OUT_DIR.mkdir(parents=True, exist_ok=True)

SPLIT = "train"   # เปลี่ยนเป็น train / valid / test ได้
MAX_IMAGES = 30   # จำนวนภาพที่อยากให้เซฟออกมา

# class names from dv3/data.yaml
CLASS_NAMES = ['AHPND', 'BGD', 'BSD', 'IMNV', 'TSV', 'WFD', 'WSSV', 'YHD']

TARGET_ONLY = False   # True = วาดเฉพาะ WSSV/YHD, False = วาดทุก class
TARGET_IDS = {6, 7}   # 6=WSSV, 7=YHD


def clamp(v, lo, hi):
    return max(lo, min(v, hi))


def find_image(img_dir: Path, stem: str):
    for ext in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]:
        p = img_dir / f"{stem}{ext}"
        if p.exists():
            return p
    return None


def main():
    img_dir = BASE_DIR / SPLIT / "images"
    lbl_dir = BASE_DIR / SPLIT / "labels"

    if not img_dir.exists() or not lbl_dir.exists():
        print(f"Split not found: {SPLIT}")
        return

    count = 0

    for label_file in lbl_dir.glob("*.txt"):
        if count >= MAX_IMAGES:
            break

        stem = label_file.stem
        img_path = find_image(img_dir, stem)
        if img_path is None:
            print(f"Image not found for {label_file.name}")
            continue

        try:
            img = Image.open(img_path).convert("RGB")
        except Exception as e:
            print(f"Open image failed: {img_path.name} -> {e}")
            continue

        draw = ImageDraw.Draw(img)
        w, h = img.size

        try:
            lines = label_file.read_text(encoding="utf-8").strip().splitlines()
        except Exception as e:
            print(f"Read label failed: {label_file.name} -> {e}")
            continue

        found_any = False

        for line in lines:
            parts = line.strip().split()
            if len(parts) != 5:
                continue

            try:
                cls_id = int(float(parts[0]))
                xc = float(parts[1])
                yc = float(parts[2])
                bw = float(parts[3])
                bh = float(parts[4])
            except:
                continue

            if TARGET_ONLY and cls_id not in TARGET_IDS:
                continue

            x1 = int((xc - bw / 2) * w)
            y1 = int((yc - bh / 2) * h)
            x2 = int((xc + bw / 2) * w)
            y2 = int((yc + bh / 2) * h)

            x1 = clamp(x1, 0, w - 1)
            y1 = clamp(y1, 0, h - 1)
            x2 = clamp(x2, 1, w)
            y2 = clamp(y2, 1, h)

            # สีแยกง่ายๆ
            if cls_id == 6:
                color = "red"      # WSSV
            elif cls_id == 7:
                color = "yellow"   # YHD
            else:
                color = "lime"

            draw.rectangle([x1, y1, x2, y2], outline=color, width=3)

            label = CLASS_NAMES[cls_id] if cls_id < len(CLASS_NAMES) else str(cls_id)
            text_pos = (x1 + 3, max(0, y1 - 18))
            draw.text(text_pos, label, fill=color)

            found_any = True

        if found_any:
            out_path = OUT_DIR / f"{SPLIT}_{stem}.jpg"
            img.save(out_path, quality=95)
            count += 1
            print(f"Saved: {out_path.name}")

    print("Done")


if __name__ == "__main__":
    main()