from pathlib import Path

# ====== แก้ 2 ค่านี้ ======
DATASET_ROOT = Path(r"C:\Users\Chayanada\Desktop\shrimp_project\datasets\stage1_detect\sources\v10")
SHRIMP_OLD_ID = 1  # จาก names: ['feed','shrimp'] => shrimp=1
# ==========================

splits = ["train", "valid", "test"]

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

            # ต้องมีอย่างน้อย cls + 4 ค่า (bbox) หรือ cls + (x,y)*N (seg)
            if len(parts) < 5:
                continue

            try:
                cls = int(float(parts[0]))
            except ValueError:
                continue

            # เก็บเฉพาะ shrimp
            if cls == SHRIMP_OLD_ID:
                parts[0] = "0"  # remap shrimp -> class 0
                out_lines.append(" ".join(parts))
            # ถ้าไม่ใช่ shrimp: ทิ้ง

        p.write_text("\n".join(out_lines) + ("\n" if out_lines else ""), encoding="utf-8")

# แก้ data.yaml ให้เหลือ 1 class (optional แต่แนะนำ)
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
print(" - updated data.yaml to 1 class")