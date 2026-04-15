# from pathlib import Path
# import shutil
# import random

# random.seed(42)  # เพื่อให้สุ่มซ้ำได้ผลเดิม

# SRC_ROOT = Path(r"C:\Users\Chayanada\Desktop\shrimp_project\datasets\stage1_detect\merged")
# OUT_ROOT = Path(r"C:\Users\Chayanada\Desktop\shrimp_project\datasets\stage1_detect\subset_8k")

# SPLITS = ["train", "valid", "test"]
# IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# # กำหนดจำนวนที่อยากได้ในแต่ละ split
# TARGETS = {
#     "train": 5600,
#     "valid": 1600,
#     "test": 800,
# }

# def ensure(p: Path):
#     p.mkdir(parents=True, exist_ok=True)

# def collect_pairs(split: str):
#     img_dir = SRC_ROOT / split / "images"
#     lbl_dir = SRC_ROOT / split / "labels"

#     pairs = []
#     for img in img_dir.iterdir():
#         if not img.is_file():
#             continue
#         if img.suffix.lower() not in IMG_EXTS:
#             continue

#         lbl = lbl_dir / f"{img.stem}.txt"
#         if lbl.exists():
#             pairs.append((img, lbl))

#     return pairs

# def copy_pairs(pairs, split: str):
#     dst_img_dir = OUT_ROOT / split / "images"
#     dst_lbl_dir = OUT_ROOT / split / "labels"
#     ensure(dst_img_dir)
#     ensure(dst_lbl_dir)

#     for img, lbl in pairs:
#         shutil.copy2(img, dst_img_dir / img.name)
#         shutil.copy2(lbl, dst_lbl_dir / lbl.name)

# total_copied = 0

# for split in SPLITS:
#     pairs = collect_pairs(split)
#     n_available = len(pairs)
#     n_target = TARGETS[split]

#     if n_target > n_available:
#         print(f"[WARN] {split}: requested {n_target}, but only {n_available} available")
#         n_target = n_available

#     sampled = random.sample(pairs, n_target)
#     copy_pairs(sampled, split)

#     print(f"{split}: copied {len(sampled)} / {n_available}")
#     total_copied += len(sampled)

# # สร้าง data.yaml
# data_yaml = OUT_ROOT / "data.yaml"
# data_yaml.write_text(
#     "train: ../subset_8k/train/images\n"
#     "val: ../subset_8k/valid/images\n"
#     "test: ../subset_8k/test/images\n\n"
#     "nc: 1\n"
#     "names: ['shrimp']\n",
#     encoding="utf-8"
# )

# print(f"\nDONE -> {OUT_ROOT}")
# print("Total copied:", total_copied)


from pathlib import Path
import shutil
import random
from collections import defaultdict

random.seed(42)  # เพื่อให้สุ่มซ้ำได้ผลเดิม

SRC_ROOT = Path(r"C:\Users\Chayanada\Desktop\shrimp_project\datasets\stage1_detect\merged")
OUT_ROOT = Path(r"C:\Users\Chayanada\Desktop\shrimp_project\datasets\stage1_detect\subset_8k")

SPLITS = ["train", "valid", "test"]
IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# กำหนดจำนวนที่อยากได้ในแต่ละ split
TARGETS = {
    "train": 5600,
    "valid": 1600,
    "test": 800,
}

def ensure(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def collect_pairs(split: str):
    img_dir = SRC_ROOT / split / "images"
    lbl_dir = SRC_ROOT / split / "labels"

    pairs = []
    for img in img_dir.iterdir():
        if not img.is_file():
            continue
        if img.suffix.lower() not in IMG_EXTS:
            continue

        lbl = lbl_dir / f"{img.stem}.txt"
        if lbl.exists():
            pairs.append((img, lbl))

    return pairs

def copy_pairs(pairs, split: str):
    dst_img_dir = OUT_ROOT / split / "images"
    dst_lbl_dir = OUT_ROOT / split / "labels"
    ensure(dst_img_dir)
    ensure(dst_lbl_dir)

    for img, lbl in pairs:
        shutil.copy2(img, dst_img_dir / img.name)
        shutil.copy2(lbl, dst_lbl_dir / lbl.name)

def summarize_by_source(pairs):
    counter = defaultdict(int)
    for img, _ in pairs:
        if "__" in img.name:
            source = img.name.split("__", 1)[0]
        else:
            source = "unknown"
        counter[source] += 1
    return dict(sorted(counter.items()))

# ลบโฟลเดอร์เดิมก่อน ป้องกันไฟล์ค้าง
if OUT_ROOT.exists():
    shutil.rmtree(OUT_ROOT)

total_copied = 0

for split in SPLITS:
    pairs = collect_pairs(split)
    n_available = len(pairs)
    n_target = TARGETS[split]

    if n_target > n_available:
        print(f"[WARN] {split}: requested {n_target}, but only {n_available} available")
        n_target = n_available

    sampled = random.sample(pairs, n_target)
    copy_pairs(sampled, split)

    summary = summarize_by_source(sampled)

    print(f"\n[{split}] total available: {n_available}")
    print(f"{split}: copied {len(sampled)}")
    print(f"{split}: sampled by source -> {summary}")

    total_copied += len(sampled)

# สร้าง data.yaml
data_yaml = OUT_ROOT / "data.yaml"
data_yaml.write_text(
    "train: ../subset_8k/train/images\n"
    "val: ../subset_8k/valid/images\n"
    "test: ../subset_8k/test/images\n\n"
    "nc: 1\n"
    "names: ['shrimp']\n",
    encoding="utf-8"
)

print(f"\nDONE -> {OUT_ROOT}")
print("Total copied:", total_copied)