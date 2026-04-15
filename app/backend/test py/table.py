import sqlite3

def setup_realtime_database():
    # ล็อคเป้าไปที่ไฟล์ในโฟลเดอร์ backend ของคุณโดยตรง
    db_path = r"C:\Users\Chayanada\Desktop\shrimp_project\app\backend\shrimp.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. ตาราง camera_nodes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS camera_nodes (
            camera_id TEXT PRIMARY KEY,
            name TEXT,
            ip_address TEXT,
            stream_url TEXT,
            status TEXT,
            last_fps INTEGER,
            current_disease TEXT,
            last_update DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. ตาราง camera_logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS camera_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            camera_id TEXT,
            detection_type TEXT,
            message TEXT,
            confidence REAL,
            image_url TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(camera_id) REFERENCES camera_nodes(camera_id)
        )
    """)

    conn.commit()
    conn.close()
    print("สร้างตารางลงในโฟลเดอร์ backend สำเร็จแล้ว!")

# เรียกใช้ฟังก์ชัน
setup_realtime_database()