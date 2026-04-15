import cv2
from fastapi.responses import StreamingResponse
from ultralytics import YOLO # สมมติว่าใช้ YOLO

# โหลด Model เตรียมไว้
model = r"C:\Users\Chayanada\Desktop\shrimp_project\runs\detect\stage1_final\weights\best.pt" 

def generate_frames(camera_id):
    # camera_id จะรับค่ามาจากหน้าเว็บ เช่น 0, 1 หรือ URL ของกล้อง IP
    cap = cv2.VideoCapture(int(camera_id) if camera_id.isdigit() else camera_id)
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # ตรวจจับด้วย AI
            results = model(frame)
            annotated_frame = results[0].plot() 
            
            # แปลงเป็นไฟล์ภาพส่งออก
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b' \r\n')

# ฟังก์ชันที่จะถูกเรียกใช้จาก main.py
def get_video_stream(camera_id):
    return StreamingResponse(generate_frames(camera_id),
                             media_type="multipart/x-mixed-replace; boundary=frame")
