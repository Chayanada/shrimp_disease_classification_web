from pathlib import Path
import shutil
import random

# =========================
# CONFIG
# =========================
SRC_DIR = Path("datasets/stage2_classify/raw_cropped")
DST_DIR = Path("datasets/stage2_classify/final")

CLASSES = ["healthy", "wssv", "yhv"]

# สัดส่วน (เหมาะกับเคสคุณ)
TRAIN_RATIO = 0.75
VAL_RATIO = 0.125
TEST_RATIO = 0.125

SEED = 42

# =========================
# MAIN
# =========================
def split_dataset():
    random.seed(SEED)

    for cls in CLASSES:
        src_cls_dir = SRC_DIR / cls
        images = list(src_cls_dir.glob("*.*"))

        # filter เฉพาะรูป
        images = [p for p in images if p.suffix.lower() in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]]

        print(f"\nClass: {cls} → total {len(images)} images")

        random.shuffle(images)

        n = len(images)
        n_train = int(n * TRAIN_RATIO)
        n_val = int(n * VAL_RATIO)
        n_test = n - n_train - n_val

        train_imgs = images[:n_train]
        val_imgs = images[n_train:n_train+n_val]
        test_imgs = images[n_train+n_val:]

        print(f" → train: {len(train_imgs)}, val: {len(val_imgs)}, test: {len(test_imgs)}")

        # copy files
        for split_name, split_imgs in zip(
            ["train", "val", "test"],
            [train_imgs, val_imgs, test_imgs]
        ):
            dst_cls_dir = DST_DIR / split_name / cls
            dst_cls_dir.mkdir(parents=True, exist_ok=True)

            for img_path in split_imgs:
                dst_path = dst_cls_dir / img_path.name
                shutil.copy(img_path, dst_path)

    print("\n✅ Done splitting dataset!")

# =========================
if __name__ == "__main__":
    split_dataset()