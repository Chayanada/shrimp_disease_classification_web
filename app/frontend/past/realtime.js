export function renderRealtime(app) {
    app.innerHTML = `
        <div class="dashboard-wrapper">

            <div class="page-header">
                <div>
                    <h1>Realtime Detection</h1>
                    <p>ระบบตรวจสอบโรคกุ้งผ่านกล้องแบบเรียลไทม์ · Raspberry Pi 5</p>
                </div>
                <div style="display:flex; gap:10px;">
                    <button class="btn btn-outline" id="btn-settings">
                        <i class="fas fa-sliders-h"></i> Camera Settings
                    </button>
                    <button class="btn btn-danger" id="btn-record">
                        <i class="fas fa-record-vinyl"></i> Record
                    </button>
                </div>
            </div>

            <div style="display:grid; grid-template-columns:1fr 340px; gap:20px; align-items:start;">

                <!-- LEFT -->
                <div style="display:flex; flex-direction:column; gap:18px;">

                    <div class="panel" style="padding:0; overflow:hidden;">

                        <div style="padding:13px 18px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--teal-50); background:var(--surface-tint);">
                            <div style="display:flex; align-items:center; gap:10px;">
                                <span class="dot-online" id="cam-dot" style="width:9px;height:9px;"></span>
                                <span style="font-weight:700; font-size:.95rem; color:var(--teal-900); font-family:var(--font-display);" id="cam-name">CAM-01 · บ่อพักน้ำ A</span>
                            </div>
                            <div style="display:flex; align-items:center; gap:10px;">
                                <code style="font-size:.75rem; color:var(--text-muted); background:var(--teal-50); padding:3px 9px; border-radius:6px;" id="cam-ip">172.20.10.2</code>
                                <span style="font-size:.75rem; color:var(--accent-coral); background:#fff0f0; padding:3px 9px; border-radius:6px; font-weight:600;">● LIVE</span>
                                <i class="fas fa-expand" style="color:var(--teal-300); cursor:pointer;" onclick="toggleFullscreen()"></i>
                            </div>
                        </div>

                        <!-- ============================================================
                             📡 LIVE STREAM จาก Raspberry Pi
                             img.src ชี้ตรงไป http://<PI_IP>:8000/video_feed
                             Pi รัน realtime.py ซึ่ง serve MJPEG stream
                             Browser ดึงตรง ไม่ผ่าน backend ของเรา
                             ถ้าต่อ Pi ไม่ได้ → onerror จะเรียก handleStreamError()
                             ============================================================ -->
                        <div style="position:relative; background:#0a1a1e; height:360px; width:100%;" id="stream-wrapper">
                            <img id="cam-stream"
                                 style="width:100%; height:100%; object-fit:cover; display:block;"
                                 onerror="handleStreamError()"/>

                            <!-- ============================================================
                                 🏷️ DETECTION OVERLAY
                                 อัปเดตโดย startPollingStats() ทุก 3 วิ
                                 ดึงจาก GET /realtime_summary → rows[0] (ผลล่าสุด)
                                 ============================================================ -->
                            <div id="detection-overlay"
                                 style="position:absolute; bottom:14px; left:14px; display:flex; gap:8px; flex-wrap:wrap;">
                            </div>

                            <div style="position:absolute; top:12px; right:12px; background:rgba(0,0,0,.55); color:#fff; font-size:.75rem; padding:4px 10px; border-radius:6px; font-weight:600; backdrop-filter:blur(4px);">
                                <i class="fas fa-tachometer-alt"></i> <span id="fps-display">— FPS</span>
                            </div>

                            <div id="no-signal"
                                 style="display:flex; position:absolute; inset:0; background:#0a1a1e; flex-direction:column; align-items:center; justify-content:center; color:#4a7a76; gap:10px;">
                                <i class="fas fa-video-slash" style="font-size:2.5rem;"></i>
                                <span style="font-size:.9rem; font-weight:500;">รอสัญญาณจากกล้อง…</span>
                                <button class="btn btn-outline" style="margin-top:6px; width:auto;" onclick="retryStream()">
                                    <i class="fas fa-redo"></i> Reconnect
                                </button>
                            </div>
                        </div>

                        <!-- ============================================================
                             📊 STATS BAR ใต้กล้อง
                             อัปเดตโดย startPollingStats() ทุก 3 วิ
                             ดึงจาก GET /realtime_summary → นับแยก label
                             ============================================================ -->
                        <div style="padding:12px 18px; display:grid; grid-template-columns:repeat(4,1fr); gap:8px; background:var(--surface-tint); border-top:1px solid var(--teal-50);">
                            ${footerStat('Healthy', 'stat-healthy', 'var(--accent-lime)',  'fa-check-circle')}
                            ${footerStat('WSSV',    'stat-wssv',    'var(--accent-coral)', 'fa-biohazard')}
                            ${footerStat('YHV',     'stat-yhv',     'var(--accent-amber)', 'fa-virus')}
                            ${footerStat('Total',   'stat-total',   'var(--teal-500)',     'fa-fish')}
                        </div>
                    </div>

                    <!-- ============================================================
                         📋 ผลการตรวจล่าสุด (summary 3 กล่อง)
                         อัปเดตโดย startPollingStats() ทุก 3 วิ
                         ดึงจาก GET /realtime_summary → จัดกลุ่มตาม disease_label
                         ============================================================ -->
                    <div class="panel">
                        <p class="panel-title" style="margin-bottom:14px;">
                            <i class="fas fa-poll" style="color:var(--teal-400);"></i> ผลการตรวจล่าสุด
                        </p>
                        <div id="latest-result">
                            <div style="text-align:center; padding:24px; color:var(--text-muted); font-size:.88rem;">
                                <i class="fas fa-satellite-dish" style="font-size:1.8rem; margin-bottom:8px; display:block; opacity:.35;"></i>
                                รอสัญญาณจากกล้อง…
                            </div>
                        </div>
                    </div>
                </div>

                <!-- RIGHT -->
                <div style="display:flex; flex-direction:column; gap:18px;">

                    <!-- Edge Node: ค่าจาก Pi จริงเพิ่มได้ทีหลังผ่าน GET /node_status -->
                    <div class="panel">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:18px;">
                            <p class="panel-title" style="margin:0; display:flex; align-items:center; gap:8px;">
                                <i class="fas fa-microchip" style="color:var(--teal-400);"></i> Edge Node
                            </p>
                            <span class="badge badge-healthy">Active</span>
                        </div>
                        <!-- ============================================================
                             🖥️ NODE STATUS
                             ตอนนี้ hardcode ไว้ก่อน
                             ถ้าจะดึงจริงให้เพิ่ม GET /node_status ใน realtime.py
                             แล้วเรียกใน startPollingStats() แล้วอัป id="node-cpu" เป็นต้น
                             ============================================================ -->
                        ${nodeRow('CPU Usage', '—', 'var(--accent-amber)', 0, 'node-cpu', 'node-cpu-bar')}
                        ${nodeRow('Memory',    '—', 'var(--teal-400)',     0, 'node-mem', 'node-mem-bar')}
                        ${nodeRow('Temp',      '—', 'var(--accent-coral)', 0, 'node-temp','node-temp-bar')}
                        <div style="margin-top:14px; padding-top:14px; border-top:1px solid var(--teal-50);">
                            <p style="font-size:.75rem; color:var(--text-muted); margin:0 0 4px;">AI Model Running</p>
                            <p style="font-size:.88rem; font-weight:600; color:var(--teal-600); margin:0;">
                                <i class="fas fa-brain"></i> YOLOv8 + EfficientNet-B0
                            </p>
                        </div>
                    </div>

                    <!-- ============================================================
                         🎥 CAMERA SWITCHER
                         คลิกแต่ละ item → switchCamera() → เปลี่ยน img.src ตรงไป Pi IP นั้น
                         ============================================================ -->
                    <div class="panel" style="background:var(--teal-50); border-color:var(--border-medium);">
                        <p class="panel-title" style="font-size:.88rem; margin-bottom:14px;">
                            <i class="fas fa-video" style="color:var(--teal-400);"></i> เปลี่ยนกล้อง
                        </p>
                        <div style="display:flex; flex-direction:column; gap:8px;" id="cam-list">
                            ${camListItem('CAM-01','บ่อพักน้ำ A',  '172.20.10.2',   true,  'http://172.20.10.2:8000/video_feed')}
                            ${camListItem('CAM-02','บ่ออนุบาล 1', '192.168.1.102', true,  'http://192.168.1.102:8000/video_feed')}
                            ${camListItem('CAM-03','บ่ออนุบาล 2', '192.168.1.103', false, '')}
                            ${camListItem('CAM-04','จุดคัดกรอง',  '192.168.1.104', true,  'http://192.168.1.104:8000/video_feed')}
                        </div>
                    </div>

                    <!-- ============================================================
                         🔔 LIVE ALERTS
                         ไม่มี mock — เริ่มว่าง
                         อัปเดตโดย startPollingStats() เมื่อ is_diseased === 1
                         ดึงจาก GET /realtime_summary → rows[0]
                         ============================================================ -->
                    <div class="panel" style="flex:1;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                            <p class="panel-title" style="margin:0; display:flex; align-items:center; gap:8px;">
                                <i class="fas fa-bell" style="color:var(--accent-amber);"></i> Live Alerts
                            </p>
                            <span style="display:flex; align-items:center; gap:5px; font-size:.78rem; color:var(--text-muted); font-weight:500;" id="alert-status">
                                <span style="width:7px;height:7px;border-radius:50%;background:#ccc;display:inline-block;"></span> รอสัญญาณ
                            </span>
                        </div>
                        <div id="live-alerts-container" style="display:flex; flex-direction:column; gap:8px; overflow-y:auto; max-height:340px;">
                            <p style="text-align:center; color:var(--text-muted); font-size:.85rem; padding:16px 0;">
                                ยังไม่มีการแจ้งเตือน
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    // ── เริ่มต้น: ตั้ง stream CAM-01 ก่อน (default) ──
    setStream('http://172.20.10.2:8000/video_feed');
    highlightCam('cam-item-CAM-01');

    // ── เริ่ม poll ข้อมูลจาก backend ──
    startPollingStats();
}

/* ──────────────────────────────────────────────
   HTML Helpers
────────────────────────────────────────────── */

function footerStat(label, id, color, icon) {
    return `
        <div style="text-align:center; padding:10px 6px; border-radius:var(--radius-sm); background:var(--surface-white);">
            <i class="fas ${icon}" style="color:${color}; font-size:.9rem; margin-bottom:4px; display:block;"></i>
            <p style="font-size:.7rem; color:var(--text-muted); margin:0; text-transform:uppercase; letter-spacing:.05em;">${label}</p>
            <p id="${id}" style="font-size:1.25rem; font-weight:700; color:${color}; margin:2px 0 0; font-family:var(--font-display);">—</p>
        </div>`;
}

function nodeRow(label, val, color, pct, valId, barId) {
    return `
        <div style="margin-bottom:12px;">
            <div style="display:flex; justify-content:space-between; font-size:.83rem; margin-bottom:5px;">
                <span style="color:var(--text-secondary);">${label}</span>
                <span id="${valId}" style="font-weight:600; color:${color};">${val}</span>
            </div>
            <div style="height:5px; background:var(--teal-50); border-radius:5px; overflow:hidden;">
                <div id="${barId}" style="height:100%; width:${pct}%; background:${color}; border-radius:5px; transition:width .5s;"></div>
            </div>
        </div>`;
}

function camListItem(id, name, ip, online, streamUrl) {
    const dot = online
        ? `<span class="dot-online" style="width:7px;height:7px;flex-shrink:0;"></span>`
        : `<span style="width:7px;height:7px;flex-shrink:0;background:#ccc;border-radius:50%;display:inline-block;"></span>`;
    return `
        <div onclick="switchCamera('${id}','${name}','${ip}','${streamUrl}')"
             style="display:flex; align-items:center; gap:10px; padding:10px 12px; border-radius:var(--radius-sm); background:var(--surface-white); cursor:pointer; border:1.5px solid transparent; transition:all .2s;"
             class="cam-item" id="cam-item-${id}">
            ${dot}
            <div style="flex:1;">
                <p style="font-size:.85rem; font-weight:600; color:var(--teal-800); margin:0;">${id}</p>
                <p style="font-size:.75rem; color:var(--text-muted); margin:0;">${name} · ${ip}</p>
            </div>
            <i class="fas fa-chevron-right" style="color:var(--teal-200); font-size:.75rem;"></i>
        </div>`;
}

function alertItem(time, cam, msg, type) {
    const MAP = {
        danger:  { i:'fa-exclamation-circle',  c:'var(--accent-coral)', bg:'#fff0f0', bl:'var(--accent-coral)' },
        warning: { i:'fa-exclamation-triangle', c:'var(--accent-amber)', bg:'#fff8e6', bl:'var(--accent-amber)' },
        success: { i:'fa-check-circle',          c:'var(--accent-lime)', bg:'#e6faf3', bl:'var(--accent-lime)'  },
        info:    { i:'fa-info-circle',            c:'var(--teal-400)',   bg:'var(--teal-50)', bl:'var(--teal-400)' },
    };
    const s = MAP[type] || MAP.info;
    return `
        <div class="alert-item" style="background:${s.bg}; border-left:3px solid ${s.bl};">
            <i class="fas ${s.i}" style="color:${s.c}; font-size:1rem; margin-top:2px; flex-shrink:0;"></i>
            <div>
                <p style="font-size:.72rem; color:var(--text-muted); margin:0 0 3px; font-weight:500;">
                    <i class="far fa-clock"></i> ${time} &nbsp;·&nbsp; <i class="fas fa-video"></i> ${cam}
                </p>
                <p style="font-size:.84rem; color:var(--text-primary); font-weight:600; margin:0;">${msg}</p>
            </div>
        </div>`;
}

/* ──────────────────────────────────────────────
   Stream Control
────────────────────────────────────────────── */

// ============================================================
// 📡 setStream: ชี้ img#cam-stream ตรงไป Pi IP
// streamUrl = "http://<PI_IP>:8000/video_feed"
// ============================================================
function setStream(streamUrl) {
    const img = document.getElementById('cam-stream');
    const ns  = document.getElementById('no-signal');
    if (!img) return;

    if (!streamUrl) {
        img.style.display = 'none';
        if (ns) ns.style.display = 'flex';
        return;
    }
    img.src           = streamUrl;   // ← ดึง MJPEG ตรงจาก Pi
    img.style.display = 'block';
    if (ns) ns.style.display = 'none';
}

function highlightCam(activeId) {
    document.querySelectorAll('.cam-item').forEach(el => {
        el.style.borderColor = 'transparent';
        el.style.background  = 'var(--surface-white)';
    });
    const el = document.getElementById(activeId);
    if (el) { el.style.borderColor = 'var(--teal-400)'; el.style.background = 'var(--teal-50)'; }
}

// ============================================================
// 🎥 switchCamera: เรียกเมื่อผู้ใช้คลิกเปลี่ยนกล้อง
// เปลี่ยน img.src ไป Pi อีกตัว
// ============================================================
window.switchCamera = function(id, name, ip, streamUrl) {
    document.getElementById('cam-name').textContent = `${id} · ${name}`;
    document.getElementById('cam-ip').textContent   = ip;
    highlightCam(`cam-item-${id}`);
    setStream(streamUrl);   // ← ชี้ stream ไป Pi ตัวใหม่
};

window.handleStreamError = function() {
    document.getElementById('cam-stream').style.display = 'none';
    document.getElementById('no-signal').style.display  = 'flex';
};

window.retryStream = function() {
    const img = document.getElementById('cam-stream');
    if (!img || !img.src) return;
    img.style.display = 'block';
    document.getElementById('no-signal').style.display = 'none';
    img.src = img.src.split('?')[0] + '?t=' + Date.now();  // force reload
};

window.toggleFullscreen = function() {
    const el = document.getElementById('stream-wrapper');
    if (!document.fullscreenElement) el?.requestFullscreen?.();
    else document.exitFullscreen?.();
};

/* ──────────────────────────────────────────────
   Polling: ดึงข้อมูลจาก Backend ทุก 3 วินาที
────────────────────────────────────────────── */

let _pollTimer   = null;
let _lastAlertId = null;  // ป้องกัน alert ซ้ำ

function startPollingStats() {
    if (_pollTimer) clearInterval(_pollTimer);

    _pollTimer = setInterval(async () => {

        try {
            const camId = document.getElementById('cam-name')?.textContent?.split(' ')[0] || 'CAM-01';
            // ============================================================
            // 🔁 GET /realtime_summary?fresh_seconds=30
            // Backend: realtime.py → get_realtime_summary(fresh_seconds=30)
            // คืนเฉพาะข้อมูลที่ Pi บันทึกใน 30 วิล่าสุด
            // ถ้า Pi ไม่ได้รัน → rows = [] → resetToWaiting()
            // ============================================================
            const res  = await fetch(`http://127.0.0.1:8000/realtime_summary?camera_id=${camId}&limit=20&fresh_seconds=30`);
            const rows = await res.json();

            if (!Array.isArray(rows) || !rows.length) {
                resetToWaiting();
                return;
            }

            // ── นับสถิติ ──────────────────────────────────────────
            const cnt = { Healthy: 0, WSSV: 0, YHV: 0 };
            rows.forEach(r => { if (cnt[r.disease_label] !== undefined) cnt[r.disease_label]++; });

            // ── อัป stats bar ใต้กล้อง ──
            document.getElementById('stat-healthy').textContent = cnt.Healthy;
            document.getElementById('stat-wssv').textContent    = cnt.WSSV;
            document.getElementById('stat-yhv').textContent     = cnt.YHV;
            document.getElementById('stat-total').textContent   = rows.length;

            // ── อัป detection overlay บนกล้อง ──
            const ov  = document.getElementById('detection-overlay');
            const lat = rows[0];  // ← ผลล่าสุด (ORDER BY captured_at DESC)
            if (ov && lat) {
                const isD = lat.is_diseased === 1;
                ov.innerHTML = isD
                    ? `<span style="background:rgba(255,107,107,.9);color:#fff;font-size:.72rem;font-weight:700;padding:4px 10px;border-radius:6px;backdrop-filter:blur(4px);">
                           <i class="fas fa-exclamation-circle"></i> ${lat.disease_label} · ${(lat.confidence*100).toFixed(0)}%
                       </span>`
                    : `<span style="background:rgba(82,217,142,.85);color:#fff;font-size:.72rem;font-weight:700;padding:4px 10px;border-radius:6px;backdrop-filter:blur(4px);">
                           <i class="fas fa-check-circle"></i> Healthy
                       </span>`;
            }

            // ── อัป "ผลการตรวจล่าสุด" panel ──
            const lr = document.getElementById('latest-result');
            if (lr) {
                const grp = { Healthy: [], WSSV: [], YHV: [] };
                rows.forEach(r => { if (grp[r.disease_label]) grp[r.disease_label].push(r); });
                lr.innerHTML = `
                    <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:12px;">
                        ${rGroup('Healthy', grp.Healthy, 'var(--accent-lime)',  '#e6faf3', 'fa-check-circle')}
                        ${rGroup('WSSV',    grp.WSSV,    'var(--accent-coral)', '#fff0f0', 'fa-biohazard')}
                        ${rGroup('YHV',     grp.YHV,     'var(--accent-amber)', '#fff8e6', 'fa-virus')}
                    </div>
                    <p style="font-size:.75rem; color:var(--text-muted); margin:12px 0 0; text-align:right;">
                        <i class="far fa-clock"></i> ${new Date().toLocaleTimeString('th-TH')}
                        &nbsp;·&nbsp; ${rows.length} ตัวใน session นี้
                    </p>`;
            }

            // ── อัป Live Alerts status dot ──
            const as = document.getElementById('alert-status');
            if (as) {
                as.innerHTML = `<span class="dot-online" style="width:7px;height:7px;"></span> Live`;
                as.style.color = 'var(--accent-lime)';
            }

            // ── Push alert เมื่อพบโรคใหม่ (ป้องกันซ้ำด้วย id) ──
            if (lat?.is_diseased === 1 && lat.id !== _lastAlertId) {
                _lastAlertId = lat.id;
                const ac = document.getElementById('live-alerts-container');
                if (ac) {
                    // ลบ "ยังไม่มีการแจ้งเตือน" ออกถ้ายังอยู่
                    const empty = ac.querySelector('p');
                    if (empty) empty.remove();

                    const now = new Date().toLocaleTimeString('th-TH');
                    ac.insertAdjacentHTML('afterbegin',
                        alertItem(now, camId,
                            `ตรวจพบ ${lat.disease_label} · ความแม่นยำ ${(lat.confidence*100).toFixed(0)}%`,
                            'danger'));

                    // เก็บแค่ 10 รายการล่าสุด
                    while (ac.children.length > 10) ac.removeChild(ac.lastChild);
                }
            }

        } catch {
            // Pi ยังไม่ได้เปิด หรือ backend ไม่ตอบ → ไม่ทำอะไร ไม่แสดง error
        }

        // ============================================================
        // 🖥️ GET /node_status  (optional — เปิดใช้เมื่อ Pi พร้อม)
        // ถ้าต้องการดึง CPU / RAM / Temp จริงจาก Pi
        // เพิ่ม endpoint นี้ใน main.py แล้วเอา comment ออกด้านล่าง
        // ============================================================
        // try {
        //     const ns   = await fetch('http://127.0.0.1:8000/node_status');
        //     const node = await ns.json();
        //     // node = { cpu: 68, memory: 54, temp: 65 }
        //     document.getElementById('node-cpu').textContent  = node.cpu  + '%';
        //     document.getElementById('node-mem').textContent  = node.memory + '%';
        //     document.getElementById('node-temp').textContent = node.temp + '°C';
        //     document.getElementById('node-cpu-bar').style.width  = node.cpu  + '%';
        //     document.getElementById('node-mem-bar').style.width  = node.memory + '%';
        //     document.getElementById('node-temp-bar').style.width = node.temp + '%';
        // } catch {}

    }, 3000);
}

// ============================================================
// 🔄 resetToWaiting: เรียกเมื่อ Pi ไม่ได้รัน หรือข้อมูลเก่าเกิน 30 วิ
// Reset UI ทุกอย่างกลับเป็นสถานะ "รอสัญญาณ"
// ============================================================
function resetToWaiting() {
    const ids = ['stat-healthy','stat-wssv','stat-yhv','stat-total'];
    ids.forEach(id => { const el = document.getElementById(id); if (el) el.textContent = '—'; });

    const ov = document.getElementById('detection-overlay');
    if (ov) ov.innerHTML = '';

    const lr = document.getElementById('latest-result');
    if (lr) lr.innerHTML = `
        <div style="text-align:center; padding:24px; color:var(--text-muted); font-size:.88rem;">
            <i class="fas fa-satellite-dish" style="font-size:1.8rem; margin-bottom:8px; display:block; opacity:.35;"></i>
            รอสัญญาณจากกล้อง…
        </div>`;

    const as = document.getElementById('alert-status');
    if (as) {
        as.innerHTML = `<span style="width:7px;height:7px;border-radius:50%;background:#ccc;display:inline-block;"></span> รอสัญญาณ`;
        as.style.color = 'var(--text-muted)';
    }
}

function rGroup(label, items, color, bg, icon) {
    const avg = items.length
        ? (items.reduce((s, r) => s + r.confidence, 0) / items.length * 100).toFixed(0) + '%'
        : '—';
    return `
        <div style="background:${bg}; border-radius:var(--radius-sm); padding:14px 10px; text-align:center;">
            <i class="fas ${icon}" style="color:${color}; font-size:1rem; margin-bottom:6px; display:block;"></i>
            <p style="font-size:.68rem; font-weight:700; color:${color}; text-transform:uppercase; letter-spacing:.05em; margin:0 0 4px;">${label}</p>
            <p style="font-size:1.5rem; font-weight:700; color:${color}; margin:0; font-family:var(--font-display);">${items.length}</p>
            <p style="font-size:.72rem; color:${color}; opacity:.7; margin:3px 0 0;">avg ${avg}</p>
        </div>`;
}