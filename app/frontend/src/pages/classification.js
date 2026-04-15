const API_BASE = "http://127.0.0.1:8000";

export function renderClassification(app, username) {
    app.innerHTML = `
        <div class="dashboard-wrapper">

            <!-- Header -->
            <div class="page-header">
                <div>
                    <h1>Disease Classification</h1>
                    <p>อัปโหลดรูปภาพกุ้งก้ามกรามเพื่อวิเคราะห์โรคด้วย AI สองขั้นตอน</p>
                </div>
                <div style="display:flex; align-items:center; gap:8px; background:var(--teal-50); padding:8px 14px; border-radius:var(--radius-sm); border:1px solid var(--border-soft);">
                    <img src="https://ui-avatars.com/api/?name=${username}&size=26&background=e6f8f7&color=1a8077&rounded=true" style="border-radius:50%;width:24px;">
                    <span style="font-size:0.85rem; font-weight:600; color:var(--teal-700);">${username}</span>
                </div>
            </div>

            <div style="display:grid; grid-template-columns:1fr 2fr; gap:22px; align-items:start;">

                <!-- LEFT: Upload Panel -->
                <div style="display:flex; flex-direction:column; gap:16px;">

                    <!-- Upload Zone -->
                    <div class="panel" id="upload-section">
                        <p class="panel-title" style="margin-bottom:16px;">
                            <i class="fas fa-cloud-upload-alt" style="color:var(--teal-400);"></i> อัปโหลดรูปภาพ
                        </p>

                        <div class="drop-zone" id="dropZone" onclick="document.getElementById('fileInput').click()">
                            <div style="pointer-events:none;">
                                <div style="width:52px;height:52px;background:var(--teal-50);border-radius:14px;display:flex;align-items:center;justify-content:center;margin:0 auto 12px;">
                                    <i class="fas fa-image" style="font-size:1.4rem;color:var(--teal-400);"></i>
                                </div>
                                <p style="font-weight:600;color:var(--teal-800);margin:0 0 5px 0;">วางรูปหรือคลิกเพื่อเลือก</p>
                                <p style="font-size:0.8rem;color:var(--text-muted);margin:0;">รองรับ JPG, PNG · ขนาดสูงสุด 10 MB</p>
                            </div>
                        </div>

                        <input id="fileInput" type="file" accept="image/*" style="display:none;" />

                        <div id="preview-wrap" style="display:none; margin-top:14px;">
                            <div style="border-radius:var(--radius-md);overflow:hidden;border:1px solid var(--border-soft);">
                                <img id="original-img" style="width:100%;height:auto;display:block;max-height:220px;object-fit:cover;" />
                            </div>
                            <p id="fileNameDisplay" style="font-size:0.8rem;color:var(--text-muted);margin:8px 0 0 0;text-align:center;"></p>
                        </div>

                        <button id="detBtn" class="btn btn-primary" style="width:100%;margin-top:14px;display:none;justify-content:center;">
                            <i class="fas fa-search-plus"></i> วิเคราะห์ด้วย AI
                        </button>
                    </div>

                    <!-- Info Card -->
                    <div class="panel" style="background:var(--teal-50); border-color:var(--border-medium);">
                        <p class="panel-title" style="margin-bottom:12px; font-size:0.88rem;">
                            <i class="fas fa-info-circle" style="color:var(--teal-400);"></i> AI Pipeline
                        </p>
                        ${makePipelineStep(1, 'YOLO Detection', 'ตรวจจับตำแหน่งกุ้งในภาพ')}
                        ${makePipelineStep(2, 'EfficientNet-B0', 'จำแนกโรคทีละตัว (Healthy / WSSV / YHV)')}
                        ${makePipelineStep(3, 'Report & Save', 'บันทึกผลลงฐานข้อมูล')}
                    </div>
                </div>

                <!-- RIGHT: Loading + Result -->
                <div>
                    <!-- Loading State -->
                    <div id="loading-section" style="display:none;">
                        <div class="panel" style="text-align:center; padding:60px 20px;">
                            <div class="spinner"></div>
                            <p style="font-weight:600; color:var(--teal-800); font-size:1.05rem; margin:0 0 6px 0;">AI กำลังประมวลผล…</p>
                            <p style="font-size:0.85rem; color:var(--text-muted); margin:0;">กำลังวาด Bounding Box และบันทึกข้อมูล</p>
                        </div>
                    </div>

                    <!-- Result State -->
                    <div id="result-section" style="display:none;">
                        <div class="panel">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; padding-bottom:14px; border-bottom:1px solid var(--teal-50);">
                                <p class="panel-title" style="margin:0;">
                                    <i class="fas fa-poll" style="color:var(--teal-400);"></i> ผลการวิเคราะห์
                                </p>
                                <span id="result-time" style="font-size:0.8rem; color:var(--text-muted); background:var(--teal-50); padding:3px 10px; border-radius:6px;"></span>
                            </div>

                            <!-- Stats -->
                            <div id="stats-container" style="display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:22px;"></div>

                            <!-- Image Compare -->
                            <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
                                <div>
                                    <p style="font-size:0.8rem; font-weight:600; color:var(--text-muted); text-align:center; margin:0 0 8px 0; text-transform:uppercase; letter-spacing:0.06em;">ภาพต้นฉบับ</p>
                                    <div style="border-radius:var(--radius-md); overflow:hidden; border:1px solid var(--border-soft); background:var(--surface-tint); min-height:180px; display:flex; align-items:center; justify-content:center;">
                                        <img id="original-img-result" style="width:100%; height:auto; display:block;" />
                                    </div>
                                </div>
                                <div>
                                    <p style="font-size:0.8rem; font-weight:600; color:var(--teal-500); text-align:center; margin:0 0 8px 0; text-transform:uppercase; letter-spacing:0.06em;">ผล AI Detection</p>
                                    <div style="border-radius:var(--radius-md); overflow:hidden; border:2px solid var(--teal-300); background:var(--surface-tint); min-height:180px; display:flex; align-items:center; justify-content:center; box-shadow:0 4px 16px rgba(43,181,168,0.15);">
                                        <img id="detected-img" style="width:100%; height:auto; display:block;" />
                                    </div>
                                </div>
                            </div>

                            <!-- Re-analyze -->
                            <div style="margin-top:18px; text-align:center;">
                                <button class="btn btn-outline" id="resetBtn">
                                    <i class="fas fa-redo-alt"></i> วิเคราะห์รูปใหม่
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Empty State (default) -->
                    <div id="empty-state" class="panel" style="text-align:center; padding:60px 20px; border:1px dashed var(--border-medium);">
                        <div style="width:64px;height:64px;background:var(--teal-50);border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 16px;">
                            <i class="fas fa-fish" style="font-size:1.6rem;color:var(--teal-300);"></i>
                        </div>
                        <p style="font-weight:600; color:var(--teal-700); margin:0 0 6px 0;">ยังไม่มีผลการวิเคราะห์</p>
                        <p style="font-size:0.85rem; color:var(--text-muted); margin:0;">อัปโหลดรูปภาพกุ้งเพื่อเริ่มต้น</p>
                    </div>
                </div>

            </div>
        </div>
    `;

    // ---- Event Listeners ----
    const fileInput = document.getElementById('fileInput');
    const detBtn    = document.getElementById('detBtn');
    const dropZone  = document.getElementById('dropZone');

    // Drag & Drop
    dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('dragging'); });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragging'));
    dropZone.addEventListener('drop', e => {
        e.preventDefault();
        dropZone.classList.remove('dragging');
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) handleFileSelected(file);
    });

    fileInput.onchange = e => {
        const file = e.target.files[0];
        if (file) handleFileSelected(file);
    };

    detBtn.onclick = () => handleDetect(fileInput.files[0], username);

    document.getElementById('resetBtn')?.addEventListener('click', resetUI);

    function handleFileSelected(file) {
        document.getElementById('fileNameDisplay').innerText = file.name;
        document.getElementById('preview-wrap').style.display = 'block';
        document.getElementById('original-img').src = URL.createObjectURL(file);
        detBtn.style.display = 'flex';
        document.getElementById('empty-state').style.display = 'none';
        document.getElementById('result-section').style.display = 'none';
    }

    async function handleDetect(file, username) {
        if (!file) return;
        document.getElementById('upload-section').style.display = 'none';
        document.getElementById('loading-section').style.display = 'block';
        document.getElementById('empty-state').style.display = 'none';

        const fd = new FormData();
        fd.append('file', file);
        fd.append('username', username);

        try {
            const res  = await fetch(`${API_BASE}/upload_detection`, { method: 'POST', body: fd });
            const json = await res.json();

            if (json.status === 'success') {
                document.getElementById('loading-section').style.display = 'none';
                document.getElementById('result-section').style.display = 'block';
                document.getElementById('upload-section').style.display = 'block';
                detBtn.style.display = 'none';

                // Copy original preview to result side
                document.getElementById('original-img-result').src = document.getElementById('original-img').src;
                document.getElementById('detected-img').src = json.data.image_url;
                document.getElementById('result-time').innerText = '⏱ ' + (json.data.process_time || '—');

                const c = json.data.counts || { healthy: 0, wssv: 0, yhv: 0 };
                document.getElementById('stats-container').innerHTML = `
                    ${makeStatChip('Healthy', c.healthy ?? 0, '#e6faf3', '#0a6641', 'fa-check-circle')}
                    ${makeStatChip('WSSV',    c.wssv    ?? 0, '#fff0f0', '#c62828', 'fa-biohazard')}
                    ${makeStatChip('YHV',     c.yhv     ?? 0, '#fff8e1', '#8a5800', 'fa-virus')}
                    ${makeStatChip('เวลา',    json.data.process_time || '—', 'var(--teal-50)', 'var(--teal-700)', 'fa-stopwatch', true)}
                `;
            } else {
                alert('Error: ' + (json.message || 'Unknown'));
                resetUI();
            }
        } catch {
            alert('ไม่สามารถติดต่อเซิร์ฟเวอร์ได้');
            resetUI();
        }
    }

    function resetUI() {
        document.getElementById('loading-section').style.display = 'none';
        document.getElementById('result-section').style.display = 'none';
        document.getElementById('empty-state').style.display = 'block';
        document.getElementById('upload-section').style.display = 'block';
        document.getElementById('preview-wrap').style.display = 'none';
        detBtn.style.display = 'none';
        fileInput.value = '';
    }
}

/* ---- Helpers ---- */
function makePipelineStep(num, title, desc) {
    return `
        <div style="display:flex; align-items:flex-start; gap:10px; margin-bottom:10px;">
            <div style="width:22px;height:22px;border-radius:50%;background:var(--teal-400);color:#fff;font-size:0.72rem;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-family:var(--font-display);">${num}</div>
            <div>
                <p style="font-size:0.85rem;font-weight:600;color:var(--teal-800);margin:0;">${title}</p>
                <p style="font-size:0.78rem;color:var(--text-muted);margin:2px 0 0 0;">${desc}</p>
            </div>
        </div>
    `;
}

function makeStatChip(label, value, bg, color, icon, isText = false) {
    return `
        <div style="background:${bg};border-radius:var(--radius-sm);padding:14px;text-align:center;border:1px solid rgba(0,0,0,0.04);">
            <i class="fas ${icon}" style="color:${color};font-size:1rem;margin-bottom:6px;display:block;"></i>
            <p style="font-size:0.72rem;font-weight:600;color:${color};text-transform:uppercase;letter-spacing:0.06em;margin:0 0 4px 0;">${label}</p>
            <p style="font-size:${isText ? '0.9rem' : '1.4rem'};font-weight:700;color:${color};margin:0;font-family:var(--font-display);">${isText ? value : value + ' ตัว'}</p>
        </div>
    `;
}