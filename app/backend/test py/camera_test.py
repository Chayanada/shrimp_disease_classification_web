import cv2
import numpy as np

def sigmoid(x, k=10):
    return 1 / (1 + np.exp(-k * x))

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

alpha = 0.5  # 0 = เห็น enhanced ล้วน, 1 = เห็น original ล้วน

cv2.namedWindow("Overlay", cv2.WINDOW_NORMAL)

while True:
    # 1) อ่านภาพจากกล้อง
    ret, frame = cap.read()
    if not ret:
        break

    # 2) แปลงเป็น grayscale เพื่อทำ edge
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 3) ลด noise ก่อนหา edge
    blur = cv2.GaussianBlur(gray, (3, 3), 0)

    # 4) Laplacian หา edge
    lap = cv2.Laplacian(blur, cv2.CV_64F)
    lap = cv2.normalize(lap, None, -1, 1, cv2.NORM_MINMAX)

    # 5) Sigmoid non-linear mapping เพื่อคุมความแรง edge
    edge = sigmoid(lap, k=8)
    edge = (edge * 255).astype(np.uint8)

    # 6) ทำ edge เป็น 3 channel แล้ว blend กลับเข้าภาพสี
    edge_colored = cv2.cvtColor(edge, cv2.COLOR_GRAY2BGR)
    enhanced = cv2.addWeighted(frame, 1.0, edge_colored, 0.2, 0)

    # 7) ✅ ทับกันพอดี (Overlay) ในหน้าต่างเดียว
    overlay = cv2.addWeighted(frame, alpha, enhanced, 1 - alpha, 0)

    cv2.imshow("Overlay", overlay)

    # กด q เพื่อออก / กด + หรือ - เพื่อปรับการทับ
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    elif key == ord("+") or key == ord("="):
        alpha = min(1.0, alpha + 0.05)   # เห็น original มากขึ้น
    elif key == ord("-") or key == ord("_"):
        alpha = max(0.0, alpha - 0.05)   # เห็น enhanced มากขึ้น

cap.release()
cv2.destroyAllWindows()