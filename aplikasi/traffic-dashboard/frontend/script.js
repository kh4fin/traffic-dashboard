const API_BASE = 'http://localhost:5000/api';
let currentChart = null;

async function fetchData(url) {
    const response = await fetch(url);
    if (!response.ok) throw new Error('Network response was not ok');
    return response.json();
}

function updateDate() {
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    const today = new Date();
    document.getElementById('currentDate').textContent = today.toLocaleDateString('id-ID', options);
}

function updateMainCard(latest) {
    const statusLabel = document.getElementById('statusLabel');
    const statusMessage = document.getElementById('statusMessage');
    const currentValue = document.getElementById('currentValue');
    const mainIcon = document.getElementById('mainIcon');
    const mainCard = document.getElementById('mainStatusCard');

    statusLabel.textContent = latest.status;
    statusLabel.style.color = latest.color;
    statusMessage.textContent = latest.message;
    currentValue.textContent = `± ${latest.value} Unit`;
    
    mainIcon.className = `bi ${latest.icon}`;
    mainIcon.style.color = latest.color;
    mainCard.style.borderLeft = `8px solid ${latest.color}`;
}

function updateForecast(forecast) {
    const grid = document.getElementById('forecastGrid');
    grid.innerHTML = '';

    forecast.forEach(item => {
        const div = document.createElement('div');
        div.className = 'forecast-item';
        
        let color = '#10b981';
        if (item.status === 'Ramai Lancar') color = '#f59e0b';
        if (item.status === 'Padat') color = '#ef4444';

        div.innerHTML = `
            <div class="forecast-time">${item.time}</div>
            <i class="bi bi-clock-history" style="color: ${color}; font-size: 1.5rem; display: block; margin-bottom: 10px;"></i>
            <span class="forecast-status" style="color: ${color}">${item.status}</span>
        `;
        grid.appendChild(div);
    });
}

async function loadDashboard(location = 'Dandangan') {
    const loading = document.getElementById('loadingOverlay');
    loading.style.display = 'flex'; // Tampilkan loading
    
    updateDate();
    try {
        const predictResult = await fetchData(`${API_BASE}/predict?location=${location}`);
        
        updateMainCard(predictResult.latest);
        updateForecast(predictResult.forecast);

        if (currentChart) {
            currentChart.destroy();
        }

        const compareCtx = document.getElementById('comparisonChart').getContext('2d');
        currentChart = new Chart(compareCtx, {
            type: 'line',
            data: {
                labels: Array.from({length: 40}, (_, i) => i + 1),
                datasets: [
                    {
                        label: 'Data Aktual',
                        data: predictResult.actual.slice(-40),
                        borderColor: '#94a3b8',
                        borderWidth: 2,
                        pointRadius: 0,
                        tension: 0.4,
                        fill: false
                    },
                    {
                        label: 'Prediksi LSTM',
                        data: predictResult.predicted.slice(-40),
                        borderColor: '#6366f1',
                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                        borderWidth: 4,
                        pointRadius: 0,
                        tension: 0.4,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top', labels: { usePointStyle: true, font: { family: 'Outfit' } } }
                },
                scales: {
                    y: { beginAtZero: true, grid: { display: false } },
                    x: { grid: { display: false } }
                }
            }
        });

        // Sembunyikan loading setelah semua selesai
        loading.style.display = 'none';

    } catch (error) {
        console.error('Error loading dashboard:', error);
        document.getElementById('statusLabel').textContent = "Offline";
        document.getElementById('statusMessage').textContent = "Gagal memuat data lokasi ini.";
        loading.style.display = 'none'; // Tetap sembunyikan jika error
    }
}

// Inisialisasi pendengar perubahan lokasi
document.getElementById('locationSelector').addEventListener('change', (e) => {
    loadDashboard(e.target.value);
});

// Muat dashboard pertama kali
loadDashboard();