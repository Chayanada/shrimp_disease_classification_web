from pathlib import Path

# ====== แก้ 2 ค่านี้ทุกครั้งก่อนรัน ======
DATASET_ROOT = Path(r"C:\Users\Chayanada\Desktop\shrimp_project\datasets\stage1_detect\sources\v2")  # <-- เปลี่ยน v2 เป็น v ที่คุณกำลังทำ
SHRIMP_OLD_ID = 1  # <-- ตำแหน่งของ shrimp ใน names:[...] เช่น ['pakan','shrimp'] => shrimp=1
# =======================================

splits = ["train", "valid", "test"]

def is_seg_line(parts):
    # seg: cls + (x,y)*N  -> token > 5 และหลัง cls เป็นจำนวนคู่
    return len(parts) > 5 and (len(parts) - 1) % 2 == 0

def seg_to_bbox(parts):
    # parts: [cls, x1, y1, x2, y2, ...] normalized 0-1
    coords = list(map(float, parts[1:]))
    xs = coords[0::2]
    ys = coords[1::2]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    x_c = (xmin + xmax) / 2
    y_c = (ymin + ymax) / 2
    w = xmax - xmin
    h = ymax - ymin
    return x_c, y_c, w, h

for split in splits:
    label_dir = DATASET_ROOT / split / "labels"
    if not label_dir.exists():
        continue

    for p in label_dir.glob("*.txt"):
        out_lines = []

        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            parts = line.split()

            # bbox format: 5 ค่า
            if len(parts) == 5:
                cls = int(parts[0])
                if cls == SHRIMP_OLD_ID:
                    parts[0] = "0"  # remap shrimp -> 0
                    out_lines.append(" ".join(parts))
                continue  # ไม่ใช่ shrimp ทิ้ง

            # seg polygon -> bbox
            if is_seg_line(parts):
                cls = int(parts[0])
                if cls == SHRIMP_OLD_ID:
                    x_c, y_c, w, h = seg_to_bbox(parts)
                    out_lines.append(f"0 {x_c:.6f} {y_c:.6f} {w:.6f} {h:.6f}")
                continue  # ไม่ใช่ shrimp ทิ้ง

        p.write_text("\n".join(out_lines) + ("\n" if out_lines else ""), encoding="utf-8")

# แก้ data.yaml ให้เหลือ 1 class
data_yaml = DATASET_ROOT / "data.yaml"
if data_yaml.exists():
    lines = data_yaml.read_text(encoding="utf-8").splitlines()
    out = []
    for line in lines:
        if line.strip().startswith("nc:"):
            out.append("nc: 1")
        elif line.strip().startswith("names:"):
            out.append("names: ['shrimp']")
        else:
            out.append(line)
    data_yaml.write_text("\n".join(out) + "\n", encoding="utf-8")

print("DONE:", DATASET_ROOT)
print(" - kept only shrimp")
print(" - remapped shrimp -> class 0")
print(" - converted seg polygons to bbox (5 numbers/line)")