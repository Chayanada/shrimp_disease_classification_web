from pathlib import Path
import re

# ====== แก้ตรงนี้ ======
DATASET_ROOT = Path(r"C:\Users\Chayanada\Desktop\shrimp_project\datasets\stage1_detect\sources\v4")
TARGET_NAME = "prawn"   # ชื่อคลาสเดิมที่อยากให้กลายเป็น shrimp
# =======================

splits = ["train", "valid", "test"]

data_yaml = DATASET_ROOT / "data.yaml"
if not data_yaml.exists():
    raise FileNotFoundError(f"data.yaml not found at: {data_yaml}")

text = data_yaml.read_text(encoding="utf-8")

# ดึง names: [...] ออกมา (รองรับทั้ง ' และ ")
m = re.search(r"names\s*:\s*\[(.*?)\]", text)
if not m:
    raise ValueError("หา names: [...] ใน data.yaml ไม่เจอ (รูปแบบไฟล์ไม่ตรง)")

raw = m.group(1)
names = [x.strip().strip("'\"") for x in raw.split(",") if x.strip()]
if not names:
    raise ValueError("names ใน data.yaml ว่าง")

# หา id ของ pawn
target_ids = [i for i, n in enumerate(names) if n.strip().lower() == TARGET_NAME.lower()]
if not target_ids:
    raise ValueError(f"ไม่พบ class '{TARGET_NAME}' ใน names: {names}")

TARGET_ID = target_ids[0]
print("FOUND:", TARGET_NAME, "id =", TARGET_ID, "| names =", names)

# 1) filter labels: เก็บเฉพาะ TARGET_ID แล้ว remap เป็น 0
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
            except:
                continue

            if cls == TARGET_ID:
                parts[0] = "0"  # remap pawn -> 0
                out_lines.append(" ".join(parts))
            # class อื่นทิ้งหมด

        p.write_text("\n".join(out_lines) + ("\n" if out_lines else ""), encoding="utf-8")

# 2) update data.yaml ให้เหลือ 1 class และชื่อเป็น shrimp
out_lines = []
for line in text.splitlines():
    s = line.strip()
    if s.startswith("nc:"):
        out_lines.append("nc: 1")
    elif s.startswith("names:"):
        out_lines.append("names: ['shrimp']")
    else:
        out_lines.append(line)

data_yaml.write_text("\n".join(out_lines) + "\n", encoding="utf-8")

print("DONE:", DATASET_ROOT)
print(" - kept only:", TARGET_NAME, "(remapped to class 0)")
print(" - updated data.yaml => names: ['shrimp'], nc: 1")