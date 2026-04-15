from pathlib import Path
from PIL import Image

# =========================
# CONFIG
# =========================
BASE_DIR = Path("datasets/stage2_classify/sources/dv3")
RAW_DIR = Path("datasets/stage2_classify/raw")

# class ids from dv3/data.yaml
# names: ['AHPND', 'BGD', 'BSD', 'IMNV', 'TSV', 'WFD', 'WSSV', 'YHD']
WSSV_ID = 6
YHD_ID = 7   # will be mapped to YHV

SPLITS = ["train", "valid", "test"]

# crop settings
MARGIN = 0.8          # 0.5, 0.8, 1.0 ลองได้
MIN_CROP_W = 80       # ตัด crop ที่เล็กเกิน
MIN_CROP_H = 80

# output folders
OUT_WSSV = RAW_DIR / "WSSV"
OUT_YHV = RAW_DIR / "YHV"

OUT_WSSV.mkdir(parents=True, exist_ok=True)
OUT_YHV.mkdir(parents=True, exist_ok=True)


def clamp(v, lo, hi):
    return max(lo, min(v, hi))


def find_image(img_dir: Path, stem: str):
    """Find matching image file by stem."""
    for ext in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]:
        candidate = img_dir / f"{stem}{ext}"
        if candidate.exists():
            return candidate
    return None


def make_safe_name(text: str) -> str:
    """Make filename safer."""
    safe = text.replace(" ", "_")
    safe = safe.replace("(", "")
    safe = safe.replace(")", "")
    return safe


def extract_from_split(split: str):
    img_dir = BASE_DIR / split / "images"
    lbl_dir = BASE_DIR / split / "labels"

    if not img_dir.exists() or not lbl_dir.exists():
        print(f"[SKIP] {split}: images/labels not found")
        return 0, 0

    saved_wssv = 0
    saved_yhv = 0

    for label_file in lbl_dir.glob("*.txt"):
        stem = label_file.stem
        img_path = find_image(img_dir, stem)

        if img_path is None:
            print(f"[WARN] Image not found for label: {label_file.name}")
            continue

        try:
            img = Image.open(img_path).convert("RGB")
        except Exception as e:
            print(f"[WARN] Failed to open image {img_path.name}: {e}")
            continue

        w, h = img.size

        try:
            lines = label_file.read_text(encoding="utf-8").strip().splitlines()
        except Exception as e:
            print(f"[WARN] Failed to read label {label_file.name}: {e}")
            continue

        obj_idx = 0
        safe_stem = make_safe_name(stem)

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
            except Exception:
                continue

            # keep only WSSV and YHD
            if cls_id not in [WSSV_ID, YHD_ID]:
                continue

            # =========================
            # YOLO normalized -> pixel coords with margin
            # =========================
            box_w = bw * w
            box_h = bh * h
            cx = xc * w
            cy = yc * h

            new_w = box_w * (1 + MARGIN)
            new_h = box_h * (1 + MARGIN)

            x1 = int(cx - new_w / 2)
            y1 = int(cy - new_h / 2)
            x2 = int(cx + new_w / 2)
            y2 = int(cy + new_h / 2)

            x1 = clamp(x1, 0, w - 1)
            y1 = clamp(y1, 0, h - 1)
            x2 = clamp(x2, 1, w)
            y2 = clamp(y2, 1, h)

            if x2 <= x1 or y2 <= y1:
                continue

            crop = img.crop((x1, y1, x2, y2))

            cw, ch = crop.size
            if cw < MIN_CROP_W or ch < MIN_CROP_H:
                continue

            if cls_id == WSSV_ID:
                out_path = OUT_WSSV / f"dv3_{split}_wssv_{safe_stem} ({obj_idx+1}).jpg"
                try:
                    crop.save(out_path, quality=95)
                    saved_wssv += 1
                except Exception as e:
                    print(f"[WARN] Failed to save {out_path.name}: {e}")

            else:
                out_path = OUT_YHV / f"dv3_{split}_yhd_{safe_stem} ({obj_idx+1}).jpg"
                try:
                    crop.save(out_path, quality=95)
                    saved_yhv += 1
                except Exception as e:
                    print(f"[WARN] Failed to save {out_path.name}: {e}")

            obj_idx += 1

    return saved_wssv, saved_yhv


def main():
    total_wssv = 0
    total_yhv = 0

    print("=== Extracting WSSV and YHD(YHV) from dv3 ===")
    print(f"Base dir: {BASE_DIR}")
    print(f"Output WSSV: {OUT_WSSV}")
    print(f"Output YHV : {OUT_YHV}")
    print("-" * 50)

    for split in SPLITS:
        wssv_count, yhv_count = extract_from_split(split)
        total_wssv += wssv_count
        total_yhv += yhv_count
        print(f"[{split}] saved WSSV = {wssv_count}, saved YHV = {yhv_count}")

    print("-" * 50)
    print("DONE")
    print(f"Total WSSV saved: {total_wssv}")
    print(f"Total YHV saved : {total_yhv}")


if __name__ == "__main__":
    main()