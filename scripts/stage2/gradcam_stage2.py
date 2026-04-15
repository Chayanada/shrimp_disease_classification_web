from pathlib import Path
import json
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

import torch
from torchvision import transforms
import timm

from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
from pytorch_grad_cam.utils.image import show_cam_on_image

MODEL_DIR = Path(r"C:\Users\Chayanada\Desktop\shrimp_project\runs\classify\efficientnet_b0")
MODEL_NAME = "efficientnet_b0"
IMAGE_PATH = Path(r"C:\Users\Chayanada\Desktop\shrimp_project\test2.jpg")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

with open(MODEL_DIR / f"{MODEL_NAME}_best_meta.json", "r", encoding="utf-8") as f:
    meta = json.load(f)

class_names = meta["class_names"]
img_size = meta["img_size"]

model = timm.create_model(MODEL_NAME, pretrained=False, num_classes=len(class_names))
model.load_state_dict(torch.load(MODEL_DIR / f"{MODEL_NAME}_best.pth", map_location=DEVICE))
model.to(DEVICE)
model.eval()

# target layer ต้องปรับตามโมเดล
# target_layers = [model.stages[-1].blocks[-1].norm1]
target_layers = [model.conv_head]

transform = transforms.Compose([
    transforms.Resize((img_size, img_size)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

img_pil = Image.open(IMAGE_PATH).convert("RGB")
img_resized = img_pil.resize((img_size, img_size))
img_np = np.array(img_resized).astype(np.float32) / 255.0

input_tensor = transform(img_pil).unsqueeze(0).to(DEVICE)

with torch.no_grad():
    outputs = model(input_tensor)
    pred_idx = outputs.argmax(dim=1).item()

targets = [ClassifierOutputTarget(pred_idx)]

cam = GradCAM(model=model, target_layers=target_layers)
grayscale_cam = cam(input_tensor=input_tensor, targets=targets)[0]

cam_image = show_cam_on_image(img_np, grayscale_cam, use_rgb=True)

plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.imshow(img_np)
plt.title("Original")
plt.axis("off")

plt.subplot(1, 2, 2)
plt.imshow(cam_image)
plt.title(f"Grad-CAM: {class_names[pred_idx]}")
plt.axis("off")

plt.tight_layout()
out_path = MODEL_DIR / f"{MODEL_NAME}_gradcam.png"
plt.savefig(out_path, dpi=200)
plt.show()

print("Saved:", out_path)