import Chart from 'chart.js/auto';

export function renderDashboard(app) {
    // ใช้ style บังคับให้แสดงผลเต็มจอ ชิดซ้าย และไม่กระจุกตรงกลาง
    app.innerHTML = `
        <div class="dashboard-wrapper" style="padding: 30px; width: 100%; text-align: left; box-sizing: border-box; display: block;">
            
            <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 30px;">
                <div>
                    <h1 style="margin: 0; font-size: 1.8rem; color: #1e293b;">Dashboard Overview</h1>
                    <p style="margin: 5px 0 0 0; color: #64748b; font-size: 0.95rem;">สรุปผลการตรวจจับโรคกุ้งแบบ Realtime และอัปโหลด</p>
                </div>
                <button style="background: #1e3a8a; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-size: 0.9rem; font-weight: 600; display: flex; align-items: center; gap: 8px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); transition: 0.2s;">
                    <i class="fas fa-download"></i> Export Report
                </button>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px;">
                
                <div style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <h3 style="color: #64748b; font-size: 0.85rem; font-weight: 600; margin: 0 0 10px 0;">TOTAL INSPECTIONS</h3>
                            <p id="total-count" style="font-size: 2rem; font-weight: 700; color: #0f172a; margin: 0;">250</p>
                        </div>
                        <div style="background: #f1f5f9; padding: 12px; border-radius: 10px; color: #3b82f6;">
                            <i class="fas fa-microscope" style="font-size: 1.2rem;"></i>
                        </div>
                    </div>
                    <div style="margin-top: 15px; font-size: 0.85rem; color: #10b981; font-weight: 500;">
                        <i class="fas fa-arrow-up"></i> 12% จากสัปดาห์ที่แล้ว
                    </div>
                </div>
                
                <div style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <h3 style="color: #64748b; font-size: 0.85rem; font-weight: 600; margin: 0 0 10px 0;">INFECTED SHRIMP</h3>
                            <p id="infected-count" style="font-size: 2rem; font-weight: 700; color: #ef4444; margin: 0;">30</p>
                        </div>
                        <div style="background: #fef2f2; padding: 12px; border-radius: 10px; color: #ef4444;">
                            <i class="fas fa-viruses" style="font-size: 1.2rem;"></i>
                        </div>
                    </div>
                    <div style="margin-top: 15px; font-size: 0.85rem; color: #64748b;">
                        พบโรค AHPND / EHP / WSSV
                    </div>
                </div>

                <div style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <h3 style="color: #64748b; font-size: 0.85rem; font-weight: 600; margin: 0 0 10px 0;">HEALTHY SHRIMP</h3>
                            <p id="healthy-count" style="font-size: 2rem; font-weight: 700; color: #10b981; margin: 0;">220</p>
                        </div>
                        <div style="background: #ecfdf5; padding: 12px; border-radius: 10px; color: #10b981;">
                            <i class="fas fa-check-circle" style="font-size: 1.2rem;"></i>
                        </div>
                    </div>
                    <div style="margin-top: 15px; font-size: 0.85rem; color: #64748b;">
                        สถานะปกติ
                    </div>
                </div>

                <div style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <h3 style="color: #64748b; font-size: 0.85rem; font-weight: 600; margin: 0 0 10px 0;">ACTIVE CAMERAS</h3>
                            <p id="pi-status" style="font-size: 2rem; font-weight: 700; color: #f59e0b; margin: 0;">3</p>
                        </div>
                        <div style="background: #fffbeb; padding: 12px; border-radius: 10px; color: #f59e0b;">
                            <i class="fas fa-video" style="font-size: 1.2rem;"></i>
                        </div>
                    </div>
                    <div style="margin-top: 15px; font-size: 0.85rem; color: #10b981; font-weight: 500;">
                        <i class="fas fa-wifi"></i> Online ทุกจุด
                    </div>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-bottom: 30px;">
                <div style="background: white; padding: 25px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
                    <h3 style="font-size: 1.1rem; color: #1e293b; margin: 0 0 20px 0;">แนวโน้มการพบโรค (7 วันล่าสุด)</h3>
                    <div style="position: relative; height: 300px; width: 100%;">
                        <canvas id="diseaseChart"></canvas>
                    </div>
                </div>
                <div style="background: white; padding: 25px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
                    <h3 style="font-size: 1.1rem; color: #1e293b; margin: 0 0 20px 0;">สัดส่วนโรคที่พบ</h3>
                    <div style="position: relative; height: 300px; width: 100%; display: flex; justify-content: center; align-items: center;">
                        <canvas id="diseaseRatioChart"></canvas>
                    </div>
                </div>
            </div>

            <div style="background: white; padding: 25px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h3 style="font-size: 1.1rem; color: #1e293b; margin: 0;">ประวัติการตรวจล่าสุด</h3>
                    <a href="#" style="color: #3b82f6; text-decoration: none; font-size: 0.9rem; font-weight: 500;">ดูทั้งหมด <i class="fas fa-chevron-right" style="font-size: 0.8rem;"></i></a>
                </div>
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse; text-align: left;">
                        <thead>
                            <tr style="border-bottom: 2px solid #e2e8f0; color: #64748b;">
                                <th style="padding: 12px 10px; font-weight: 600; font-size: 0.9rem;">เวลา (Time)</th>
                                <th style="padding: 12px 10px; font-weight: 600; font-size: 0.9rem;">แหล่งที่มา (Source)</th>
                                <th style="padding: 12px 10px; font-weight: 600; font-size: 0.9rem;">ผู้ใช้งาน (User)</th>
                                <th style="padding: 12px 10px; font-weight: 600; font-size: 0.9rem;">ผลตรวจ (Result)</th>
                                <th style="padding: 12px 10px; font-weight: 600; font-size: 0.9rem;">จัดการ (Action)</th>
                            </tr>
                        </thead>
                        <tbody id="dashboard-table-body">
                            </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;

    setTimeout(() => { initDashboardCharts(); }, 100);
}

async function fetchDashboardData() {
    // ข้อมูลจำลอง เพื่อให้เห็นโครงสร้างสวยๆ ก่อนต่อ API หลังบ้าน
    const mockData = {
        total: 250, infected: 30, healthy: 220,
        lineChartData: [2, 5, 3, 8, 4, 10, 5], 
        ratioChartData: [15, 8, 7], 
        recentLogs: [
            { time: '10:30 น. (28 มี.ค.)', source: 'Raspberry Pi #01', user: 'System Auto', result: 'พบโรค AHPND', confidence: '98%' },
            { time: '09:15 น. (28 มี.ค.)', source: 'Web Upload', user: 'Owner Nai', result: 'ปกติ', confidence: '95%' },
            { time: '16:40 น. (27 มี.ค.)', source: 'Web Upload', user: 'User01', result: 'พบโรค EHP', confidence: '92%' },
            { time: '11:20 น. (27 มี.ค.)', source: 'Raspberry Pi #02', user: 'System Auto', result: 'ปกติ', confidence: '97%' },
        ]
    };

    // ใส่ข้อมูลลงตาราง
    const tbody = document.getElementById('dashboard-table-body');
    if (tbody) {
        tbody.innerHTML = ''; 
        mockData.recentLogs.forEach(log => {
            const isNormal = log.result === 'ปกติ';
            const badgeBg = isNormal ? '#dcfce7' : '#fee2e2';
            const badgeColor = isNormal ? '#166534' : '#991b1b';
            
            tbody.innerHTML += `
                <tr style="border-bottom: 1px solid #f1f5f9; transition: 0.2s;">
                    <td style="padding: 15px 10px; font-size: 0.9rem; color: #334155;">${log.time}</td>
                    <td style="padding: 15px 10px; font-size: 0.9rem; color: #334155;">${log.source}</td>
                    <td style="padding: 15px 10px; font-size: 0.9rem; color: #334155;">
                        <span style="display:inline-flex; align-items:center; gap:5px;"><i class="fas fa-user-circle" style="color:#cbd5e1;"></i> ${log.user}</span>
                    </td>
                    <td style="padding: 15px 10px; font-size: 0.9rem;">
                        <span style="background: ${badgeBg}; color: ${badgeColor}; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">
                            ${log.result} ${!isNormal ? `(${log.confidence})` : ''}
                        </span>
                    </td>
                    <td style="padding: 15px 10px;">
                        <button style="background:none; border: 1px solid #cbd5e1; color: #475569; padding: 5px 12px; border-radius: 6px; cursor: pointer; font-size: 0.8rem; font-weight: 500;">ดูรูปภาพ</button>
                    </td>
                </tr>
            `;
        });
    }
    return mockData;
}

async function initDashboardCharts() {
    const data = await fetchDashboardData();
    if (!data) return;

    // กราฟเส้น (Line)
    const lineCtx = document.getElementById('diseaseChart');
    if (lineCtx) {
        new Chart(lineCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'จำนวนเคสที่พบโรค',
                    data: data.lineChartData,
                    borderColor: '#3b82f6', // สีฟ้าแบบธุรกิจ
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4, // ทำให้เส้นโค้งสมูท
                    pointBackgroundColor: '#ffffff',
                    pointBorderColor: '#3b82f6',
                    pointBorderWidth: 2,
                    pointRadius: 4
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, grid: { borderDash: [2, 4], color: '#e2e8f0' } }, x: { grid: { display: false } } } }
        });
    }

    // กราฟโดนัท (Donut)
    const donutCtx = document.getElementById('diseaseRatioChart');
    if (donutCtx) {
        new Chart(donutCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['AHPND', 'EHP', 'WSSV'],
                datasets: [{
                    data: data.ratioChartData,
                    backgroundColor: ['#ef4444', '#f59e0b', '#3b82f6'],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, cutout: '70%', plugins: { legend: { position: 'bottom', labels: { usePointStyle: true, padding: 20 } } } }
        });
    }
}





