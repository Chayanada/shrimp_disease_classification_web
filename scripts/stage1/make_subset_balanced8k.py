from pathlib import Path
import shutil
import random
from collections import defaultdict

random.seed(42)

SRC_ROOT = Path(r"C:\Users\Chayanada\Desktop\shrimp_project\datasets\stage1_detect\merged")
OUT_ROOT = Path(r"C:\Users\Chayanada\Desktop\shrimp_project\datasets\stage1_detect\subset_8k_balanced")

SPLITS = ["train", "valid", "test"]
IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

TARGETS = {
    "train": 5600,
    "valid": 1600,
    "test": 800,
}

def ensure(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def collect_pairs_by_source(split: str):
    img_dir = SRC_ROOT / split / "images"
    lbl_dir = SRC_ROOT / split / "labels"

    groups = defaultdict(list)

    for img in img_dir.iterdir():
        if not img.is_file():
            continue
        if img.suffix.lower() not in IMG_EXTS:
            continue

        lbl = lbl_dir / f"{img.stem}.txt"
        if not lbl.exists():
            continue

        # ชื่อไฟล์จาก merged เช่น v3__abc.jpg
        # source prefix = v3
        if "__" in img.name:
            source = img.name.split("__", 1)[0]
        else:
            source = "unknown"

        groups[source].append((img, lbl))

    return groups

def balanced_sample(groups: dict, target: int):
    sources = sorted(groups.keys())
    total_available = sum(len(groups[s]) for s in sources)

    if target > total_available:
        print(f"[WARN] requested {target}, but only {total_available} available")
        target = total_available

    # shuffle ในแต่ละ source ก่อน
    for s in sources:
        random.shuffle(groups[s])

    # รอบแรก: แจกโควตาเท่า ๆ กัน
    n_sources = len(sources)
    base_quota = target // n_sources
    remainder = target % n_sources

    selected = []
    leftovers = []

    for i, s in enumerate(sources):
        quota = base_quota + (1 if i < remainder else 0)
        picked = groups[s][:quota]
        selected.extend(picked)

        # เก็บส่วนที่เหลือไว้กรณี source ไหนมีไม่พอ
        leftovers.extend(groups[s][quota:])

    # ถ้า source บางตัวมีรูปไม่พอ selected อาจยังไม่ถึง target
    if len(selected) < target:
        still_needed = target - len(selected)

        # เอาจริง ๆ บาง source อาจ quota มากเกินจำนวนที่มี
        # จึงต้อง rebuild selected ใหม่แบบปลอดภัย
        selected = []
        leftovers = []

        # pass 1: เลือกได้เท่าที่มี แต่ไม่เกิน quota
        shortage = 0
        temp_leftovers = []

        for i, s in enumerate(sources):
            quota = base_quota + (1 if i < remainder else 0)
            available = groups[s]
            picked_count = min(len(available), quota)
            selected.extend(available[:picked_count])

            if len(available) < quota:
                shortage += quota - len(available)

            temp_leftovers.extend(available[picked_count:])

        # pass 2: เติมจาก source ที่ยังเหลือ
        if shortage > 0:
            random.shuffle(temp_leftovers)
            selected.extend(temp_leftovers[:shortage])

    # กันกรณีเกิน
    if len(selected) > target:
        selected = selected[:target]

    random.shuffle(selected)
    return selected

def copy_pairs(pairs, split: str):
    dst_img_dir = OUT_ROOT / split / "images"
    dst_lbl_dir = OUT_ROOT / split / "labels"
    ensure(dst_img_dir)
    ensure(dst_lbl_dir)

    for img, lbl in pairs:
        shutil.copy2(img, dst_img_dir / img.name)
        shutil.copy2(lbl, dst_lbl_dir / lbl.name)

def summarize_selected(pairs):
    counter = defaultdict(int)
    for img, _ in pairs:
        if "__" in img.name:
            source = img.name.split("__", 1)[0]
        else:
            source = "unknown"
        counter[source] += 1
    return dict(sorted(counter.items()))

# ลบโฟลเดอร์เดิมก่อน เพื่อกันไฟล์ค้าง
if OUT_ROOT.exists():
    shutil.rmtree(OUT_ROOT)

total_copied = 0

for split in SPLITS:
    groups = collect_pairs_by_source(split)
    total_available = sum(len(v) for v in groups.values())
    print(f"\n[{split}] total available: {total_available}")
    print("source counts:", {k: len(v) for k, v in sorted(groups.items())})

    sampled = balanced_sample(groups, TARGETS[split])
    copy_pairs(sampled, split)

    summary = summarize_selected(sampled)
    print(f"{split}: copied {len(sampled)}")
    print(f"{split}: sampled by source -> {summary}")

    total_copied += len(sampled)

# สร้าง data.yaml
data_yaml = OUT_ROOT / "data.yaml"
data_yaml.write_text(
    "train: ../subset_8k_balanced/train/images\n"
    "val: ../subset_8k_balanced/valid/images\n"
    "test: ../subset_8k_balanced/test/images\n\n"
    "nc: 1\n"
    "names: ['shrimp']\n",
    encoding="utf-8"
)

print(f"\nDONE -> {OUT_ROOT}")
print("Total copied:", total_copied)