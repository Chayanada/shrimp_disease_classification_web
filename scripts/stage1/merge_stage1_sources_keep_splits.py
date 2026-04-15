from pathlib import Path
import shutil
from pathlib import Path

SRC_ROOT = Path(r"C:\Users\Chayanada\Desktop\shrimp_project\datasets\stage1_detect\sources")
OUT_ROOT = Path(r"C:\Users\Chayanada\Desktop\shrimp_project\datasets\stage1_detect\merged")

VERSIONS = [f"v{i}" for i in range(1, 11)]
SPLITS = ["train", "valid", "test"]
IMG_EXTS = {".jpg", ".jpeg", ".png"}

def ensure(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def copy_with_prefix(src_img: Path, src_lbl: Path, dst_img_dir: Path, dst_lbl_dir: Path, prefix: str):
    # ต้องมี label คู่กับภาพเท่านั้นถึงจะคัดลอก (กัน dataset เลอะ)
    if not src_lbl.exists():
        return 0

    new_img_name = f"{prefix}__{src_img.name}"
    new_lbl_name = f"{prefix}__{src_lbl.name}"

    shutil.copy2(src_img, dst_img_dir / new_img_name)
    shutil.copy2(src_lbl, dst_lbl_dir / new_lbl_name)
    return 1

# สร้างโฟลเดอร์ปลายทาง
for sp in SPLITS:
    ensure(OUT_ROOT / sp / "images")
    ensure(OUT_ROOT / sp / "labels")

total = 0

for v in VERSIONS:
    vroot = SRC_ROOT / v
    if not vroot.exists():
        print("SKIP (missing):", vroot)
        continue

    for sp in SPLITS:
        img_dir = vroot / sp / "images"
        lbl_dir = vroot / sp / "labels"
        if not img_dir.exists() or not lbl_dir.exists():
            continue

        dst_img_dir = OUT_ROOT / sp / "images"
        dst_lbl_dir = OUT_ROOT / sp / "labels"

        for img in img_dir.iterdir():
            if img.suffix.lower() not in IMG_EXTS:
                continue
            lbl = lbl_dir / (img.stem + ".txt")
            total += copy_with_prefix(img, lbl, dst_img_dir, dst_lbl_dir, prefix=v)

# สร้าง data.yaml สำหรับ merged (shrimp class เดียว)
data_yaml = OUT_ROOT / "data.yaml"
data_yaml.write_text(
    "train: ../merged/train/images\n"
    "val: ../merged/valid/images\n"
    "test: ../merged/test/images\n\n"
    "nc: 1\n"
    "names: ['shrimp']\n",
    encoding="utf-8"
)

print("DONE ->", OUT_ROOT)
print("total paired image+label copied:", total)
print(list(Path(OUT_ROOT).rglob("*.npy")))