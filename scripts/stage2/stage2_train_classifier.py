# from pathlib import Path
# import random
# import json
# import numpy as np
# import torch
# import torch.nn as nn
# import torch.nn.functional as F
# import timm
# from torch.utils.data import DataLoader, WeightedRandomSampler
# from torchvision import datasets, transforms, models
# from sklearn.metrics import classification_report, confusion_matrix
# from open_clip import create_model_from_pretrained
# from torchvision import datasets, transforms, models


# # =========================
# # CONFIG
# # =========================
# DATA_DIR = Path("datasets/stage2_classify/final")
# SAVE_DIR = Path("runs/classify")
# SAVE_DIR.mkdir(parents=True, exist_ok=True)

# MODEL_NAME = "deit_tiny_patch16_224"   # เปลี่ยนได้: resnet18, efficientnet_b0, mobilenet_v3_small, densenet121
# IMG_SIZE = 224
# BATCH_SIZE = 4
# EPOCHS = 30
# LR = 1e-4
# NUM_WORKERS = 0   # สำคัญมากบน Windows
# SEED = 42

# DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# # =========================
# # SEED
# # =========================
# def set_seed(seed=42):
#     random.seed(seed)
#     np.random.seed(seed)
#     torch.manual_seed(seed)
#     torch.cuda.manual_seed_all(seed)

#     torch.backends.cudnn.deterministic = True
#     torch.backends.cudnn.benchmark = False
    
# # =========================
# # MODEL FACTORY
# # =========================
# def build_model(model_name: str, num_classes: int):
#     model_name = model_name.lower()

#     if model_name == "resnet18":
#         model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
#         model.fc = nn.Linear(model.fc.in_features, num_classes)

#     elif model_name == "efficientnet_b0":
#         model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.DEFAULT)
#         model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)

#     elif model_name == "mobilenet_v3_small":
#         model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.DEFAULT)
#         model.classifier[3] = nn.Linear(model.classifier[3].in_features, num_classes)

#     elif model_name == "densenet121":
#         model = models.densenet121(weights=models.DenseNet121_Weights.DEFAULT)
#         model.classifier = nn.Linear(model.classifier.in_features, num_classes)
   
#     elif model_name == "vit_b_16":
#         model = models.vit_b_16(weights=models.ViT_B_16_Weights.DEFAULT)
#         model.heads.head = nn.Linear(model.heads.head.in_features, num_classes)

#     elif model_name == "mobilenet_v3_large":
#         model = models.mobilenet_v3_large(weights=models.MobileNet_V3_Large_Weights.DEFAULT)
#         model.classifier[3] = nn.Linear(model.classifier[3].in_features, num_classes)

#     elif model_name == "convnext_tiny":
#         model = models.convnext_tiny(weights=models.ConvNeXt_Tiny_Weights.DEFAULT)
#         model.classifier[2] = nn.Linear(model.classifier[2].in_features, num_classes)

#     elif model_name == "deit_tiny_patch16_224":
#         model = timm.create_model(
#             "deit_tiny_patch16_224",
#             pretrained=True,
#             num_classes=num_classes
#         )

#     else:
#         raise ValueError(f"Unsupported model: {model_name}")

#     return model

# # =========================
# # TRAIN / EVAL FUNCTION
# # =========================
# def run_epoch(model, loader, criterion, device, optimizer=None):
#     is_train = optimizer is not None
#     model.train() if is_train else model.eval()

#     total_loss = 0.0
#     correct = 0
#     total = 0

#     all_preds = []
#     all_labels = []

#     with torch.set_grad_enabled(is_train):
#         for images, labels in loader:
#             images = images.to(device, non_blocking=True)
#             labels = labels.to(device, non_blocking=True)

#             outputs = model(images)
#             loss = criterion(outputs, labels)

#             if is_train:
#                 optimizer.zero_grad()
#                 loss.backward()
#                 optimizer.step()

#             total_loss += loss.item() * images.size(0)
#             preds = outputs.argmax(dim=1)

#             correct += (preds == labels).sum().item()
#             total += labels.size(0)

#             all_preds.extend(preds.detach().cpu().numpy().tolist())
#             all_labels.extend(labels.detach().cpu().numpy().tolist())

#     avg_loss = total_loss / total if total > 0 else 0.0
#     acc = correct / total if total > 0 else 0.0

#     return avg_loss, acc, all_labels, all_preds

# def main():
#     set_seed(SEED)

#     imagenet_mean = [0.485, 0.456, 0.406]
#     imagenet_std = [0.229, 0.224, 0.225]

#     train_tf = transforms.Compose([
#         transforms.Resize((IMG_SIZE, IMG_SIZE)),
#         transforms.RandomHorizontalFlip(p=0.5),
#         transforms.ToTensor(),
#         transforms.Normalize(mean=imagenet_mean, std=imagenet_std),
#     ])

#     eval_tf = transforms.Compose([
#         transforms.Resize((IMG_SIZE, IMG_SIZE)),
#         transforms.ToTensor(),
#         transforms.Normalize(mean=imagenet_mean, std=imagenet_std),
#     ])

#     train_ds = datasets.ImageFolder(DATA_DIR / "train", transform=train_tf)
#     val_ds = datasets.ImageFolder(DATA_DIR / "val", transform=eval_tf)
#     test_ds = datasets.ImageFolder(DATA_DIR / "test", transform=eval_tf)

#     class_names = train_ds.classes
#     num_classes = len(class_names)

#     print("Classes:", class_names)
#     print("Train size:", len(train_ds))
#     print("Val size:", len(val_ds))
#     print("Test size:", len(test_ds))

#     targets = [label for _, label in train_ds.samples]
#     class_counts = np.bincount(targets, minlength=num_classes)
#     print("Train class counts:", dict(zip(class_names, class_counts.tolist())))

#     class_weights_np = 1.0 / class_counts
#     class_weights_np = class_weights_np / class_weights_np.sum() * num_classes
#     class_weights = torch.tensor(class_weights_np, dtype=torch.float32).to(DEVICE)

#     sample_weights = [class_weights_np[label] for label in targets]
#     sampler = WeightedRandomSampler(
#         weights=sample_weights,
#         num_samples=len(sample_weights),
#         replacement=True
#     )

#     train_loader = DataLoader(
#         train_ds,
#         batch_size=BATCH_SIZE,
#         sampler=sampler,
#         num_workers=NUM_WORKERS,
#         pin_memory=True
#     )

#     val_loader = DataLoader(
#         val_ds,
#         batch_size=BATCH_SIZE,
#         shuffle=False,
#         num_workers=NUM_WORKERS,
#         pin_memory=True
#     )

#     test_loader = DataLoader(
#         test_ds,
#         batch_size=BATCH_SIZE,
#         shuffle=False,
#         num_workers=NUM_WORKERS,
#         pin_memory=True
#     )

#     model = build_model(MODEL_NAME, num_classes).to(DEVICE)

#     criterion = nn.CrossEntropyLoss(weight=class_weights)
#     optimizer = torch.optim.Adam(model.parameters(), lr=LR)

#     save_path = SAVE_DIR / f"{MODEL_NAME}_best.pth"
#     meta_path = SAVE_DIR / f"{MODEL_NAME}_best_meta.json"

#     best_val_acc = -1.0

#     for epoch in range(1, EPOCHS + 1):
#         train_loss, train_acc, _, _ = run_epoch(model, train_loader, criterion, DEVICE, optimizer)
#         val_loss, val_acc, _, _ = run_epoch(model, val_loader, criterion, DEVICE, optimizer=None)

#         print(
#             f"Epoch {epoch:02d}/{EPOCHS} | "
#             f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f} | "
#             f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}"
#         )

#         if val_acc > best_val_acc:
#             best_val_acc = val_acc

#             torch.save({
#                 "model_name": MODEL_NAME,
#                 "img_size": IMG_SIZE,
#                 "class_names": class_names,
#                 "model_state_dict": model.state_dict(),
#             }, save_path)

#             with open(meta_path, "w", encoding="utf-8") as f:
#                 json.dump({
#                     "model_name": MODEL_NAME,
#                     "img_size": IMG_SIZE,
#                     "best_val_acc": best_val_acc,
#                     "class_names": class_names,
#                     "batch_size": BATCH_SIZE,
#                     "epochs": EPOCHS,
#                     "lr": LR,
#                     "seed": SEED,
#                 }, f, ensure_ascii=False, indent=2)

#             print(f"  -> Saved best model to: {save_path}")

#     print(f"\nBest Val Acc: {best_val_acc:.4f}")

#     checkpoint = torch.load(save_path, map_location=DEVICE)
#     model.load_state_dict(checkpoint["model_state_dict"])
#     model.eval()

#     test_loss, test_acc, test_labels, test_preds = run_epoch(model, test_loader, criterion, DEVICE, optimizer=None)

#     print(f"\nTest Loss: {test_loss:.4f}")
#     print(f"Test Acc : {test_acc:.4f}")

#     print(f"\nModel : {MODEL_NAME} Classification Report:")
#     print(classification_report(
#         test_labels,
#         test_preds,
#         target_names=class_names,
#         digits=4,
#         zero_division=0
#     ))

#     print(f"{MODEL_NAME} Confusion Matrix:")
#     print(confusion_matrix(test_labels, test_preds))

# if __name__ == "__main__":
#     main()