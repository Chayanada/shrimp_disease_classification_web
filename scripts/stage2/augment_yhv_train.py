from pathlib import Path
import cv2
import numpy as np

# =========================
# CONFIG
# =========================
INPUT_DIR = Path("datasets/stage2_classify/raw_cropped/YHV")
OUTPUT_DIR = Path("datasets/stage2_classify/raw_cropped/augment_YHV")

VALID_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# =========================
# AUGMENT FUNCTIONS
# =========================
def flip_horizontal(img):
    return cv2.flip(img, 1)

def rotate_image(img, angle):
    h, w = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(
        img, M, (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT_101
    )

def change_brightness_contrast(img, alpha=1.0, beta=0):
    # alpha = contrast, beta = brightness
    return cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

def add_gaussian_blur(img, ksize=3):
    return cv2.GaussianBlur(img, (ksize, ksize), 0)

def add_gaussian_noise(img, sigma=8):
    noise = np.random.normal(0, sigma, img.shape).astype(np.float32)
    out = img.astype(np.float32) + noise
    return np.clip(out, 0, 255).astype(np.uint8)

def shift_image(img, shift_x=0.05, shift_y=0.05):
    h, w = img.shape[:2]
    tx = int(w * shift_x)
    ty = int(h * shift_y)
    M = np.float32([[1, 0, tx], [0, 1, ty]])
    return cv2.warpAffine(
        img, M, (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT_101
    )

# =========================
# MAIN
# =========================
def main():
    images = [
        p for p in INPUT_DIR.iterdir()
        if p.is_file()
        and p.suffix.lower() in VALID_EXTS
        and "_aug" not in p.stem
    ]

    print(f"Found {len(images)} original YHV images")

    total_created = 0

    for img_path in images:
        img = cv2.imread(str(img_path))

        if img is None:
            print(f"[WARN] Cannot read: {img_path.name}")
            continue

        # สร้างหลายแบบต่อ 1 รูป
        aug_list = [
            ("aug_flip", flip_horizontal(img)),
            ("aug_rot_p10", rotate_image(img, 10)),
            ("aug_rot_m10", rotate_image(img, -10)),
            ("aug_bright", change_brightness_contrast(img, alpha=1.0, beta=18)),
            # ("aug_dark", change_brightness_contrast(img, alpha=1.0, beta=-18)),
            ("aug_contrast", change_brightness_contrast(img, alpha=2.12, beta=0)),
            ("aug_blur", add_gaussian_blur(img, 3)),
            ("aug_noise", add_gaussian_noise(img, sigma=8)),
            ("aug_shift", shift_image(img, shift_x=0.1, shift_y=0.1)),
        ]

        for aug_name, aug_img in aug_list:
            out_name = f"{img_path.stem}_{aug_name}.jpg"
            out_path = OUTPUT_DIR / out_name

            ok = cv2.imwrite(str(out_path), aug_img)
            if ok:
                total_created += 1
            else:
                print(f"[WARN] Cannot save: {out_name}")

    print(f"Done. Created {total_created} augmented images.")


if __name__ == "__main__":
    main()