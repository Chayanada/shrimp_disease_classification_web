from pathlib import Path
import json
import pandas as pd

RUNS_DIR = Path(r"C:\Users\Chayanada\Desktop\shrimp_project\runs\detect")

rows = []

for model_dir in RUNS_DIR.iterdir():
    if not model_dir.is_dir():
        continue

    metrics_files = list(model_dir.glob("*_test_metrics.json"))
    meta_files = list(model_dir.glob("*_best_meta.json"))

    if not metrics_files or not meta_files:
        continue

    with open(metrics_files[0], "r", encoding="utf-8") as f:
        metrics = json.load(f)

    with open(meta_files[0], "r", encoding="utf-8") as f:
        meta = json.load(f)

    rows.append({
        "model_name": meta["model_name"],
        "img_size": meta["img_size"],
        "best_val_acc": meta["best_val_acc"],
        "test_accuracy": metrics["accuracy"],
        "precision_macro": metrics["precision_macro"],
        "recall_macro": metrics["recall_macro"],
        "f1_macro": metrics["f1_macro"],
        "precision_weighted": metrics["precision_weighted"],
        "recall_weighted": metrics["recall_weighted"],
        "f1_weighted": metrics["f1_weighted"],
    })

df = pd.DataFrame(rows).sort_values(by="f1_macro", ascending=False)
out_path = RUNS_DIR / "compare_models.csv"
df.to_csv(out_path, index=False, encoding="utf-8")
print(df)
print(f"\nSaved to: {out_path}")