from pathlib import Path
import pandas as pd

RUNS_DIR = Path(r"C:\Users\Chayanada\Desktop\shrimp_project\runs\detect")

rows = []

for run_dir in RUNS_DIR.iterdir():
    if not run_dir.is_dir():
        continue

    results_file = run_dir / "results.csv"
    if not results_file.exists():
        continue

    df = pd.read_csv(results_file)

    # เอา row สุดท้าย (epoch สุดท้าย)
    last = df.iloc[-1]

    rows.append({
        "run_name": run_dir.name,
        "mAP50": last.get("metrics/mAP50(B)", None),
        "mAP50-95": last.get("metrics/mAP50-95(B)", None),
        "precision": last.get("metrics/precision(B)", None),
        "recall": last.get("metrics/recall(B)", None),
    })

compare_df = pd.DataFrame(rows).sort_values(by="mAP50-95", ascending=False)

out_path = RUNS_DIR / "compare_detect_models.csv"
compare_df.to_csv(out_path, index=False)

print(compare_df)
print(f"\nSaved to: {out_path}")