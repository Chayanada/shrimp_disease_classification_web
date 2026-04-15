# from pathlib import Path

# DATASET_DIR = Path(r"C:\Users\Chayanada\Desktop\shrimp_project\datasets\stage2_classify\sources\dv7\train")

# total_all = 0

# for cls_name in ["Healthy", "WSSV", "YHD"]:
#     print(f"\n=== {cls_name} ===")

#     cls_path = DATASET_DIR / cls_name

#     count = len(list(cls_path.glob("*.*")))
#     print(f"Total {cls_name}: {count}")

#     total_all += count

# print(f"\nTOTAL DATASET: {total_all}")


# from pathlib import Path

# DATASET_DIR = Path(r"C:\Users\Chayanada\Desktop\shrimp_project\datasets\stage2_classify\raw")

# total_all = 0

# for cls_name in ["healthy", "WSSV", "YHV"]:
#     cls_path = DATASET_DIR / cls_name

#     count = len([f for f in cls_path.iterdir() if f.suffix.lower() in [".jpg", ".jpeg", ".png"]])

#     print(f"{cls_name}: {count}")
#     total_all += count

# print(f"\nTOTAL DATASET: {total_all}")




from pathlib import Path
from collections import Counter

DATASET_DIR = Path(r"C:\Users\Chayanada\Desktop\shrimp_project\datasets\stage2_classify\sources\dv3")

# map class id → ชื่อโรค (ต้องตรงกับ dataset)
class_names = {
    0: "AHPND",
    1: "BGD",
    2: "BSD",
    3: "IMNV",
    4: "TSV",
    5: "WFD",
    6: "WSSV",
    7: "YHD"
}
counter = Counter()

for split in ["train", "valid", "test"]:
    label_path = DATASET_DIR / split / "labels"

    for txt_file in label_path.glob("*.txt"):
        with open(txt_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue
            class_id = int(line.split()[0])
            counter[class_id] += 1

print("=== Class counts ===")
for class_id, count in sorted(counter.items()):
    print(f"{class_names.get(class_id, class_id)}: {count}")

print(f"\nTotal objects: {sum(counter.values())}")