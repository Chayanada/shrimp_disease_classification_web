from pathlib import Path

DATASET_ROOT = Path(r"C:\Users\Chayanada\Desktop\shrimp_project\datasets\stage1_detect\sources\v4")
splits = ["train", "valid", "test"]

def is_seg_line(parts):
    # seg: cls + (x,y)*N  -> token > 5 และหลัง cls เป็นจำนวนคู่
    return len(parts) > 5 and (len(parts) - 1) % 2 == 0

def seg_to_bbox(parts):
    coords = list(map(float, parts[1:]))  # after cls
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

            # ถ้าเป็น bbox อยู่แล้ว -> ไม่แตะ
            if len(parts) == 5:
                out_lines.append(line.strip())
                continue

            # แก้เฉพาะ seg เท่านั้น
            if is_seg_line(parts):
                cls = parts[0]
                x_c, y_c, w, h = seg_to_bbox(parts)
                out_lines.append(f"{cls} {x_c:.6f} {y_c:.6f} {w:.6f} {h:.6f}")
                continue

            # format แปลก -> ไม่แตะ
            out_lines.append(line.strip())

        p.write_text("\n".join(out_lines) + ("\n" if out_lines else ""), encoding="utf-8")

print("DONE: converted seg-only -> bbox in", DATASET_ROOT)