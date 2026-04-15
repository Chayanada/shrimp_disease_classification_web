# from pathlib import Path
# import cv2
# import numpy as np
# import random

# # =========================
# # CONFIG
# # =========================
# INPUT_DIR = Path("datasets/stage2_classify/final/train/yhv")
# OUTPUT_DIR = Path("datasets/stage2_classify/final/train/aug_yhv")

# VALID_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# AUG_PER_IMAGE = 3   # 🔥 ปรับได้ (3 = ดีสำหรับเริ่ม)

# SEED = 42
# random.seed(SEED)

# # =========================
# # AUGMENT FUNCTIONS (เบา ๆ)
# # =========================
# def flip(img):
#     return cv2.flip(img, 1)

# def rotate(img):
#     angle = random.uniform(-8, 8)
#     h, w = img.shape[:2]
#     M = cv2.getRotationMatrix2D((w//2, h//2), angle, 1)
#     return cv2.warpAffine(
#         img, M, (w, h),
#         flags=cv2.INTER_LINEAR,
#         borderMode=cv2.BORDER_REFLECT_101
#     )

# def brightness_contrast(img):
#     alpha = random.uniform(0.9, 1.15)   # contrast
#     beta = random.randint(-12, 12)      # brightness
#     return cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

# def blur(img):
#     return cv2.GaussianBlur(img, (3, 3), 0)

# def noise(img):
#     sigma = random.uniform(3, 7)
#     n = np.random.normal(0, sigma, img.shape).astype(np.float32)
#     out = img.astype(np.float32) + n
#     return np.clip(out, 0, 255).astype(np.uint8)

# def shift(img):
#     h, w = img.shape[:2]
#     tx = int(w * random.uniform(-0.04, 0.04))
#     ty = int(h * random.uniform(-0.04, 0.04))
#     M = np.float32([[1, 0, tx], [0, 1, ty]])
#     return cv2.warpAffine(
#         img, M, (w, h),
#         borderMode=cv2.BORDER_REFLECT_101
#     )

# # =========================
# # RANDOM AUGMENT PIPELINE
# # =========================
# def random_augment(img):
#     out = img.copy()

#     if random.random() < 0.5:
#         out = flip(out)

#     if random.random() < 0.7:
#         out = rotate(out)

#     if random.random() < 0.7:
#         out = brightness_contrast(out)

#     if random.random() < 0.3:
#         out = blur(out)

#     if random.random() < 0.3:
#         out = noise(out)

#     if random.random() < 0.3:
#         out = shift(out)

#     return out

# # =========================
# # MAIN
# # =========================
# def main():
#     OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

#     images = [
#         p for p in INPUT_DIR.iterdir()
#         if p.suffix.lower() in VALID_EXTS
#     ]

#     print(f"Found {len(images)} images")

#     total = 0

#     for img_path in images:
#         img = cv2.imread(str(img_path))
#         if img is None:
#             print(f"[WARN] skip {img_path.name}")
#             continue

#         for i in range(AUG_PER_IMAGE):
#             aug = random_augment(img)

#             out_name = f"{img_path.stem}_aug{i+1}.jpg"
#             out_path = OUTPUT_DIR / out_name

#             cv2.imwrite(str(out_path), aug)
#             total += 1

#     print(f"✅ Done! Created {total} augmented images.")

# # =========================
# if __name__ == "__main__":
#     main()


from pathlib import Path
import cv2
import numpy as np
import random

# =========================
# CONFIG
# =========================
INPUT_DIR = Path("datasets/stage2_classify/final/train/yhv")
OUTPUT_DIR = Path("datasets/stage2_classify/final/train/aug_yhv")

VALID_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

AUG_PER_IMAGE = 3   # 21 original -> 63 aug
SEED = 42

random.seed(SEED)
np.random.seed(SEED)

# =========================
# AUGMENT FUNCTIONS
# =========================
def flip(img):
    return cv2.flip(img, 1)

def rotate(img):
    angle = random.uniform(-10, 10)
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    return cv2.warpAffine(
        img,
        M,
        (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT_101
    )

def brightness_contrast(img):
    alpha = random.uniform(0.88, 1.18)   # contrast
    beta = random.randint(-15, 15)       # brightness
    return cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

def blur(img):
    return cv2.GaussianBlur(img, (3, 3), 0)

def noise(img):
    sigma = random.uniform(3, 7)
    n = np.random.normal(0, sigma, img.shape).astype(np.float32)
    out = img.astype(np.float32) + n
    return np.clip(out, 0, 255).astype(np.uint8)

def shift(img):
    h, w = img.shape[:2]
    tx = int(w * random.uniform(-0.06, 0.06))
    ty = int(h * random.uniform(-0.06, 0.06))
    M = np.float32([[1, 0, tx], [0, 1, ty]])
    return cv2.warpAffine(
        img,
        M,
        (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT_101
    )

# =========================
# RANDOM AUGMENT PIPELINE
# =========================
def random_augment(img):
    out = img.copy()

    candidates = []

    if random.random() < 0.7:
        candidates.append("flip")
    if random.random() < 0.8:
        candidates.append("rotate")
    if random.random() < 0.9:
        candidates.append("brightness_contrast")
    if random.random() < 0.35:
        candidates.append("blur")
    if random.random() < 0.35:
        candidates.append("noise")
    if random.random() < 0.35:
        candidates.append("shift")

    # บังคับให้มีอย่างน้อย 2 operations
    if len(candidates) < 2:
        fallback_ops = ["flip", "rotate", "brightness_contrast", "shift"]
        while len(candidates) < 2:
            op = random.choice(fallback_ops)
            if op not in candidates:
                candidates.append(op)

    random.shuffle(candidates)

    for op in candidates:
        if op == "flip":
            out = flip(out)
        elif op == "rotate":
            out = rotate(out)
        elif op == "brightness_contrast":
            out = brightness_contrast(out)
        elif op == "blur":
            out = blur(out)
        elif op == "noise":
            out = noise(out)
        elif op == "shift":
            out = shift(out)

    return out

# =========================
# MAIN
# =========================
def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    images = [
        p for p in INPUT_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in VALID_EXTS
    ]

    print(f"Found {len(images)} images in {INPUT_DIR}")

    total_created = 0

    for img_path in images:
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"[WARN] Cannot read: {img_path.name}")
            continue

        for i in range(AUG_PER_IMAGE):
            aug_img = random_augment(img)

            out_name = f"aug{i+1}_{img_path.stem}.jpg"
            out_path = OUTPUT_DIR / out_name

            ok = cv2.imwrite(str(out_path), aug_img)
            if ok:
                total_created += 1
            else:
                print(f"[WARN] Cannot save: {out_name}")

    print(f"✅ Done. Created {total_created} augmented images in {OUTPUT_DIR}")

if __name__ == "__main__":
    main()