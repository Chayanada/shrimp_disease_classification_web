# 2

from pathlib import Path
import json
import copy
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, WeightedRandomSampler
from sklearn.utils.class_weight import compute_class_weight
from torchvision import datasets, transforms

import timm

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
)

# =========================
# CONFIG
# =========================
DATA_DIR = Path(r"C:\Users\Chayanada\Desktop\shrimp_project\datasets\stage2_classify\final")
RUNS_DIR = Path(r"C:\Users\Chayanada\Desktop\shrimp_project\runs\classify")

MODEL_NAME = "deit_tiny_patch16_224"   # เปลี่ยนได้
IMG_SIZE = 224
BATCH_SIZE = 8
EPOCHS = 100
LR = 1e-4
SEED = 42
NUM_WORKERS = 2
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# baseline / other pretrained models ที่อยากลอง
# "resnet18"
# "mobilenetv3_large_100"
# "efficientnet_b0"
# "convnext_tiny"
# "deit_tiny_patch16_224"

# =========================
# UTILS
# =========================
def seed_everything(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def build_model(model_name: str, num_classes: int):
    model = timm.create_model(model_name, pretrained=True, num_classes=num_classes)
    return model

def evaluate_model(model, loader, device, class_names):
    model.eval()
    y_true = []
    y_pred = []
    y_prob = []

    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            probs = torch.softmax(outputs, dim=1)
            preds = outputs.argmax(dim=1)

            y_true.extend(labels.cpu().numpy().tolist())
            y_pred.extend(preds.cpu().numpy().tolist())
            y_prob.extend(probs.cpu().numpy().tolist())

    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_macro": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "precision_weighted": float(precision_score(y_true, y_pred, average="weighted", zero_division=0)),
        "recall_weighted": float(recall_score(y_true, y_pred, average="weighted", zero_division=0)),
        "f1_weighted": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
    }

    report_dict = classification_report(
        y_true, y_pred, target_names=class_names, output_dict=True, zero_division=0
    )
    report_text = classification_report(
        y_true, y_pred, target_names=class_names, digits=4, zero_division=0
    )
    cm = confusion_matrix(y_true, y_pred)

    return metrics, report_dict, report_text, cm, y_true, y_pred, y_prob

def plot_history(df: pd.DataFrame, save_dir: Path, model_name: str):
    plt.figure(figsize=(8, 5))
    plt.plot(df["epoch"], df["train_loss"], label="train_loss")
    plt.plot(df["epoch"], df["val_loss"], label="val_loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_dir / f"{model_name}_loss_curve.png", dpi=200)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(df["epoch"], df["train_acc"], label="train_acc")
    plt.plot(df["epoch"], df["val_acc"], label="val_acc")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_dir / f"{model_name}_acc_curve.png", dpi=200)
    plt.close()

def save_confusion_matrix(cm, class_names, save_dir: Path, model_name: str):
    cm_csv_path = save_dir / f"{model_name}_confusion_matrix.csv"
    pd.DataFrame(cm, index=class_names, columns=class_names).to_csv(cm_csv_path, encoding="utf-8")

    fig, ax = plt.subplots(figsize=(6, 6))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
    disp.plot(cmap="Blues", xticks_rotation=45, ax=ax, colorbar=False)
    plt.tight_layout()
    plt.savefig(save_dir / f"{model_name}_confusion_matrix.png", dpi=200, bbox_inches="tight")
    plt.close()

# =========================
# MAIN
# =========================
def main():
    seed_everything(SEED)

    save_dir = RUNS_DIR / MODEL_NAME
    ensure_dir(save_dir)

    # transforms
    train_tfms = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    # evaluate
    eval_tfms = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    # dataset
    train_ds = datasets.ImageFolder(DATA_DIR / "train", transform=train_tfms)
    val_ds = datasets.ImageFolder(DATA_DIR / "val", transform=eval_tfms)
    test_ds = datasets.ImageFolder(DATA_DIR / "test", transform=eval_tfms)

    class_names = train_ds.classes
    num_classes = len(class_names)

    # =========================
    # 🔥 OVERSAMPLING (สำคัญ)
    # =========================
    labels = train_ds.targets

    class_counts = np.bincount(labels)
    class_weights = 1. / class_counts
    sample_weights = [class_weights[label] for label in labels]

    sampler = WeightedRandomSampler(sample_weights, len(sample_weights), replacement=True)

    train_loader = DataLoader(
        train_ds,
        batch_size=BATCH_SIZE,
        sampler=sampler,   # 🔥 ใช้ sampler
        num_workers=NUM_WORKERS
    )

    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False)
    test_loader = DataLoader(test_ds, batch_size=BATCH_SIZE, shuffle=False)

    # =========================
    # MODEL
    # =========================
    model = build_model(MODEL_NAME, num_classes).to(DEVICE)

    # =========================
    # 🔥 CLASS WEIGHT (สำคัญ)
    # =========================
    class_weights = compute_class_weight(
        class_weight='balanced',
        classes=np.unique(labels),
        y=labels
    )

    class_weights = torch.tensor(class_weights, dtype=torch.float).to(DEVICE)

    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)

    best_val_acc = 0.0
    best_state = None
    history_rows = []

    # =========================
    # TRAIN LOOP
    # =========================
    for epoch in range(EPOCHS):
        # train
        model.train()
        train_loss_sum = 0.0
        train_correct = 0
        train_total = 0

        for images, labels in train_loader:
            images = images.to(DEVICE)
            labels = labels.to(DEVICE)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            train_loss_sum += loss.item() * images.size(0)
            preds = outputs.argmax(dim=1)
            train_correct += (preds == labels).sum().item()
            train_total += labels.size(0)

        train_loss = train_loss_sum / train_total
        train_acc = train_correct / train_total

        # val
        model.eval()
        val_loss_sum = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(DEVICE)
                labels = labels.to(DEVICE)

                outputs = model(images)
                loss = criterion(outputs, labels)

                val_loss_sum += loss.item() * images.size(0)
                preds = outputs.argmax(dim=1)
                val_correct += (preds == labels).sum().item()
                val_total += labels.size(0)

        val_loss = val_loss_sum / val_total
        val_acc = val_correct / val_total

        history_rows.append({
            "epoch": epoch + 1,
            "train_loss": float(train_loss),
            "train_acc": float(train_acc),
            "val_loss": float(val_loss),
            "val_acc": float(val_acc),
        })

        print(
            f"Epoch {epoch+1}/{EPOCHS} | "
            f"train_loss={train_loss:.4f} train_acc={train_acc:.4f} | "
            f"val_loss={val_loss:.4f} val_acc={val_acc:.4f}"
        )

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_state = copy.deepcopy(model.state_dict())
            torch.save(best_state, save_dir / f"{MODEL_NAME}_best.pth")

    # save meta
    meta = {
        "model_name": MODEL_NAME,
        "img_size": IMG_SIZE,
        "best_val_acc": best_val_acc,
        "class_names": class_names,
        "batch_size": BATCH_SIZE,
        "epochs": EPOCHS,
        "lr": LR,
        "seed": SEED,
    }
    with open(save_dir / f"{MODEL_NAME}_best_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    # =========================
    # SAVE HISTORY
    # =========================
    history_df = pd.DataFrame(history_rows)
    history_df.to_csv(save_dir / f"{MODEL_NAME}_history.csv", index=False)
    plot_history(history_df, save_dir, MODEL_NAME)

    # =========================
    # TEST EVAL
    # =========================
    model.load_state_dict(torch.load(save_dir / f"{MODEL_NAME}_best.pth", map_location=DEVICE))
    metrics, report_dict, report_text, cm, y_true, y_pred, y_prob = evaluate_model(
        model, test_loader, DEVICE, class_names
    )

    with open(save_dir / f"{MODEL_NAME}_test_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    with open(save_dir / f"{MODEL_NAME}_classification_report.txt", "w", encoding="utf-8") as f:
        f.write(report_text)

    with open(save_dir / f"{MODEL_NAME}_classification_report.json", "w", encoding="utf-8") as f:
        json.dump(report_dict, f, indent=2, ensure_ascii=False)

    save_confusion_matrix(cm, class_names, save_dir, MODEL_NAME)

    print("\nTest metrics:")
    print(json.dumps(metrics, indent=2, ensure_ascii=False))
    print(f"\nSaved everything to: {save_dir}")

if __name__ == "__main__":
    main()