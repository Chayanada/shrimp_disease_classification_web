# from fastapi import FastAPI, File, UploadFile, Form
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles

# # --- Import ส่วนที่เราแยกไว้ (สำคัญมาก) ---
# from auth import UserSchema, register_logic, login_logic
# import detector

# app = FastAPI()

# from fastapi.staticfiles import StaticFiles

# app.mount("/static", StaticFiles(directory="static"), name="static")

# # --- ตั้งค่า CORS ให้ Frontend คุยกับ Backend ได้ ---
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # --- เชื่อมต่อ Folder สำหรับเก็บรูปภาพ ---
# app.mount("/static", StaticFiles(directory="static"), name="static")

# # --- 1. เส้นทางสำหรับการสมัครสมาชิก (Register) ---
# @app.post("/register")
# async def register(user: UserSchema):
#     # เรียกใช้ฟังก์ชันจาก auth.py เพื่อบันทึกลง SQLite
#     return register_logic(user)

# # --- 2. เส้นทางสำหรับการเข้าสู่ระบบ (Login) ---
# @app.post("/login")
# async def login(user: UserSchema):
#     # เรียกใช้ฟังก์ชันจาก auth.py เพื่อตรวจสอบใน SQLite
#     return login_logic(user)

# # --- 3. เส้นทางสำหรับการตรวจโรคกุ้ง (Detection) ---
# @app.post("/upload_detection")
# async def upload_detection(
#     username: str = Form(...), # รับชื่อ user มาจากหน้าเว็บ
#     file: UploadFile = File(...)
# ):
#     # อ่านข้อมูลไฟล์ที่ส่งมา
#     content = await file.read()
    
#     # ส่งไปให้ detector.py จัดการ (Resize เป็น 224 และบันทึกข้อมูล)
#     result = detector.process_detection(username, content)
    
#     return {"status": "success", "data": result}

# # --- 4. ดูประวัติการตรวจทั้งหมด ---
# @app.get("/history")
# def get_history():
#     return detector.db_logs

# @app.get("/")
# def read_root():
#     return {"message": "KungKamKram Export API is running"}

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# --- Import ส่วนที่เราแยกไว้ ---
from auth import UserSchema, register_logic, login_logic
from realtime import get_video_stream
import detector

app = FastAPI()

# --- เชื่อมต่อ Folder สำหรับเก็บรูปภาพ (สำคัญ: ต้องมีบรรทัดนี้เว็บถึงจะดึงรูปไปโชว์ได้) ---
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- ตั้งค่า CORS ให้ Frontend คุยกับ Backend ได้ ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. เส้นทางสำหรับการสมัครสมาชิก (Register) ---
@app.post("/register")
async def register(user: UserSchema):
    return register_logic(user)

# --- 2. เส้นทางสำหรับการเข้าสู่ระบบ (Login) ---
@app.post("/login")
async def login(user: UserSchema):
    return login_logic(user)

# --- 3. เส้นทางสำหรับการตรวจโรคกุ้ง (Detection) ---
@app.post("/upload_detection")
async def upload_detection(
    username: str = Form(...),
    file: UploadFile = File(...)
):
    content = await file.read()
    
    # ส่งไปให้ detector.py จัดการ 
    result = detector.process_detection(username, content)
    
    # *** คืนค่า result ไปตรงๆ เลย จะได้ไม่ซ้อนกัน 2 ชั้น ***
    return result

# --- 4. ดูประวัติการตรวจทั้งหมด ---
@app.get("/history")
def get_history():
    return {"message": "รอทำ API สำหรับดึงประวัติภายหลัง"}

@app.get("/")
def read_root():
    return {"message": "KungKamKram Export API is running"}


# ส่วนที่ 2: เพิ่ม Route นี้ไว้ก่อนบรรทัดสุดท้ายของไฟล์
# @app.get("/video_feed/{camera_id}")
# async def video_feed(camera_id: str):
#     return get_video_stream(camera_id)