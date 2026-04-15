from pathlib import Path
import shutil

# =========================
# CONFIG
# =========================
BASE_DIR = Path("datasets/stage2_classify/sources/dv3")
RAW_DIR = Path("datasets/stage2_classify/raw")

SPLITS = ["train", "valid", "test"]

# class ids from dv3/data.yaml
# names: ['AHPND', 'BGD', 'BSD', 'IMNV', 'TSV', 'WFD', 'WSSV', 'YHD']
WSSV_ID = 6
YHD_ID = 7

# output folders
OUT_WSSV = RAW_DIR / "WSSV"
OUT_YHV = RAW_DIR / "YHV"
OUT_MIXED = RAW_DIR / "mixed_disease"

OUT_WSSV.mkdir(parents=True, exist_ok=True)
OUT_YHV.mkdir(parents=True, exist_ok=True)
OUT_MIXED.mkdir(parents=True, exist_ok=True)


def find_image(img_dir: Path, stem: str):
    """Find matching image file by stem."""
    for ext in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]:
        candidate = img_dir / f"{stem}{ext}"
        if candidate.exists():
            return candidate
    return None


def make_safe_name(text: str) -> str:
    safe = text.replace(" ", "_")
    safe = safe.replace("(", "")
    safe = safe.replace(")", "")
    return safe


def process_split(split: str):
    img_dir = BASE_DIR / split / "images"
    lbl_dir = BASE_DIR / split / "labels"

    if not img_dir.exists() or not lbl_dir.exists():
        print(f"[SKIP] {split}: images/labels not found")
        return 0, 0, 0

    count_wssv = 0
    count_yhv = 0
    count_mixed = 0

    for label_file in lbl_dir.glob("*.txt"):
        stem = label_file.stem
        img_path = find_image(img_dir, stem)

        if img_path is None:
            print(f"[WARN] Image not found for label: {label_file.name}")
            continue

        try:
            lines = label_file.read_text(encoding="utf-8").strip().splitlines()
        except Exception as e:
            print(f"[WARN] Failed to read label {label_file.name}: {e}")
            continue

        class_ids = set()

        for line in lines:
            parts = line.strip().split()
            if len(parts) != 5:
                continue

            try:
                cls_id = int(float(parts[0]))
            except Exception:
                continue

            class_ids.add(cls_id)

        has_wssv = WSSV_ID in class_ids
        has_yhd = YHD_ID in class_ids

        safe_stem = make_safe_name(stem)

        # ถ้ามีทั้ง WSSV และ YHD -> mixed
        if has_wssv and has_yhd:
            out_path = OUT_MIXED / f"dv3_{split}_mixed_{safe_stem}.jpg"
            try:
                shutil.copy(img_path, out_path)
                count_mixed += 1
            except Exception as e:
                print(f"[WARN] Failed to copy mixed image {img_path.name}: {e}")

        # ถ้ามีแค่ WSSV
        elif has_wssv and not has_yhd:
            out_path = OUT_WSSV / f"dv3_{split}_wssv_{safe_stem}.jpg"
            try:
                shutil.copy(img_path, out_path)
                count_wssv += 1
            except Exception as e:
                print(f"[WARN] Failed to copy WSSV image {img_path.name}: {e}")

        # ถ้ามีแค่ YHD -> YHV
        elif has_yhd and not has_wssv:
            out_path = OUT_YHV / f"dv3_{split}_yhd_{safe_stem}.jpg"
            try:
                shutil.copy(img_path, out_path)
                count_yhv += 1
            except Exception as e:
                print(f"[WARN] Failed to copy YHV image {img_path.name}: {e}")

        # class อื่น ไม่สนใจ
        else:
            continue

    return count_wssv, count_yhv, count_mixed


def main():
    total_wssv = 0
    total_yhv = 0
    total_mixed = 0

    print("=== Extract dv3 full images for WSSV / YHV / mixed ===")
    print(f"Base dir   : {BASE_DIR}")
    print(f"Output WSSV: {OUT_WSSV}")
    print(f"Output YHV : {OUT_YHV}")
    print(f"Output mix : {OUT_MIXED}")
    print("-" * 60)

    for split in SPLITS:
        c_wssv, c_yhv, c_mixed = process_split(split)
        total_wssv += c_wssv
        total_yhv += c_yhv
        total_mixed += c_mixed
        print(f"[{split}] WSSV={c_wssv}, YHV={c_yhv}, mixed={c_mixed}")

    print("-" * 60)
    print("DONE")
    print(f"Total WSSV : {total_wssv}")
    print(f"Total YHV  : {total_yhv}")
    print(f"Total mixed: {total_mixed}")


if __name__ == "__main__":
    main()