import './style.css';
import { renderDashboard as displayDashboard, renderDashboard } from './pages/dashboard.js';
import { renderRealtime as displayRealtime } from './pages/realtime.js'; 
import { renderClassification as displayClassification } from './pages/classification.js'; 

const API_BASE = "http://127.0.0.1:8000";

// Selectors
const app = document.querySelector("#app");
const authContainer = document.querySelector("#auth-container");
const mainLayout = document.querySelector("#main-layout");
const sidebarContainer = document.querySelector("#sidebar-container");

// --- 1. การจัดการ Authentication (Login/Register) ---

function renderLogin() {
    // ซ่อน Layout หลัก และแสดงหน้า Auth
    mainLayout.style.display = "none";
    authContainer.style.display = "flex";
    
    authContainer.innerHTML = `
        <div class="wrap">
            <div class="card">
                <h1>KungKamKram Export</h1>
                <input id="u" type="text" placeholder="Username" />
                <input id="p" type="password" placeholder="Password" />
                <button id="loginBtn">Login</button>
                <span class="link-btn" id="goReg">สมัครสมาชิก</span>
            </div>
        </div>
    `;
    document.getElementById("loginBtn").onclick = () => handleAuth("/login");
    document.getElementById("goReg").onclick = renderRegister;
}

function renderRegister() {
    authContainer.innerHTML = `
        <div class="wrap">
            <div class="card">
                <h1>Register</h1>
                <input id="u" type="text" placeholder="Username" />
                <input id="p" type="password" placeholder="Password" />
                <button id="regBtn" class="secondary">Register</button>
                <span class="link-btn" id="goLogin">กลับไปหน้า Login</span>
            </div>
        </div>
    `;
    document.getElementById("regBtn").onclick = () => handleAuth("/register");
    document.getElementById("goLogin").onclick = renderLogin;
}

async function handleAuth(path) {
    const user = document.getElementById("u").value;
    const pass = document.getElementById("p").value;
    const res = await fetch(`${API_BASE}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: user, password: pass })
    });
    const data = await res.json();
    if (res.ok) {
        if (path === "/login") {
            // เมื่อ Login สำเร็จ: ซ่อน Auth -> แสดง Layout หลัก -> สร้าง Sidebar -> ไปหน้า Classification
            authContainer.style.display = "none";
            mainLayout.style.display = "flex";
            renderSidebar(data.username);
            setTimeout(() => {
                window.renderDashboard(); 
            }, 50);
        } else {
            renderLogin();
        }
    } else alert(data.detail);
}

function updateActiveMenu(activeId) {
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
    });
    const activeItem = document.getElementById(activeId);
    if (activeItem) activeItem.classList.add('active');
}

// --- 2. การจัดการ Sidebar และ Layout หลัก ---

function renderSidebar(username) {
    sidebarContainer.innerHTML = `
        <aside class="sidebar">

            <!-- Logo -->
            <div class="logo-section" style="margin-bottom:30px;">
                <div class="logo-row">
                    <div class="logo-badge">🦐</div>
                    <div>
                        <div style="font-family:var(--font-display); font-weight:700; font-size:1rem; color:#fff;">KungKamKram</div>
                        <div class="logo-sub">Export System</div>
                    </div>
                </div>
            </div>

            <!-- Main Menu -->
            <nav class="menu" style="flex:1;">
                <div class="menu-label">Main</div>
                <div class="menu-item active" id="menu-dashboard" onclick="renderDashboard()">
                    <i class="fas fa-th-large"></i> Dashboard
                </div>
                <div class="menu-item" id="menu-class" onclick="renderClassification('${username}')">
                    <i class="fas fa-file-image"></i> Disease Classification
                </div>
                <div class="menu-item" id="menu-realtime" onclick="renderRealtime()">
                    <i class="fas fa-video"></i> Realtime Detection
                </div>
                <div class="menu-item" id="menu-library" onclick="renderLibrary()">
                    <i class="fas fa-book"></i> Library
                </div>
                <div class="menu-item" id="menu-admin" onclick="renderAdmin()">
                    <i class="fas fa-user-shield"></i> Admin Managing
                </div>
                <div class="menu-label" style="margin-top:8px;">System</div>
                <div class="menu-item" id="menu-settings" onclick="renderSettings()">
                    <i class="fas fa-cog"></i> Settings
                </div>
            </nav>

            <!-- User Card + Logout -->
            <div class="user-card" style="margin-top:20px;">
                <img class="user-avatar"
                     src="https://ui-avatars.com/api/?name=${username}&background=1a8077&color=fff&rounded=true">
                <div style="flex:1;">
                    <p class="u-name">${username}</p>
                    <p class="u-role">@Owner</p>
                </div>
                <button onclick="renderLogin()"
                        title="ออกจากระบบ"
                        style="background:rgba(255,107,107,.15);border:none;color:var(--accent-coral);
                               width:32px;height:32px;border-radius:8px;cursor:pointer;
                               display:flex;align-items:center;justify-content:center;
                               transition:all .2s;flex-shrink:0;margin:0;padding:0;width:32px;"
                        onmouseover="this.style.background='var(--accent-coral)';this.style.color='#fff';"
                        onmouseout="this.style.background='rgba(255,107,107,.15)';this.style.color='var(--accent-coral)';">
                    <i class="fas fa-sign-out-alt" style="font-size:.9rem;"></i>
                </button>
            </div>
        </aside>
    `;
}

// --- 3. หน้าต่างๆ ของระบบ (Pages) ---

window.renderDashboard = () => {
    const app = document.getElementById('app');
    displayDashboard(app); // เรียกใช้ฟังก์ชันจากไฟล์แยก
    updateActiveMenu('menu-dashboard');
};

// window.renderClassification = (username) => {
//     app.innerHTML = `
//         <div class="page-body">
//             <h1>Disease Classification</h1>
//             <div class="card" style="max-width: 500px;">
//                 <input id="fileInput" type="file" accept="image/*" />
//                 <button id="detBtn">Detect Now</button>
//                 <div id="result" style="margin-top:20px;"></div>
//             </div>
//         </div>
//     `;

//     document.getElementById("detBtn").onclick = async () => {
//         const file = document.getElementById("fileInput").files[0];
//         if (!file) return alert("เลือกรูปก่อนครับ");

//         const fd = new FormData();
//         fd.append("file", file);
//         fd.append("username", username);

//         const res = await fetch(`${API_BASE}/upload_detection`, { method: "POST", body: fd });
//         const json = await res.json();
        
//         if (json.status === "success") {
//             document.getElementById("result").innerHTML = `
//                 <hr style="margin: 20px 0; border: 0; border-top: 1px solid #eee;"/>
//                 <h3 style="color: #1e3a8a;">ผลตรวจ: ${json.data.disease_name}</h3>
//                 <p>ความแม่นยำ: ${json.data.confidence}</p>
//                 <img src="${json.data.image_url}" style="width:100%; border-radius:10px; margin-top: 10px;" />
//             `;
//         }
//     };
//     updateActiveMenu('menu-class')
// };

window.renderClassification = (username) => {
    const app = document.getElementById('app');
    
    displayClassification(app, username);
    
    updateActiveMenu('menu-class');
};

window.renderRealtime = () => {
    const app = document.getElementById('app');
    displayRealtime(app); // เรียกใช้ฟังก์ชันจากไฟล์แยก
    updateActiveMenu('menu-realtime');
};

// window.renderLibrary = () => {
//     app.innerHTML = `
//         <div class="page-body">
//             <h1>Library</h1>
//             <div class="card"><p>คลังข้อมูลโรคกุ้ง...</p></div>
//         </div>
//     `;
//     updateActiveMenu('menu-library'); // เรียกใช้เพื่อให้เมนู Realtime เป็นสีฟ้า
// };

// window.renderAdmin = () => {
//     app.innerHTML = `
//         <div class="page-body">
//             <h1>Admin Managing</h1>
//             <div class="card"><p>ส่วนจัดการผู้ใช้งาน...</p></div>
//         </div>
//     `;
//     updateActiveMenu('menu-admin'); // เรียกใช้เพื่อให้เมนู Realtime เป็นสีฟ้า
// };

// window.renderSupport = () => {
//     app.innerHTML = `
//         <div class="page-body">
//             <h1>Support</h1>
//             <div class="card">
//                 <p>หากมีปัญหาการใช้งาน ติดต่อเราได้ที่เบอร์ 0XX-XXX-XXXX</p>
//             </div>
//         </div>
//     `;
//     // สมมติว่าใน Sidebar คุณตั้ง id ของเมนู Support ไว้ว่า 'menu-support'
//     updateActiveMenu('menu-support'); 
// };

// window.renderSettings = () => {
//     app.innerHTML = `
//         <div class="page-body">
//             <h1>Settings</h1>
//             <div class="card">
//                 <p>จัดการข้อมูลส่วนตัวและตั้งค่าระบบได้ที่นี่</p>
//             </div>
//         </div>
//     `;
//     // สมมติว่าใน Sidebar คุณตั้ง id ของเมนู Settings ไว้ว่า 'menu-settings'
//     updateActiveMenu('menu-settings');
// };

// เริ่มต้นแอปที่หน้า Login
renderLogin();