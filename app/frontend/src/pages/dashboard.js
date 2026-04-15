// import Chart from 'chart.js/auto';

// // ============================================================
// // GET /dashboard_summary
// // คืน: { classification, realtime, recent_classify, recent_realtime }
// // ดึงจาก DB ทุก 10 วินาที
// // ============================================================

// let _dashTimer = null;

// export function renderDashboard(app) {
//     app.innerHTML = `
//         <div class="dashboard-wrapper">

//             <!-- Header -->
//             <div class="page-header">
//                 <div>
//                     <h1>Dashboard Overview</h1>
//                     <p>สรุปภาพรวมการตรวจโรคกุ้งก้ามกราม · อัปเดตทุก 10 วินาที</p>
//                 </div>
//                 <div style="display:flex; gap:10px; align-items:center;">
//                     <span id="dash-updated" style="font-size:.78rem; color:var(--text-muted);"></span>
//                     <button class="btn btn-primary" onclick="fetchAndRender()">
//                         <i class="fas fa-sync-alt"></i> Refresh
//                     </button>
//                 </div>
//             </div>

//             <!-- ══════════════════════════════════
//                  SECTION 1: Classification (Upload)
//                  ══════════════════════════════════ -->
//             <div style="display:flex; align-items:center; gap:10px; margin-bottom:14px;">
//                 <div style="width:4px; height:22px; background:var(--teal-400); border-radius:4px;"></div>
//                 <h2 style="font-family:var(--font-display); font-size:1.05rem; color:var(--teal-800); margin:0;">
//                     <i class="fas fa-file-image" style="color:var(--teal-400); margin-right:6px;"></i>
//                     Disease Classification · อัปโหลดรูปภาพ
//                 </h2>
//             </div>

//             <!-- Stat cards: classification -->
//             <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:20px;">
//                 ${statCard('Total Scans',     'cls-total',    'var(--teal-500)',     'var(--teal-50)',  'fa-images')}
//                 ${statCard('พบโรค',           'cls-infected', 'var(--accent-coral)', '#fff0f0',        'fa-viruses')}
//                 ${statCard('ปกติ (Healthy)',  'cls-healthy',  'var(--accent-lime)',  '#e6faf3',        'fa-check-circle')}
//                 ${statCard('โรคที่พบบ่อย',   'cls-top',      'var(--accent-amber)', '#fff8e6',        'fa-trophy')}
//             </div>

//             <!-- Charts + recent table: classification -->
//             <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:30px;">

//                 <!-- Disease breakdown donut -->
//                 <div class="panel">
//                     <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
//                         <p class="panel-title" style="margin:0;">สัดส่วนโรคที่พบ</p>
//                         <span class="badge badge-info" style="font-size:.72rem;">ทั้งหมด</span>
//                     </div>
//                     <div style="height:200px; display:flex; align-items:center; justify-content:center;">
//                         <canvas id="cls-donut"></canvas>
//                     </div>
//                 </div>

//                 <!-- Recent uploads table -->
//                 <div class="panel">
//                     <p class="panel-title" style="margin-bottom:14px;">
//                         <i class="fas fa-clock" style="color:var(--teal-400);"></i> อัปโหลดล่าสุด
//                     </p>
//                     <div style="overflow-y:auto; max-height:220px;">
//                         <table class="data-table" style="font-size:.82rem;">
//                             <thead><tr>
//                                 <th style="font-size:.7rem;">ผู้ใช้</th>
//                                 <th style="font-size:.7rem;">Healthy</th>
//                                 <th style="font-size:.7rem;">WSSV</th>
//                                 <th style="font-size:.7rem;">YHV</th>
//                                 <th style="font-size:.7rem;">เวลา</th>
//                             </tr></thead>
//                             <tbody id="cls-table">
//                                 <tr><td colspan="5" style="text-align:center;color:var(--text-muted);padding:16px;">กำลังโหลด…</td></tr>
//                             </tbody>
//                         </table>
//                     </div>
//                 </div>
//             </div>

//             <!-- ══════════════════════════════════
//                  SECTION 2: Realtime Detection
//                  ══════════════════════════════════ -->
//             <div style="display:flex; align-items:center; gap:10px; margin-bottom:14px;">
//                 <div style="width:4px; height:22px; background:var(--accent-coral); border-radius:4px;"></div>
//                 <h2 style="font-family:var(--font-display); font-size:1.05rem; color:var(--teal-800); margin:0;">
//                     <i class="fas fa-video" style="color:var(--accent-coral); margin-right:6px;"></i>
//                     Realtime Detection · กล้อง Raspberry Pi
//                     <span id="rt-today-badge" style="display:none; margin-left:8px;" class="badge badge-healthy" style="font-size:.7rem;">Today</span>
//                 </h2>
//             </div>

//             <!-- Stat cards: realtime -->
//             <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:20px;">
//                 ${statCard('ตรวจจับวันนี้',  'rt-total',   'var(--teal-500)',     'var(--teal-50)',  'fa-fish')}
//                 ${statCard('พบโรค',          'rt-diseased','var(--accent-coral)', '#fff0f0',        'fa-exclamation-circle')}
//                 ${statCard('ปกติ',           'rt-healthy', 'var(--accent-lime)',  '#e6faf3',        'fa-check-circle')}
//                 ${statCard('กล้อง Active',   'rt-cameras', 'var(--accent-amber)', '#fff8e6',        'fa-video')}
//             </div>

//             <!-- RT breakdown + recent alerts -->
//             <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">

//                 <!-- WSSV / YHV bar breakdown -->
//                 <div class="panel">
//                     <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
//                         <p class="panel-title" style="margin:0;">การกระจายโรค (วันนี้)</p>
//                         <span id="rt-sessions" class="badge badge-info" style="font-size:.72rem;">0 sessions</span>
//                     </div>
//                     <div id="rt-breakdown">
//                         <div style="text-align:center; padding:30px; color:var(--text-muted); font-size:.85rem;">
//                             <i class="fas fa-satellite-dish" style="font-size:1.6rem; margin-bottom:8px; display:block; opacity:.35;"></i>
//                             รอข้อมูลจาก Pi…
//                         </div>
//                     </div>
//                 </div>

//                 <!-- Recent disease alerts from realtime -->
//                 <div class="panel">
//                     <p class="panel-title" style="margin-bottom:14px;">
//                         <i class="fas fa-bell" style="color:var(--accent-amber);"></i> แจ้งเตือนล่าสุด (Realtime)
//                     </p>
//                     <div id="rt-alerts" style="display:flex; flex-direction:column; gap:8px; overflow-y:auto; max-height:220px;">
//                         <p style="text-align:center; color:var(--text-muted); font-size:.85rem; padding:16px 0;">
//                             ยังไม่มีการแจ้งเตือน
//                         </p>
//                     </div>
//                 </div>
//             </div>

//         </div>
//     `;

//     fetchAndRender();

//     // auto-refresh ทุก 10 วินาที
//     if (_dashTimer) clearInterval(_dashTimer);
//     _dashTimer = setInterval(fetchAndRender, 10000);
// }

// /* ──────────────────────────────────────────────
//    HTML Helpers
// ────────────────────────────────────────────── */

// function statCard(label, id, color, bg, icon) {
//     return `
//         <div class="stat-card" style="position:relative; overflow:hidden;">
//             <div style="display:flex; justify-content:space-between; align-items:flex-start;">
//                 <div>
//                     <p style="font-size:.72rem; font-weight:600; color:var(--text-muted); text-transform:uppercase; letter-spacing:.07em; margin:0 0 10px;">${label}</p>
//                     <p id="${id}" style="font-size:2rem; font-weight:700; color:${color}; margin:0; font-family:var(--font-display);">—</p>
//                 </div>
//                 <div style="background:${bg}; width:42px; height:42px; border-radius:12px; display:flex; align-items:center; justify-content:center; color:${color}; flex-shrink:0;">
//                     <i class="fas ${icon}" style="font-size:1rem;"></i>
//                 </div>
//             </div>
//         </div>`;
// }

// /* ──────────────────────────────────────────────
//    Fetch & Render
// ────────────────────────────────────────────── */

// window.fetchAndRender = async function() {
//     try {
//         // ============================================================
//         // 📡 GET /dashboard_summary
//         // Backend: main.py → dashboard_summary()
//         // Query: table detections + table realtime_detections
//         // ============================================================
//         const res  = await fetch('http://127.0.0.1:8000/dashboard_summary');
//         const data = await res.json();

//         renderClassification(data.classification, data.recent_classify);
//         renderRealtime(data.realtime, data.recent_realtime);

//         const el = document.getElementById('dash-updated');
//         if (el) el.textContent = `อัปเดต ${new Date().toLocaleTimeString('th-TH')}`;

//     } catch {
//         // backend ไม่พร้อม → แสดง placeholder เงียบๆ
//     }
// };

// /* ── Classification section ── */
// function renderClassification(cls, recentCls) {
//     // stat cards
//     setVal('cls-total',    cls.total_scans);
//     setVal('cls-infected', cls.infected_scans);
//     setVal('cls-healthy',  cls.healthy_scans);
//     setVal('cls-top',      cls.top_disease || '—');

//     // donut chart
//     const ctx = document.getElementById('cls-donut');
//     if (ctx) {
//         // destroy ถ้ามีอยู่แล้ว
//         if (ctx._chart) ctx._chart.destroy();
//         ctx._chart = new Chart(ctx.getContext('2d'), {
//             type: 'doughnut',
//             data: {
//                 labels: ['Healthy', 'WSSV', 'YHV'],
//                 datasets: [{
//                     data: [cls.total_healthy, cls.total_wssv, cls.total_yhv],
//                     backgroundColor: ['#52d98e', '#ff6b6b', '#f4a742'],
//                     borderWidth: 0,
//                     hoverOffset: 6,
//                 }]
//             },
//             options: {
//                 responsive: true, maintainAspectRatio: false,
//                 cutout: '72%',
//                 plugins: {
//                     legend: {
//                         position: 'bottom',
//                         labels: { usePointStyle: true, padding: 16, color: 'var(--text-secondary)', font: { size: 12 } }
//                     }
//                 }
//             }
//         });
//     }

//     // recent uploads table
//     const tbody = document.getElementById('cls-table');
//     if (!tbody) return;
//     if (!recentCls.length) {
//         tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:var(--text-muted);padding:16px;">ยังไม่มีข้อมูล</td></tr>`;
//         return;
//     }
//     tbody.innerHTML = recentCls.map(r => {
//         const isD = (r.wssv_count + r.yhv_count) > 0;
//         const t   = (r.created_at || '').replace('T', ' ').slice(0, 16);
//         return `<tr>
//             <td style="font-weight:500;">${r.username || '—'}</td>
//             <td style="color:var(--accent-lime); font-weight:600;">${r.healthy_count ?? 0}</td>
//             <td style="color:var(--accent-coral); font-weight:600;">${r.wssv_count   ?? 0}</td>
//             <td style="color:var(--accent-amber); font-weight:600;">${r.yhv_count    ?? 0}</td>
//             <td style="color:var(--text-muted); font-size:.75rem;">${t}</td>
//         </tr>`;
//     }).join('');
// }

// /* ── Realtime section ── */
// function renderRealtime(rt, recentRt) {
//     // stat cards
//     setVal('rt-total',    rt.total_detections);
//     setVal('rt-diseased', rt.diseased);
//     setVal('rt-healthy',  rt.healthy);
//     setVal('rt-cameras',  rt.active_cameras);

//     const sessEl = document.getElementById('rt-sessions');
//     if (sessEl) sessEl.textContent = `${rt.sessions} sessions`;

//     const badge = document.getElementById('rt-today-badge');

//     // breakdown bars
//     const bd = document.getElementById('rt-breakdown');
//     if (bd) {
//         if (rt.total_detections === 0) {
//             bd.innerHTML = `<div style="text-align:center; padding:30px; color:var(--text-muted); font-size:.85rem;">
//                 <i class="fas fa-satellite-dish" style="font-size:1.6rem; margin-bottom:8px; display:block; opacity:.35;"></i>
//                 รอข้อมูลจาก Pi…
//             </div>`;
//             if (badge) badge.style.display = 'none';
//         } else {
//             if (badge) badge.style.display = 'inline-block';
//             const tot = rt.total_detections || 1;
//             bd.innerHTML = [
//                 { label:'Healthy', val:rt.healthy,  color:'var(--accent-lime)',  bg:'#e6faf3', icon:'fa-check-circle'  },
//                 { label:'WSSV',    val:rt.wssv,     color:'var(--accent-coral)', bg:'#fff0f0', icon:'fa-biohazard'     },
//                 { label:'YHV',     val:rt.yhv,      color:'var(--accent-amber)', bg:'#fff8e6', icon:'fa-virus'         },
//             ].map(d => {
//                 const pct = Math.round(d.val / tot * 100);
//                 return `
//                     <div style="margin-bottom:16px;">
//                         <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
//                             <span style="display:flex; align-items:center; gap:7px; font-size:.85rem; font-weight:600; color:var(--teal-800);">
//                                 <span style="width:28px;height:28px;border-radius:8px;background:${d.bg};display:flex;align-items:center;justify-content:center;">
//                                     <i class="fas ${d.icon}" style="color:${d.color};font-size:.8rem;"></i>
//                                 </span>
//                                 ${d.label}
//                             </span>
//                             <span style="font-size:.85rem; font-weight:700; color:${d.color};">${d.val} <span style="font-weight:400; color:var(--text-muted); font-size:.75rem;">(${pct}%)</span></span>
//                         </div>
//                         <div style="height:8px; background:var(--teal-50); border-radius:8px; overflow:hidden;">
//                             <div style="height:100%; width:${pct}%; background:${d.color}; border-radius:8px; transition:width .6s ease;"></div>
//                         </div>
//                     </div>`;
//             }).join('');
//         }
//     }

//     // recent realtime alerts
//     const alertsEl = document.getElementById('rt-alerts');
//     if (!alertsEl) return;
//     if (!recentRt.length) {
//         alertsEl.innerHTML = `<p style="text-align:center; color:var(--text-muted); font-size:.85rem; padding:16px 0;">ยังไม่มีการแจ้งเตือน</p>`;
//         return;
//     }
//     alertsEl.innerHTML = recentRt.map(r => {
//         const conf = (r.confidence * 100).toFixed(0);
//         const t    = (r.captured_at || '').replace('T', ' ').slice(11, 19);
//         const isWSSV = r.disease_label === 'WSSV';
//         const color  = isWSSV ? 'var(--accent-coral)' : 'var(--accent-amber)';
//         const bg     = isWSSV ? '#fff0f0' : '#fff8e6';
//         const icon   = isWSSV ? 'fa-biohazard' : 'fa-virus';
//         return `
//             <div class="alert-item" style="background:${bg}; border-left:3px solid ${color};">
//                 <i class="fas ${icon}" style="color:${color}; font-size:.95rem; margin-top:2px; flex-shrink:0;"></i>
//                 <div>
//                     <p style="font-size:.7rem; color:var(--text-muted); margin:0 0 2px; font-weight:500;">
//                         <i class="fas fa-video"></i> ${r.camera_id} &nbsp;·&nbsp; <i class="far fa-clock"></i> ${t}
//                     </p>
//                     <p style="font-size:.83rem; color:var(--text-primary); font-weight:600; margin:0;">
//                         พบ ${r.disease_label} · ความแม่นยำ ${conf}%
//                     </p>
//                 </div>
//             </div>`;
//     }).join('');
// }

// /* ── util ── */
// function setVal(id, val) {
//     const el = document.getElementById(id);
//     if (el) el.textContent = (val === undefined || val === null) ? '—' : val;
// }



import Chart from 'chart.js/auto';

const PC_BASE = 'http://127.0.0.1:8000';
const PI_BASE = 'http://172.20.10.2:8000';

let _dashTimer = null;

// ============================================================
// Dashboard Main
// ============================================================
export function renderDashboard(app) {
    app.innerHTML = `
        <div class="dashboard-wrapper">

            <div class="page-header">
                <div>
                    <h1>Dashboard Overview</h1>
                    <p>สรุปภาพรวมการตรวจโรคกุ้งก้ามกราม · อัปเดตทุก 10 วินาที</p>
                </div>
                <div style="display:flex; gap:10px; align-items:center;">
                    <span id="dash-updated" style="font-size:.78rem; color:var(--text-muted);"></span>
                    <button class="btn btn-primary" id="dash-refresh-btn">
                        <i class="fas fa-sync-alt"></i> Refresh
                    </button>
                </div>
            </div>

            <div style="display:flex; align-items:center; gap:10px; margin-bottom:14px;">
                <div style="width:4px; height:22px; background:var(--teal-400); border-radius:4px;"></div>
                <h2 style="font-family:var(--font-display); font-size:1.05rem; color:var(--teal-800); margin:0;">
                    <i class="fas fa-file-image" style="color:var(--teal-400); margin-right:6px;"></i>
                    Disease Classification · อัปโหลดรูปภาพ
                </h2>
            </div>

            <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:20px;">
                ${statCard('Total Scans', 'cls-total', 'var(--teal-500)', 'var(--teal-50)', 'fa-images')}
                ${statCard('พบโรค', 'cls-infected', 'var(--accent-coral)', '#fff0f0', 'fa-viruses')}
                ${statCard('ปกติ (Healthy)', 'cls-healthy', 'var(--accent-lime)', '#e6faf3', 'fa-check-circle')}
                ${statCard('โรคที่พบบ่อย', 'cls-top', 'var(--accent-amber)', '#fff8e6', 'fa-trophy')}
            </div>

            <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:30px;">
                <div class="panel">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                        <p class="panel-title" style="margin:0;">สัดส่วนโรคที่พบ</p>
                        <span class="badge badge-info" style="font-size:.72rem;">ทั้งหมด</span>
                    </div>
                    <div style="height:200px; display:flex; align-items:center; justify-content:center;">
                        <canvas id="cls-donut"></canvas>
                    </div>
                </div>

                <div class="panel">
                    <p class="panel-title" style="margin-bottom:14px;">
                        <i class="fas fa-clock" style="color:var(--teal-400);"></i> อัปโหลดล่าสุด
                    </p>
                    <div style="overflow-y:auto; max-height:220px;">
                        <table class="data-table" style="font-size:.82rem;">
                            <thead>
                                <tr>
                                    <th style="font-size:.7rem;">ผู้ใช้</th>
                                    <th style="font-size:.7rem;">Healthy</th>
                                    <th style="font-size:.7rem;">WSSV</th>
                                    <th style="font-size:.7rem;">YHV</th>
                                    <th style="font-size:.7rem;">เวลา</th>
                                </tr>
                            </thead>
                            <tbody id="cls-table">
                                <tr>
                                    <td colspan="5" style="text-align:center;color:var(--text-muted);padding:16px;">กำลังโหลด…</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div style="display:flex; align-items:center; gap:10px; margin-bottom:14px;">
                <div style="width:4px; height:22px; background:var(--accent-coral); border-radius:4px;"></div>
                <h2 style="font-family:var(--font-display); font-size:1.05rem; color:var(--teal-800); margin:0;">
                    <i class="fas fa-video" style="color:var(--accent-coral); margin-right:6px;"></i>
                    Realtime Detection · กล้อง Raspberry Pi
                    <span id="rt-today-badge" style="display:none; margin-left:8px;" class="badge badge-healthy">Today</span>
                </h2>
            </div>

            <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:20px;">
                ${statCard('ตรวจจับวันนี้', 'rt-total', 'var(--teal-500)', 'var(--teal-50)', 'fa-fish')}
                ${statCard('พบโรค', 'rt-diseased', 'var(--accent-coral)', '#fff0f0', 'fa-exclamation-circle')}
                ${statCard('ปกติ', 'rt-healthy', 'var(--accent-lime)', '#e6faf3', 'fa-check-circle')}
                ${statCard('กล้อง Active', 'rt-cameras', 'var(--accent-amber)', '#fff8e6', 'fa-video')}
            </div>

            <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
                <div class="panel">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                        <p class="panel-title" style="margin:0;">การกระจายโรค (วันนี้)</p>
                        <span id="rt-sessions" class="badge badge-info" style="font-size:.72rem;">0 detections</span>
                    </div>
                    <div id="rt-breakdown">
                        <div style="text-align:center; padding:30px; color:var(--text-muted); font-size:.85rem;">
                            <i class="fas fa-satellite-dish" style="font-size:1.6rem; margin-bottom:8px; display:block; opacity:.35;"></i>
                            รอข้อมูลจาก Pi…
                        </div>
                    </div>
                </div>

                <div class="panel">
                    <p class="panel-title" style="margin-bottom:14px;">
                        <i class="fas fa-bell" style="color:var(--accent-amber);"></i> แจ้งเตือนล่าสุด (Realtime)
                    </p>
                    <div id="rt-alerts" style="display:flex; flex-direction:column; gap:8px; overflow-y:auto; max-height:220px;">
                        <p style="text-align:center; color:var(--text-muted); font-size:.85rem; padding:16px 0;">
                            ยังไม่มีการแจ้งเตือน
                        </p>
                    </div>
                </div>
            </div>

        </div>
    `;

    const refreshBtn = document.getElementById('dash-refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', fetchAndRender);
    }

    fetchAndRender();

    if (_dashTimer) clearInterval(_dashTimer);
    _dashTimer = setInterval(fetchAndRender, 10000);
}

// ============================================================
// HTML Helpers
// ============================================================
function statCard(label, id, color, bg, icon) {
    return `
        <div class="stat-card" style="position:relative; overflow:hidden;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <p style="font-size:.72rem; font-weight:600; color:var(--text-muted); text-transform:uppercase; letter-spacing:.07em; margin:0 0 10px;">
                        ${label}
                    </p>
                    <p id="${id}" style="font-size:2rem; font-weight:700; color:${color}; margin:0; font-family:var(--font-display);">
                        —
                    </p>
                </div>
                <div style="background:${bg}; width:42px; height:42px; border-radius:12px; display:flex; align-items:center; justify-content:center; color:${color}; flex-shrink:0;">
                    <i class="fas ${icon}" style="font-size:1rem;"></i>
                </div>
            </div>
        </div>
    `;
}

// ============================================================
// Fetch & Render
// ============================================================
async function fetchAndRender() {
    await fetchClassificationPart();
    await fetchRealtimePart();

    const el = document.getElementById('dash-updated');
    if (el) {
        el.textContent = `อัปเดต ${new Date().toLocaleTimeString('th-TH')}`;
    }
}

async function fetchClassificationPart() {
    try {
        const res = await fetch(`${PC_BASE}/dashboard_summary`);
        if (!res.ok) throw new Error(`PC dashboard_summary ${res.status}`);

        const data = await res.json();

        const cls = data.classification || data || {};
        const recentCls = Array.isArray(data.recent_classify)
            ? data.recent_classify
            : Array.isArray(data.recent)
                ? data.recent
                : [];

        renderClassification(cls, recentCls);
    } catch (err) {
        console.error('classification fetch error:', err);
        renderClassificationFallback();
    }
}

async function fetchRealtimePart() {
    try {
        const res = await fetch(`${PI_BASE}/dashboard_summary`);
        if (!res.ok) throw new Error(`PI dashboard_summary ${res.status}`);

        const rtData = await res.json();

        let recentArr = [];
        if (Array.isArray(rtData.recent)) {
            recentArr = rtData.recent;
        } else if (typeof rtData.recent === 'string') {
            try {
                recentArr = JSON.parse(rtData.recent);
            } catch (e) {
                recentArr = [];
            }
        }

        renderRealtimeSection(rtData, recentArr);
    } catch (err) {
        console.error('realtime fetch error:', err);
        renderRealtimeFallback();
    }
}

// ============================================================
// Classification Section
// ============================================================
function renderClassification(cls, recentCls) {
    setVal('cls-total', cls.total_scans ?? 0);
    setVal('cls-infected', cls.infected_scans ?? 0);
    setVal('cls-healthy', cls.healthy_scans ?? 0);
    setVal('cls-top', cls.top_disease || '—');

    const ctx = document.getElementById('cls-donut');
    if (ctx) {
        const existing = Chart.getChart(ctx);
        if (existing) existing.destroy();

        new Chart(ctx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Healthy', 'WSSV', 'YHV'],
                datasets: [{
                    data: [
                        Number(cls.total_healthy ?? 0),
                        Number(cls.total_wssv ?? 0),
                        Number(cls.total_yhv ?? 0)
                    ],
                    backgroundColor: ['#52d98e', '#ff6b6b', '#f4a742'],
                    borderWidth: 0,
                    hoverOffset: 6,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '72%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            padding: 16,
                            color: '#4f6b68',
                            font: { size: 12 }
                        }
                    }
                }
            }
        });
    }

    const tbody = document.getElementById('cls-table');
    if (!tbody) return;

    if (!recentCls.length) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align:center;color:var(--text-muted);padding:16px;">ยังไม่มีข้อมูล</td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = recentCls.map(r => {
        const t = (r.created_at || '').replace('T', ' ').slice(0, 16);
        return `
            <tr>
                <td style="font-weight:500;">${escapeHtml(r.username || '—')}</td>
                <td style="color:var(--accent-lime); font-weight:600;">${r.healthy_count ?? 0}</td>
                <td style="color:var(--accent-coral); font-weight:600;">${r.wssv_count ?? 0}</td>
                <td style="color:var(--accent-amber); font-weight:600;">${r.yhv_count ?? 0}</td>
                <td style="color:var(--text-muted); font-size:.75rem;">${escapeHtml(t)}</td>
            </tr>
        `;
    }).join('');
}

function renderClassificationFallback() {
    setVal('cls-total', 0);
    setVal('cls-infected', 0);
    setVal('cls-healthy', 0);
    setVal('cls-top', '—');

    const tbody = document.getElementById('cls-table');
    if (tbody) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align:center;color:var(--text-muted);padding:16px;">
                    โหลดข้อมูลจากคอมไม่สำเร็จ
                </td>
            </tr>
        `;
    }
}

// ============================================================
// Realtime Section
// ============================================================
function renderRealtimeSection(rt, recentRt) {
    setVal('rt-total', rt.total_detections ?? 0);
    setVal('rt-diseased', rt.diseased_count ?? 0);
    setVal('rt-healthy', rt.healthy_count ?? 0);
    setVal('rt-cameras', 1);

    const badge = document.getElementById('rt-today-badge');
    if (badge) badge.style.display = 'inline-flex';

    const sessionsEl = document.getElementById('rt-sessions');
    if (sessionsEl) {
        sessionsEl.textContent = `${rt.total_detections ?? 0} detections`;
    }

    const breakdownEl = document.getElementById('rt-breakdown');
    if (breakdownEl) {
        const wssv = Number(rt.wssv_count ?? 0);
        const yhv = Number(rt.yhv_count ?? 0);
        const totalDisease = wssv + yhv;

        if (totalDisease === 0) {
            breakdownEl.innerHTML = `
                <div style="text-align:center; padding:30px; color:var(--text-muted); font-size:.85rem;">
                    ยังไม่มีข้อมูลโรคจาก Pi
                </div>
            `;
        } else {
            const wssvPct = ((wssv / totalDisease) * 100).toFixed(0);
            const yhvPct = ((yhv / totalDisease) * 100).toFixed(0);

            breakdownEl.innerHTML = `
                ${diseaseBar('WSSV', wssv, wssvPct, 'var(--accent-coral)', '#fff0f0', 'fa-biohazard')}
                ${diseaseBar('YHV', yhv, yhvPct, 'var(--accent-amber)', '#fff8e6', 'fa-virus')}
            `;
        }
    }

    const alertsEl = document.getElementById('rt-alerts');
    if (!alertsEl) return;

    if (!Array.isArray(recentRt) || !recentRt.length) {
        alertsEl.innerHTML = `
            <p style="text-align:center; color:var(--text-muted); font-size:.85rem; padding:16px 0;">
                ยังไม่มีการแจ้งเตือน
            </p>
        `;
        return;
    }

    alertsEl.innerHTML = recentRt.map(r => {
        const conf = ((Number(r.confidence) || 0) * 100).toFixed(0);
        const t = (r.created_at || '').replace('T', ' ').slice(11, 19);
        const isWSSV = String(r.disease_label || '').toUpperCase() === 'WSSV';
        const color = isWSSV ? 'var(--accent-coral)' : 'var(--accent-amber)';
        const bg = isWSSV ? '#fff0f0' : '#fff8e6';
        const icon = isWSSV ? 'fa-biohazard' : 'fa-virus';

        return `
            <div class="alert-item" style="background:${bg}; border-left:3px solid ${color}; padding:10px; border-radius:10px;">
                <div style="display:flex; gap:8px; align-items:flex-start;">
                    <i class="fas ${icon}" style="color:${color}; font-size:.95rem; margin-top:2px;"></i>
                    <div>
                        <p style="font-size:.7rem; color:var(--text-muted); margin:0 0 2px; font-weight:500;">
                            <i class="fas fa-video"></i> ${escapeHtml(r.camera_id || 'CAM-01')} &nbsp;·&nbsp;
                            <i class="far fa-clock"></i> ${escapeHtml(t)}
                        </p>
                        <p style="font-size:.83rem; color:var(--text-primary); font-weight:600; margin:0;">
                            พบ ${escapeHtml(r.disease_label || 'unknown')} · ความมั่นใจ ${conf}%
                        </p>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function renderRealtimeFallback() {
    setVal('rt-total', 0);
    setVal('rt-diseased', 0);
    setVal('rt-healthy', 0);
    setVal('rt-cameras', 0);

    const breakdownEl = document.getElementById('rt-breakdown');
    if (breakdownEl) {
        breakdownEl.innerHTML = `
            <div style="text-align:center; padding:30px; color:var(--text-muted); font-size:.85rem;">
                โหลดข้อมูลจาก Pi ไม่สำเร็จ
            </div>
        `;
    }

    const alertsEl = document.getElementById('rt-alerts');
    if (alertsEl) {
        alertsEl.innerHTML = `
            <p style="text-align:center; color:var(--text-muted); font-size:.85rem; padding:16px 0;">
                โหลดการแจ้งเตือนไม่สำเร็จ
            </p>
        `;
    }
}

function diseaseBar(label, count, pct, color, bg, icon) {
    return `
        <div style="margin-bottom:14px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                <span style="font-size:.86rem; font-weight:600; color:var(--text-primary);">
                    <i class="fas ${icon}" style="color:${color}; margin-right:6px;"></i>${label}
                </span>
                <span style="font-size:.8rem; color:var(--text-muted);">${count} ครั้ง · ${pct}%</span>
            </div>
            <div style="height:10px; background:${bg}; border-radius:999px; overflow:hidden;">
                <div style="height:100%; width:${pct}%; background:${color}; border-radius:999px;"></div>
            </div>
        </div>
    `;
}

// ============================================================
// Utils
// ============================================================
function setVal(id, val) {
    const el = document.getElementById(id);
    if (el) {
        el.textContent = (val === undefined || val === null) ? '—' : val;
    }
}

function escapeHtml(value) {
    return String(value)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
}