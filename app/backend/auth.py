import sqlite3
from pydantic import BaseModel
from fastapi import HTTPException

# โครงสร้างรับข้อมูล
class UserSchema(BaseModel):
    username: str
    password: str

# ฟังก์ชันเชื่อมต่อฐานข้อมูล
def get_db():
    conn = sqlite3.connect("shrimp.db")
    conn.row_factory = sqlite3.Row
    return conn

# สร้างตารางเมื่อเริ่มโปรแกรมครั้งแรก
def init_db():
    conn = get_db()
    conn.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)")
    conn.commit()
    conn.close()

init_db() # สั่งสร้างฐานข้อมูลทันที

def register_logic(user: UserSchema):
    conn = get_db()
    try:
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user.username, user.password))
        conn.commit()
        return {"status": "success", "message": "สมัครสมาชิกเรียบร้อย"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="ชื่อนี้มีคนใช้แล้ว")
    finally:
        conn.close()

def login_logic(user: UserSchema):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (user.username, user.password)).fetchone()
    conn.close()
    if row:
        return {"status": "success", "username": row["username"]}
    raise HTTPException(status_code=400, detail="ชื่อผู้ใช้หรือรหัสผ่านผิด")