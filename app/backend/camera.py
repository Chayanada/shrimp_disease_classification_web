# import sqlite3
# import time
# from datetime import datetime
# # import cv2  (ถ้าคุณใช้ OpenCV เปิดกล้อง ให้เอาคอมเมนต์ออก)
# # from ultralytics import YOLO (ถ้าคุณใช้ YOLO ให้เอาคอมเมนต์ออก)

# # ล็อคเป้า Database ให้ตรงเป๊ะ
# DB_PATH = r"C:\Users\Chayanada\Desktop\shrimp_project\app\backend\shrimp.db"

# # ---------------------------------------------------------
# # ฟังก์ชันสำหรับเซฟข้อมูลลง Database (ที่ถามหา)
# # ---------------------------------------------------------
# def save_log_to_db(camera_id, disease_name, confidence, image_path):
#     try:
#         # 1. เชื่อมต่อ Database
#         conn = sqlite3.connect(DB_PATH)
#         cursor = conn.cursor()
        
#         # 2. กำหนดประเภทการแจ้งเตือน
#         det_type = "danger" if disease_name in ["YHV", "WSSV", "AHPND", "EHP"] else "info"
#         msg = f"ตรวจพบ {disease_name} ความแม่นยำ {int(confidence*100)}%"

#         # 3. สั่งพิมพ์งาน (เตรียมบันทึก)
#         cursor.execute("""
#             INSERT INTO camera_logs (camera_id, detection_type, message, confidence, image_url)
#             VALUES (?, ?, ?, ?, ?)
#         """, (camera_id, det_type, msg, confidence, image_path))

#         # 4. กด SAVE (Ctrl+S) 🎯 ตรงนี้แหละครับที่ถามหา!
#         conn.commit() 
        
#         # 5. ปิดการเชื่อมต่อ
#         conn.close()
#         print(f"✅ บันทึก {disease_name} ลง Database สำเร็จ! รูป: {image_path}")
        
#     except Exception as e:
#         print(f"❌ Error บันทึกข้อมูลไม่สำเร็จ: {e}")

# # ---------------------------------------------------------
# # จำลองการทำงานของกล้องและ AI
# # ---------------------------------------------------------
# def run_camera():
#     print("🎥 เริ่มเปิดกล้องและรัน AI ตรวจจับโรค...")
    
#     # สมมติว่านี่คือลูป while True ของกล้องคุณ
#     while True:
#         # [เอาโค้ด YOLO ตรวจจับ YHV ของคุณมาใส่ตรงนี้]
        
#         # --- (จำลองว่า AI ตรวจเจอ YHV แบบที่คุณบอก) ---
#         ai_detected_disease = "YHV"
#         ai_confidence = 0.88
        
#         # ตอนที่เซฟรูป ให้ตั้งชื่อไฟล์รูป (สมมติว่าคุณเซฟรูปลงโฟลเดอร์ static/detections)
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         saved_image_url = f"http://127.0.0.1:8000/static/detections/snap_{timestamp}.jpg"
        
#         # 🎯 พอ AI จับได้ปุ๊บ เรียกฟังก์ชันเซฟลง Database ทันที!
#         print("🤖 AI เจอโรค! กำลังส่งข้อมูลเข้า Database...")
#         save_log_to_db("CAM-01", ai_detected_disease, ai_confidence, saved_image_url)
        
#         # พัก 5 วินาทีก่อนตรวจใหม่ (อันนี้ผมใส่ไว้กันมันรันรัวๆ เฉยๆ ครับ)
#         time.sleep(5) 
#         break # (ใส่ break ไว้เพื่อให้มันรันรอบเดียวแล้วจบ คุณจะเอาออกก็ได้)

# # เริ่มการทำงาน
# if __name__ == "__main__":
#     run_camera()