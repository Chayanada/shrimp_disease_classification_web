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
                </div>
            </nav>

            <!-- User Card + Logout -->
            <div class="user-card" style="margin-top:20px;">
                <img class="user-avatar"
                     src="https://ui-avatars.com/api/?name=${username}&background=1a8077&color=fff&rounded=true">
                <div style="flex:1;">
                    <p class="u-name" style="color:rgba(255,255,255,0.6); margin:0;">${username}</p>
                    <p class="u-role" style="color:rgba(255,255,255,0.6); margin:0;">@Owner</p>
                </div>
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

// เริ่มต้นแอปที่หน้า Login
renderLogin();