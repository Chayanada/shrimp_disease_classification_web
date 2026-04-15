const PI_BASE = "http://172.20.10.2:8000";

let _pollTimer = null;
let _nodeTimer = null;
let _visibilityHandler = null;
let _pageShowHandler = null;

const CAMERA_ID = "CAM-01";
const CAMERA_NAME = "บ่อพักน้ำ A";
const CAMERA_IP = "172.20.10.2";

// ใช้ URL ตรงที่คุณเปิดแล้วขึ้นจริง
const STREAM_URL = `${PI_BASE}/video_feed`;

export function renderRealtime(app) {
    cleanupRealtime();

    app.innerHTML = `
        <div class="dashboard-wrapper">

            <div class="page-header">
                <div>
                    <h1>Realtime Detection</h1>
                    <p>ระบบตรวจสอบโรคกุ้งผ่านกล้องแบบเรียลไทม์ · Raspberry Pi 5</p>
                </div>
                <div style="display:flex; gap:10px;">
                    <button class="btn btn-outline" id="btn-reconnect">
                        <i class="fas fa-redo"></i> Reconnect
                    </button>
                    <button class="btn btn-outline" id="btn-fullscreen">
                        <i class="fas fa-expand"></i> Fullscreen
                    </button>
                </div>
            </div>

            <div style="display:grid; grid-template-columns:1fr 340px; gap:20px; align-items:start;">

                <div style="display:flex; flex-direction:column; gap:18px;">

                    <div class="panel" style="padding:0; overflow:hidden;">
                        <div style="padding:13px 18px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--teal-50); background:var(--surface-tint);">
                            <div style="display:flex; align-items:center; gap:10px;">
                                <span class="dot-online" style="width:9px;height:9px;"></span>
                                <span style="font-weight:700; font-size:.95rem; color:var(--teal-900); font-family:var(--font-display);">
                                    ${CAMERA_ID} · ${CAMERA_NAME}
                                </span>
                            </div>
                            <div style="display:flex; align-items:center; gap:10px;">
                                <code style="font-size:.75rem; color:var(--text-muted); background:var(--teal-50); padding:3px 9px; border-radius:6px;">
                                    ${CAMERA_IP}
                                </code>
                                <span style="font-size:.75rem; color:var(--accent-coral); background:#fff0f0; padding:3px 9px; border-radius:6px; font-weight:600;">● LIVE</span>
                            </div>
                        </div>

                        <div id="stream-wrapper" style="position:relative; background:#0a1a1e; height:360px; width:100%;">
                            <div id="stream-host" style="width:100%; height:100%;"></div>

                            <div id="detection-overlay"
                                 style="position:absolute; bottom:14px; left:14px; display:flex; gap:8px; flex-wrap:wrap;">
                            </div>

                            <div style="position:absolute; top:12px; right:12px; background:rgba(0,0,0,.55); color:#fff; font-size:.75rem; padding:4px 10px; border-radius:6px; font-weight:600;">
                                <i class="fas fa-tachometer-alt"></i> <span id="fps-display">— FPS</span>
                            </div>
                        </div>

                        <div style="padding:12px 18px; display:grid; grid-template-columns:repeat(4,1fr); gap:8px; background:var(--surface-tint); border-top:1px solid var(--teal-50);">
                            ${footerStat("Healthy", "stat-healthy", "var(--accent-lime)", "fa-check-circle")}
                            ${footerStat("WSSV", "stat-wssv", "var(--accent-coral)", "fa-biohazard")}
                            ${footerStat("YHV", "stat-yhv", "var(--accent-amber)", "fa-virus")}
                            ${footerStat("Total", "stat-total", "var(--teal-500)", "fa-fish")}
                        </div>
                    </div>

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

                <div style="display:flex; flex-direction:column; gap:18px;">

                    <div class="panel">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:18px;">
                            <p class="panel-title" style="margin:0; display:flex; align-items:center; gap:8px;">
                                <i class="fas fa-microchip" style="color:var(--teal-400);"></i> Edge Node
                            </p>
                            <span class="badge badge-healthy" id="node-badge">Active</span>
                        </div>
                        ${nodeRow("CPU Usage", "—", "var(--accent-amber)", 0, "node-cpu", "node-cpu-bar")}
                        ${nodeRow("Memory", "—", "var(--teal-400)", 0, "node-mem", "node-mem-bar")}
                        ${nodeRow("Temp", "—", "var(--accent-coral)", 0, "node-temp", "node-temp-bar")}
                    </div>

                    <div class="panel" style="background:var(--teal-50); border-color:var(--border-medium);">
                        <p class="panel-title" style="font-size:.88rem; margin-bottom:14px;">
                            <i class="fas fa-video" style="color:var(--teal-400);"></i> Camera
                        </p>

                        <div style="display:flex; align-items:center; gap:10px; padding:10px 12px; border-radius:var(--radius-sm); background:var(--surface-white); border:1.5px solid var(--teal-400);">
                            <span class="dot-online" style="width:7px;height:7px;flex-shrink:0;"></span>
                            <div style="flex:1;">
                                <p style="font-size:.85rem; font-weight:600; color:var(--teal-800); margin:0;">${CAMERA_ID}</p>
                                <p style="font-size:.75rem; color:var(--text-muted); margin:0;">${CAMERA_NAME} · ${CAMERA_IP}</p>
                            </div>
                            <i class="fas fa-check-circle" style="color:var(--accent-lime); font-size:.9rem;"></i>
                        </div>
                    </div>

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

    document.getElementById("btn-reconnect")?.addEventListener("click", mountStreamIframe);
    document.getElementById("btn-fullscreen")?.addEventListener("click", toggleFullscreen);

    mountStreamIframe();
    startPollingStats();
    startNodePolling();

    _visibilityHandler = () => {
        if (document.visibilityState === "visible") {
            mountStreamIframe();
            startPollingStats();
            startNodePolling();
        }
    };
    document.addEventListener("visibilitychange", _visibilityHandler);

    _pageShowHandler = () => {
        mountStreamIframe();
        startPollingStats();
        startNodePolling();
    };
    window.addEventListener("pageshow", _pageShowHandler);
}

function mountStreamIframe() {
    const host = document.getElementById("stream-host");
    if (!host) return;

    host.innerHTML = "";

    const iframe = document.createElement("iframe");
    iframe.src = `${STREAM_URL}?t=${Date.now()}`;
    iframe.style.width = "100%";
    iframe.style.height = "100%";
    iframe.style.border = "0";
    iframe.style.display = "block";
    iframe.setAttribute("allow", "autoplay");

    host.appendChild(iframe);
}

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

function badge(text, color, bg) {
    return `
        <span style="background:${bg}; color:${color}; border:1px solid ${color}; padding:5px 10px; border-radius:999px; font-size:.75rem; font-weight:700;">
            ${text}
        </span>`;
}

function alertItem(time, cam, msg, type) {
    const MAP = {
        danger:  { i: "fa-exclamation-circle", c: "var(--accent-coral)", bg: "#fff0f0", bl: "var(--accent-coral)" },
        warning: { i: "fa-exclamation-triangle", c: "var(--accent-amber)", bg: "#fff8e6", bl: "var(--accent-amber)" },
        success: { i: "fa-check-circle", c: "var(--accent-lime)", bg: "#e6faf3", bl: "var(--accent-lime)" },
        info:    { i: "fa-info-circle", c: "var(--teal-400)", bg: "var(--teal-50)", bl: "var(--teal-400)" },
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

function rGroup(label, items, color, bg, icon) {
    const avg = items.length
        ? ((items.reduce((s, r) => s + (Number(r.confidence) || 0), 0) / items.length) * 100).toFixed(0) + "%"
        : "—";

    return `
        <div style="background:${bg}; border-radius:var(--radius-sm); padding:14px 10px; text-align:center;">
            <i class="fas ${icon}" style="color:${color}; font-size:1rem; margin-bottom:6px; display:block;"></i>
            <p style="font-size:.68rem; font-weight:700; color:${color}; text-transform:uppercase; letter-spacing:.05em; margin:0 0 4px;">${label}</p>
            <p style="font-size:1.5rem; font-weight:700; color:${color}; margin:0; font-family:var(--font-display);">${items.length}</p>
            <p style="font-size:.72rem; color:${color}; opacity:.7; margin:3px 0 0;">avg ${avg}</p>
        </div>`;
}

async function fetchRealtimeSummary() {
    const res = await fetch(`${PI_BASE}/realtime_summary?camera_id=${encodeURIComponent(CAMERA_ID)}&limit=50&fresh_seconds=30`);
    if (!res.ok) throw new Error("realtime_summary failed");
    const data = await res.json();
    return Array.isArray(data) ? data : [];
}

function renderSummaryRows(rows) {
    const healthy = rows.filter(r => Number(r.is_healthy) === 1);
    const wssv = rows.filter(r => Number(r.is_wssv) === 1);
    const yhv = rows.filter(r => Number(r.is_yhv) === 1);
    const diseased = rows.filter(r => Number(r.is_diseased) === 1);
    const total = rows.length;

    setText("stat-healthy", healthy.length);
    setText("stat-wssv", wssv.length);
    setText("stat-yhv", yhv.length);
    setText("stat-total", total);

    const fps = Math.min(30, Math.max(0, total));
    setText("fps-display", `${fps} FPS`);

    const overlay = document.getElementById("detection-overlay");
    if (overlay) {
        overlay.innerHTML = "";
        if (healthy.length) overlay.innerHTML += badge(`Healthy ${healthy.length}`, "var(--accent-lime)", "#e6faf3");
        if (wssv.length) overlay.innerHTML += badge(`WSSV ${wssv.length}`, "var(--accent-coral)", "#fff0f0");
        if (yhv.length) overlay.innerHTML += badge(`YHV ${yhv.length}`, "var(--accent-amber)", "#fff8e6");
    }

    const latestEl = document.getElementById("latest-result");
    if (latestEl) {
        if (!rows.length) {
            latestEl.innerHTML = `
                <div style="text-align:center; padding:24px; color:var(--text-muted); font-size:.88rem;">
                    <i class="fas fa-satellite-dish" style="font-size:1.8rem; margin-bottom:8px; display:block; opacity:.35;"></i>
                    รอสัญญาณจากกล้อง…
                </div>
            `;
        } else {
            latestEl.innerHTML = `
                <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:10px;">
                    ${rGroup("Healthy", healthy, "var(--accent-lime)", "#e6faf3", "fa-check-circle")}
                    ${rGroup("WSSV", wssv, "var(--accent-coral)", "#fff0f0", "fa-biohazard")}
                    ${rGroup("YHV", yhv, "var(--accent-amber)", "#fff8e6", "fa-virus")}
                </div>
            `;
        }
    }

    const alertsEl = document.getElementById("live-alerts-container");
    const alertStatus = document.getElementById("alert-status");

    if (!rows.length) {
        if (alertsEl) {
            alertsEl.innerHTML = `
                <p style="text-align:center; color:var(--text-muted); font-size:.85rem; padding:16px 0;">
                    ยังไม่มีการแจ้งเตือน
                </p>
            `;
        }
        if (alertStatus) {
            alertStatus.innerHTML = `<span style="width:7px;height:7px;border-radius:50%;background:#ccc;display:inline-block;"></span> รอสัญญาณ`;
            alertStatus.style.color = "var(--text-muted)";
        }
        return;
    }

    if (!diseased.length) {
        if (alertsEl) {
            alertsEl.innerHTML = `
                <p style="text-align:center; color:var(--text-muted); font-size:.85rem; padding:16px 0;">
                    ยังไม่มีการแจ้งเตือน
                </p>
            `;
        }
        if (alertStatus) {
            alertStatus.innerHTML = `<span style="width:7px;height:7px;border-radius:50%;background:var(--accent-lime);display:inline-block;"></span> ปกติ`;
            alertStatus.style.color = "var(--accent-lime)";
        }
        return;
    }

    if (alertStatus) {
        alertStatus.innerHTML = `<span style="width:7px;height:7px;border-radius:50%;background:var(--accent-coral);display:inline-block;"></span> ตรวจพบความผิดปกติ`;
        alertStatus.style.color = "var(--accent-coral)";
    }

    if (alertsEl) {
        alertsEl.innerHTML = diseased.slice(0, 10).map(r => {
            const time = ((r.captured_at || r.created_at || "").replace("T", " ").slice(11, 19)) || "--:--:--";
            const msg = `พบ ${escapeHtml(r.disease_label || "unknown")} · ${(Number(r.confidence || 0) * 100).toFixed(0)}%`;
            return alertItem(time, CAMERA_ID, msg, "danger");
        }).join("");
    }
}

function startPollingStats() {
    if (_pollTimer) clearInterval(_pollTimer);

    const run = async () => {
        try {
            const rows = await fetchRealtimeSummary();
            renderSummaryRows(rows);
        } catch (err) {
            console.error("realtime summary error:", err);
        }
    };

    run();
    _pollTimer = setInterval(run, 5000);
}

function startNodePolling() {
    if (_nodeTimer) clearInterval(_nodeTimer);

    const run = async () => {
        try {
            const res = await fetch(`${PI_BASE}/node_status`);
            if (!res.ok) throw new Error("node_status failed");

            const node = await res.json();

            setText("node-cpu", `${node.cpu ?? 0}%`);
            setText("node-mem", `${node.memory ?? 0}%`);
            setText("node-temp", `${node.temp ?? 0}°C`);

            setWidth("node-cpu-bar", `${clamp(node.cpu)}%`);
            setWidth("node-mem-bar", `${clamp(node.memory)}%`);
            setWidth("node-temp-bar", `${Math.min(100, clamp(node.temp))}%`);

            const badge = document.getElementById("node-badge");
            if (badge) badge.textContent = "Active";
        } catch (err) {
            console.error("node status error:", err);
        }
    };

    run();
    _nodeTimer = setInterval(run, 5000);
}

function cleanupRealtime() {
    if (_pollTimer) {
        clearInterval(_pollTimer);
        _pollTimer = null;
    }
    if (_nodeTimer) {
        clearInterval(_nodeTimer);
        _nodeTimer = null;
    }
    if (_visibilityHandler) {
        document.removeEventListener("visibilitychange", _visibilityHandler);
        _visibilityHandler = null;
    }
    if (_pageShowHandler) {
        window.removeEventListener("pageshow", _pageShowHandler);
        _pageShowHandler = null;
    }
}

function clamp(v) {
    const n = Number(v) || 0;
    return Math.max(0, Math.min(100, n));
}

function toggleFullscreen() {
    const el = document.getElementById("stream-wrapper");
    if (!document.fullscreenElement) el?.requestFullscreen?.();
    else document.exitFullscreen?.();
}

function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

function setWidth(id, value) {
    const el = document.getElementById(id);
    if (el) el.style.width = value;
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}