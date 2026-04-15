import os
import uuid
import cv2
import numpy as np
import sqlite3
import torch
import time 
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
from datetime import datetime
from ultralytics import YOLO
from collections import OrderedDict

# --- ส่วนโหลดโมเดล (รันตอน Start Server) ---
# Stage 1: YOLO
MODEL_S1_PATH = r"C:\Users\Chayanada\Desktop\shrimp_project\runs\detect\stage1_final\weights\best.pt"
model_stage1 = YOLO(MODEL_S1_PATH)

# Stage 2: EfficientNet-B0
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
S2_PATH = r"C:\Users\Chayanada\Desktop\shrimp_project\runs\classify\efficientnet_b0_best.pth"

def init_stage2():
    model = models.efficientnet_b0(weights=None)
    num_ftrs = model.classifier[1].in_features
    
    model.classifier[1] = nn.Linear(num_ftrs, 3) 
    
    checkpoint = torch.load(S2_PATH, map_location=device)
    state_dict = checkpoint['model_state_dict'] if 'model_state_dict' in checkpoint else checkpoint
    
    new_state_dict = OrderedDict()
    for k, v in state_dict.items():
        name = k[7:] if k.startswith('module.') else k
        new_state_dict[name] = v
        
    model.load_state_dict(new_state_dict)
    model.to(device)
    model.eval()
    
    # ดึงชื่อคลาส (ปรับให้ตรงกับ 3 คลาส)
    classes = checkpoint.get('class_names', ["Healthy", "WSSV", "YHV"])
    return model, classes

model_stage2, class_names = init_stage2()

# เตรียม Transform
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

def process_detection(username, file_content):
    start_time = time.time() # จับเวลาประมวลผล

    # 1. อ่านรูปต้นฉบับ
    nparr = np.frombuffer(file_content, np.uint8)
    img_orig = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    img_plotted = img_orig.copy() 

    # ตั้งค่าตัวแปรนับจำนวนตาม Database
    counts = {"healthy": 0, "wssv": 0, "yhv": 0}
    shrimp_count = 0

    # 2. Stage 1: ค้นหาตำแหน่งกุ้งด้วย YOLO
    results = model_stage1.predict(img_orig, conf=0.25, imgsz=512, verbose=False)
    result = results[0]

    # 3. Stage 2: ตรวจโรคกุ้งทีละตัว และวาดกรอบ
    if result.boxes is not None and len(result.boxes) > 0:
        shrimp_count = len(result.boxes)
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            shrimp_crop = img_orig[max(0,y1):min(img_orig.shape[0],y2), 
                                   max(0,x1):min(img_orig.shape[1],x2)]
            
            if shrimp_crop.size == 0: continue
            
            # เตรียมรูปเข้า Stage 2 (EfficientNet)
            rgb_crop = cv2.cvtColor(shrimp_crop, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_crop)
            input_tensor = preprocess(pil_img).unsqueeze(0).to(device)
            
            with torch.no_grad():
                output = model_stage2(input_tensor)
                _, pred = torch.max(output, 1)
                
            disease_name = class_names[pred.item()]
            disease_key = disease_name.lower() 
            
            # บวกเลขเข้า Counter
            if disease_key in counts:
                counts[disease_key] += 1
            else:
                counts[disease_key] = 1 
                
            # วาด Bounding Box และ Label
            if disease_key == "healthy":
                color = (0, 255, 0) # สีเขียว
            elif disease_key == "wssv":
                color = (0, 0, 255) # สีแดง
            else:
                color = (0, 255, 255) # สีเหลือง (YHV)
                
            cv2.rectangle(img_plotted, (x1, y1), (x2, y2), color, 2)
            
            (tw, th), _ = cv2.getTextSize(disease_name, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
            cv2.rectangle(img_plotted, (x1, y1 - 25), (x1 + tw, y1), color, -1) 
            cv2.putText(img_plotted, disease_name, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    # 4. บันทึกรูปลงโฟลเดอร์
    new_filename = f"{uuid.uuid4()}.jpg"
    os.makedirs("static/detections", exist_ok=True)
    cv2.imwrite(os.path.join("static/detections", new_filename), img_plotted)

    img_url = f"http://127.0.0.1:8000/static/detections/{new_filename}"
    
    # 5. สร้างตาราง และ บันทึกลง Database
    try:
        # ใส่ตัว r ไว้ข้างหน้า เพื่อบอกว่าเป็น Raw String (กันปัญหาเครื่องหมาย \)
        conn = conn = sqlite3.connect("shrimp.db")
        cursor = conn.cursor()
        
        # สร้างตารางก่อน (ถ้ายังไม่มี)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                image_path TEXT,
                healthy_count INTEGER DEFAULT 0,
                wssv_count INTEGER DEFAULT 0,
                yhv_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # นำข้อมูลใส่ลงตาราง
        cursor.execute("""
            INSERT INTO detections (username, image_path, healthy_count, wssv_count, yhv_count)
            VALUES (?, ?, ?, ?, ?)
        """, (username, img_url, counts.get("healthy", 0), counts.get("wssv", 0), counts.get("yhv", 0)))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database Error: {e}")

    process_time = f"{round(time.time() - start_time, 2)} วินาที"

    # 6. ส่งผลลัพธ์กลับไปให้หน้าเว็บ
    return {
        "status": "success",
        "data": {
            "image_url": img_url,
            "counts": counts,
            "process_time": process_time,
            "disease_name": f"ตรวจพบทั้งหมด {shrimp_count} ตัว" 
        }
    }