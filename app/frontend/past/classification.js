// // สมมติว่ามีตัวแปร API_BASE ส่งมาด้วย หรือกำหนดตรงนี้
// const API_BASE = "http://127.0.0.1:8000";

// export function renderClassification(app, username) {
//     app.innerHTML = `
//         <div class="dashboard-wrapper" style="padding: 30px; width: 100%; text-align: left; box-sizing: border-box; display: block;">
            
//             <div style="margin-bottom: 30px;">
//                 <h1 style="margin: 0; font-size: 1.8rem; color: #1e293b;">Disease Classification</h1>
//                 <p style="margin: 5px 0 0 0; color: #64748b; font-size: 0.95rem;">อัปโหลดรูปภาพกุ้งเพื่อวิเคราะห์โรคด้วย AI</p>
//             </div>

//             <div style="display: grid; grid-template-columns: 1fr; gap: 20px; max-width: 1000px;">
                
//                 <div style="background: white; padding: 30px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px dashed #cbd5e1; text-align: center;" id="upload-section">
//                     <i class="fas fa-cloud-upload-alt" style="font-size: 3rem; color: #3b82f6; margin-bottom: 15px;"></i>
//                     <h3 style="margin: 0 0 10px 0; color: #1e293b;">เลือกรูปภาพกุ้งที่คุณต้องการตรวจสอบ</h3>
                    
//                     <input id="fileInput" type="file" accept="image/*" style="display: none;" />
//                     <button id="browseBtn" style="background: white; color: #3b82f6; border: 1px solid #3b82f6; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-size: 1rem; font-weight: 600; margin-bottom: 15px; transition: 0.2s;">
//                         เปิดดูไฟล์ (Browse)
//                     </button>
//                     <p id="fileNameDisplay" style="color: #64748b; font-size: 0.85rem; margin: 0;"></p>
                    
//                     <button id="detBtn" style="background: #10b981; color: white; border: none; padding: 12px 30px; border-radius: 8px; cursor: pointer; font-size: 1rem; font-weight: 600; display: none; margin: 20px auto 0 auto; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); transition: 0.2s;">
//                         <i class="fas fa-search"></i> เริ่มวิเคราะห์ (Detect Now)
//                     </button>
//                 </div>

//                 <div id="loading-section" style="display: none; text-align: center; padding: 40px; background: white; border-radius: 12px; border: 1px solid #e2e8f0;">
//                     <i class="fas fa-spinner fa-spin" style="font-size: 3rem; color: #3b82f6; margin-bottom: 15px;"></i>
//                     <h3 style="color: #1e293b; margin: 0;">AI กำลังประมวลผลและวาด Bounding Box...</h3>
//                     <p style="color: #64748b; font-size: 0.9rem;">อาจใช้เวลาสักครู่ ระบบกำลังบันทึกข้อมูลลงฐานข้อมูล</p>
//                 </div>

//                 <div id="result-section" style="display: none; background: white; padding: 25px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
//                     <h2 style="margin: 0 0 20px 0; color: #1e293b; border-bottom: 1px solid #e2e8f0; padding-bottom: 15px;">ผลการวิเคราะห์ (Analysis Result)</h2>
                    
//                     <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 25px;" id="stats-container">
//                         </div>

//                     <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
//                         <div>
//                             <h4 style="color: #64748b; text-align: center; margin-bottom: 10px;">ภาพต้นฉบับ (Original)</h4>
//                             <div style="border-radius: 8px; overflow: hidden; border: 1px solid #e2e8f0; background: #f8fafc; display: flex; align-items: center; justify-content: center; min-height: 250px;">
//                                 <img id="original-img" src="" style="width: 100%; display: block;" />
//                             </div>
//                         </div>
//                         <div>
//                             <h4 style="color: #3b82f6; text-align: center; margin-bottom: 10px;">ตรวจพบ (Detected)</h4>
//                             <div style="border-radius: 8px; overflow: hidden; border: 1px solid #e2e8f0; background: #f8fafc; display: flex; align-items: center; justify-content: center; min-height: 250px;">
//                                 <img id="detected-img" src="" style="width: 100%; display: block;" />
//                             </div>
//                         </div>
//                     </div>
//                 </div>

//             </div>
//         </div>
//     `;

//     // --- Logic การทำงาน ---
//     const fileInput = document.getElementById("fileInput");
//     const browseBtn = document.getElementById("browseBtn");
//     const detBtn = document.getElementById("detBtn");
//     const fileNameDisplay = document.getElementById("fileNameDisplay");
//     const originalImg = document.getElementById("original-img");
    
//     // คลิกปุ่ม Browse ให้ไปทริกเกอร์ file input
//     browseBtn.onclick = () => fileInput.click();

//     // เมื่อเลือกรูปภาพ ให้โชว์ชื่อไฟล์, แสดงปุ่ม Detect และแสดงรูป Preview ทันที
//     fileInput.onchange = (e) => {
//         const file = e.target.files[0];
//         if (file) {
//             fileNameDisplay.innerText = `ไฟล์ที่เลือก: ${file.name}`;
//             detBtn.style.display = "flex"; // โชว์ปุ่ม
            
//             // สร้าง URL จำลองเพื่อให้ผู้ใช้เห็นรูปภาพก่อนเลยโดยไม่ต้องรออัปโหลด
//             const objectUrl = URL.createObjectURL(file);
//             originalImg.src = objectUrl;
            
//             // รีเซ็ตหน้าผลลัพธ์
//             document.getElementById("result-section").style.display = "none";
//         }
//     };

//     // เมื่อกดปุ่ม Detect
//     detBtn.onclick = async () => {
//         const file = fileInput.files[0];
//         if (!file) return alert("กรุณาเลือกรูปภาพก่อนครับ");

//         // โชว์ Loading และซ่อนส่วนอัปโหลด/ปุ่ม
//         document.getElementById("upload-section").style.display = "none";
//         document.getElementById("loading-section").style.display = "block";

//         const fd = new FormData();
//         fd.append("file", file);
//         fd.append("username", username);

//         try {
//             const res = await fetch(`${API_BASE}/upload_detection`, { method: "POST", body: fd });
//             const json = await res.json();
            
//             if (json.status === "success") {
//                 // ซ่อน Loading, โชว์ Result
//                 document.getElementById("loading-section").style.display = "none";
//                 document.getElementById("result-section").style.display = "block";
//                 document.getElementById("upload-section").style.display = "block"; // เอาปุ่มกลับมาเผื่ออัปรูปใหม่
//                 detBtn.style.display = "none"; // ซ่อนปุ่ม detect รอไฟล์ใหม่
//                 fileInput.value = ""; // เคลียร์ไฟล์
//                 fileNameDisplay.innerText = "";

//                 // ตั้งค่ารูปที่มีการวาดกรอบ BBox แล้ว
//                 document.getElementById("detected-img").src = json.data.image_url;

//                 // --- อัปเดตข้อมูลกล่องสรุปตาม Database โครงสร้างใหม่ ---
//                 // สมมติว่า Backend ส่งกลับมาเป็น: { healthy: 10, wssv: 2, yhv: 0, ahpnd: 1 }
//                 const counts = json.data.counts || { healthy: 0, wssv: 0, yhv: 0, others: 0 };
                
//                 document.getElementById("stats-container").innerHTML = `
//                     <div style="background: #ecfdf5; padding: 15px; border-radius: 8px; border: 1px solid #a7f3d0; text-align: center;">
//                         <p style="margin: 0; color: #065f46; font-size: 0.85rem; font-weight: 600;">Healthy (ปกติ)</p>
//                         <h2 style="margin: 5px 0 0 0; color: #047857;">${counts.healthy || 0} ตัว</h2>
//                     </div>
//                     <div style="background: #fef2f2; padding: 15px; border-radius: 8px; border: 1px solid #fecaca; text-align: center;">
//                         <p style="margin: 0; color: #991b1b; font-size: 0.85rem; font-weight: 600;">WSSV</p>
//                         <h2 style="margin: 5px 0 0 0; color: #b91c1c;">${counts.wssv || 0} ตัว</h2>
//                     </div>
//                     <div style="background: #fffbeb; padding: 15px; border-radius: 8px; border: 1px solid #fde68a; text-align: center;">
//                         <p style="margin: 0; color: #92400e; font-size: 0.85rem; font-weight: 600;">YHV</p>
//                         <h2 style="margin: 5px 0 0 0; color: #d97706;">${counts.yhv || 0} ตัว</h2>
//                     </div>
//                     <div style="background: #eff6ff; padding: 15px; border-radius: 8px; border: 1px solid #bfdbfe; text-align: center;">
//                         <p style="margin: 0; color: #1e40af; font-size: 0.85rem; font-weight: 600;">เวลาประมวลผล</p>
//                         <h2 style="margin: 5px 0 0 0; color: #1d4ed8;">${json.data.process_time || '1.2s'}</h2>
//                     </div>
//                 `;
//             } else {
//                 alert("เกิดข้อผิดพลาดจากเซิร์ฟเวอร์: " + (json.message || "Unknown Error"));
//                 resetUI();
//             }
//         } catch (error) {
//             console.error(error);
//             alert("ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้");
//             resetUI();
//         }
//     };

//     function resetUI() {
//         document.getElementById("loading-section").style.display = "none";
//         document.getElementById("upload-section").style.display = "block";
//     }
// }

const API_BASE = "http://127.0.0.1:8000";

export function renderClassification(app, username) {
    app.innerHTML = `
        <div class="dashboard-container" style="
            min-height: 100vh;
            background-color: #f8fafc;
            padding: 20px;
            display: flex;
            justify-content: center;
            font-family: 'Inter', sans-serif;
        ">
            <div class="dashboard-wrapper" style="width: 100%; max-width: 1100px;">
                
                <div style="margin-bottom: 30px; text-align: center;">
                    <h1 style="margin: 0; font-size: 2rem; color: #1e293b; font-weight: 800;">Shrimp Disease Classification</h1>
                    <p style="margin: 8px 0 0 0; color: #64748b; font-size: 1rem;">ระบบวิเคราะห์สุขภาพกุ้งอัจฉริยะ (User: <span style="color: #3b82f6;">${username}</span>)</p>
                </div>

                <div style="display: grid; grid-template-columns: 1fr; gap: 25px;">
                    
                    <div id="upload-section" style="
                        background: white; 
                        padding: 40px 20px; 
                        border-radius: 20px; 
                        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); 
                        border: 2px dashed #cbd5e1; 
                        text-align: center;
                    ">
                        <div style="background: #eff6ff; width: 80px; height: 80px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px auto;">
                            <i class="fas fa-cloud-upload-alt" style="font-size: 2.5rem; color: #3b82f6;"></i>
                        </div>
                        <h3 style="margin: 0 0 10px 0; color: #1e293b;">เลือกรูปภาพกุ้งเพื่อเริ่มตรวจ</h3>
                        <p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 20px;">รองรับไฟล์ JPG, PNG</p>
                        
                        <input id="fileInput" type="file" accept="image/*" style="display: none;" />
                        <button id="browseBtn" style="background: white; color: #3b82f6; border: 1.5px solid #3b82f6; padding: 12px 25px; border-radius: 12px; cursor: pointer; font-size: 1rem; font-weight: 600; transition: 0.2s;">
                            เปิดคลังภาพ (Browse)
                        </button>
                        <p id="fileNameDisplay" style="color: #3b82f6; font-size: 0.9rem; margin: 15px 0 0 0; font-weight: 500;"></p>
                        
                        <button id="detBtn" style="
                            background: #10b981; color: white; border: none; 
                            padding: 15px 40px; border-radius: 12px; cursor: pointer; 
                            font-size: 1.1rem; font-weight: 600; display: none; 
                            margin: 25px auto 0 auto; 
                            box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.4);
                            transition: 0.3s;
                        ">
                            <i class="fas fa-search" style="margin-right: 8px;"></i> เริ่มการวิเคราะห์ทันที
                        </button>
                    </div>

                    <div id="loading-section" style="display: none; text-align: center; padding: 60px 20px; background: white; border-radius: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                        <div class="loader" style="
                            border: 5px solid #f3f3f3;
                            border-top: 5px solid #3b82f6;
                            border-radius: 50%;
                            width: 50px;
                            height: 50px;
                            animation: spin 1s linear infinite;
                            margin: 0 auto 20px auto;
                        "></div>
                        <h3 style="color: #1e293b; margin: 0;">AI กำลังประมวลผล...</h3>
                        <p style="color: #64748b; margin-top: 10px;">กำลังวาด Bounding Box และบันทึกข้อมูล</p>
                    </div>

                    <div id="result-section" style="display: none; background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border: 1px solid #e2e8f0;">
                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 25px; border-bottom: 2px solid #f1f5f9; padding-bottom: 15px;">
                            <h2 style="margin: 0; color: #1e293b; font-size: 1.4rem;">ผลการตรวจสอบ</h2>
                            <span id="result-time" style="color: #64748b; font-size: 0.85rem;"></span>
                        </div>
                        
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-bottom: 30px;" id="stats-container">
                        </div>

                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                            <div style="text-align: center;">
                                <p style="color: #64748b; font-weight: 600; margin-bottom: 10px;">ภาพต้นฉบับ</p>
                                <div style="border-radius: 15px; overflow: hidden; border: 2px solid #f1f5f9; background: #f8fafc;">
                                    <img id="original-img" src="" style="width: 100%; height: auto; display: block;" />
                                </div>
                            </div>
                            <div style="text-align: center;">
                                <p style="color: #3b82f6; font-weight: 600; margin-bottom: 10px;">ผลการตรวจจาก AI</p>
                                <div style="border-radius: 15px; overflow: hidden; border: 2px solid #3b82f6; background: #f8fafc; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);">
                                    <img id="detected-img" src="" style="width: 100%; height: auto; display: block;" />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <style>
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            #browseBtn:hover { background: #eff6ff !important; border-color: #2563eb !important; color: #2563eb !important; }
            #detBtn:hover { transform: translateY(-3px); box-shadow: 0 15px 20px -5px rgba(16, 185, 129, 0.5); }
        </style>
    `;

    // --- Logic การทำงาน (คงเดิมแต่ปรับ UI Interaction เล็กน้อย) ---
    const fileInput = document.getElementById("fileInput");
    const browseBtn = document.getElementById("browseBtn");
    const detBtn = document.getElementById("detBtn");
    const fileNameDisplay = document.getElementById("fileNameDisplay");
    const originalImg = document.getElementById("original-img");
    
    browseBtn.onclick = () => fileInput.click();

    fileInput.onchange = (e) => {
        const file = e.target.files[0];
        if (file) {
            fileNameDisplay.innerText = `✔️ เลือกไฟล์แล้ว: ${file.name}`;
            detBtn.style.display = "block";
            const objectUrl = URL.createObjectURL(file);
            originalImg.src = objectUrl;
            document.getElementById("result-section").style.display = "none";
        }
    };

    detBtn.onclick = async () => {
        const file = fileInput.files[0];
        if (!file) return;

        document.getElementById("upload-section").style.display = "none";
        document.getElementById("loading-section").style.display = "block";

        const fd = new FormData();
        fd.append("file", file);
        fd.append("username", username);

        try {
            const res = await fetch(`${API_BASE}/upload_detection`, { method: "POST", body: fd });
            const json = await res.json();
            
            if (json.status === "success") {
                document.getElementById("loading-section").style.display = "none";
                document.getElementById("result-section").style.display = "block";
                document.getElementById("upload-section").style.display = "block";
                detBtn.style.display = "none";

                document.getElementById("detected-img").src = json.data.image_url;
                
                const counts = json.data.counts || { healthy: 0, wssv: 0, yhv: 0 };
                
                document.getElementById("stats-container").innerHTML = `
                    <div style="background: #f0fdf4; padding: 15px; border-radius: 12px; border: 1px solid #bbf7d0; text-align: center;">
                        <p style="margin: 0; color: #166534; font-size: 0.85rem; font-weight: 600;">Healthy</p>
                        <h2 style="margin: 5px 0 0 0; color: #15803d;">${counts.healthy}</h2>
                    </div>
                    <div style="background: #fef2f2; padding: 15px; border-radius: 12px; border: 1px solid #fecaca; text-align: center;">
                        <p style="margin: 0; color: #991b1b; font-size: 0.85rem; font-weight: 600;">WSSV</p>
                        <h2 style="margin: 5px 0 0 0; color: #b91c1c;">${counts.wssv}</h2>
                    </div>
                    <div style="background: #fffbeb; padding: 15px; border-radius: 12px; border: 1px solid #fde68a; text-align: center;">
                        <p style="margin: 0; color: #92400e; font-size: 0.85rem; font-weight: 600;">YHV</p>
                        <h2 style="margin: 5px 0 0 0; color: #d97706;">${counts.yhv}</h2>
                    </div>
                    <div style="background: #f1f5f9; padding: 15px; border-radius: 12px; border: 1px solid #cbd5e1; text-align: center;">
                        <p style="margin: 0; color: #475569; font-size: 0.85rem; font-weight: 600;">Time</p>
                        <h2 style="margin: 5px 0 0 0; color: #1e293b;">${json.data.process_time || '1.2s'}</h2>
                    </div>
                `;
            } else {
                alert("Error: " + json.message);
                resetUI();
            }
        } catch (error) {
            alert("ไม่สามารถติดต่อเซิร์ฟเวอร์ได้");
            resetUI();
        }
    };

    function resetUI() {
        document.getElementById("loading-section").style.display = "none";
        document.getElementById("upload-section").style.display = "block";
    }
}









