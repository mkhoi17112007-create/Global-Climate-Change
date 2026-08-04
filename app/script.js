document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const searchBtn = document.getElementById('searchBtn');
    const cityInput = document.getElementById('cityInput');
    const weatherContent = document.getElementById('weatherContent');
    const loader = document.getElementById('loader');
    const weatherCard = document.getElementById('weatherCard');

    const cityNameEl = document.getElementById('cityName');
    const tempValueEl = document.getElementById('tempValue');
    const conditionEl = document.getElementById('weatherCondition');
    const humidityEl = document.getElementById('humidityValue');
    const windEl = document.getElementById('windValue');

    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    const menuToggle = document.getElementById('menuToggle');

    const sidebarLinks = {
        'side-home': document.getElementById('home-tab'),
        'side-data': document.getElementById('data-tab'),
        'side-predict': document.getElementById('predict-tab'),
        'side-map': document.getElementById('map-tab')
    };

    const pageTitle = document.getElementById('pageTitle');
    const dataSearchInput = document.getElementById('dataSearchInput');
    const datasetSelect = document.getElementById('datasetSelect');

    let weatherData = [];
    let isDataLoaded = false;
    let currentDataset = "state_temp_cleaned.csv";

    // Sidebar Toggle Logic
    menuToggle.addEventListener('click', () => {
        const isMobile = window.innerWidth <= 900;
        if (isMobile) {
            sidebar.classList.toggle('active');
        } else {
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('expanded');
        }
    });

    // Close sidebar on mobile when a link is clicked
    const closeSidebarOnMobile = () => {
        if (window.innerWidth <= 900) {
            sidebar.classList.remove('active');
        }
    };

    // Navigation Logic
    Object.keys(sidebarLinks).forEach(id => {
        const link = document.getElementById(id);
        if (link) {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                switchTab(id);
                closeSidebarOnMobile();
            });
        }
    });

    // Special case for About modal
    document.getElementById('side-about').addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById('aboutModal').style.display = 'block';
        closeSidebarOnMobile();
    });

    function switchTab(activeId) {
        Object.keys(sidebarLinks).forEach(id => {
            const link = document.getElementById(id);
            const tab = sidebarLinks[id];
            if (id === activeId) {
                link.classList.add('active');
                tab.classList.remove('hidden');
                pageTitle.textContent = link.querySelector('span').textContent;
            } else {
                link.classList.remove('active');
                tab.classList.add('hidden');
            }
        });

        if (activeId === 'side-data') renderDataTable();
    }

    // CSV Loading Logic
    function loadCSV(filename) {
        isDataLoaded = false;
        const tableContainer = document.querySelector('.table-container');
        if (tableContainer) {
            tableContainer.innerHTML = `
                <div style="text-align:center; padding: 2rem;">
                    <i class="fa-solid fa-circle-notch fa-spin" style="font-size: 2rem; color: #fdbb2d; margin-bottom: 1rem;"></i>
                    <p>Đang tải dữ liệu ${filename}...</p>
                </div>
            `;
        }
        
        Papa.parse(`../data/process/${filename}`, {
            download: true,
            header: true,
            dynamicTyping: true,
            skipEmptyLines: true,
            complete: function(results) {
                weatherData = results.data.filter(row => Object.keys(row).length > 0 && Object.values(row).some(v => v !== null && v !== ""));
                isDataLoaded = true;
                currentDataset = filename;
                
                if (!sidebarLinks['side-data'].classList.contains('hidden')) {
                    renderDataTable(true);
                }
            }
        });
    }

    loadCSV(currentDataset);

    if (datasetSelect) {
        datasetSelect.addEventListener('change', (e) => {
            loadCSV(e.target.value);
        });
    }

    // Data Search Logic
    if (dataSearchInput) {
        dataSearchInput.addEventListener('input', () => renderDataTable(true));
    }

    function renderDataTable(forceRedraw = false) {
        const tableContainer = document.querySelector('.table-container');
        if (!tableContainer || weatherData.length === 0) return;
        
        if (!forceRedraw && tableContainer.querySelector('table')) return;

        const searchTerm = dataSearchInput ? dataSearchInput.value.toLowerCase() : "";
        const filteredData = weatherData.filter(row => 
            Object.values(row).some(val => String(val).toLowerCase().includes(searchTerm))
        );

        const headers = Object.keys(weatherData[0]);
        let tableHTML = `<table class="csv-table"><thead><tr>`;
        headers.forEach(h => tableHTML += `<th>${h}</th>`);
        tableHTML += `</tr></thead><tbody>`;

        const previewRows = filteredData.slice(0, 50);
        if (previewRows.length === 0) {
            tableHTML += `<tr><td colspan="${headers.length}" style="text-align:center; padding:2rem;">Không tìm thấy kết quả.</td></tr>`;
        } else {
            previewRows.forEach(row => {
                tableHTML += `<tr>`;
                headers.forEach(h => {
                    let val = row[h];
                    if (typeof val === 'number') val = val.toFixed(2);
                    tableHTML += `<td>${val || '--'}</td>`;
                });
                tableHTML += `</tr>`;
            });
        }
        tableHTML += `</tbody></table>`;
        tableContainer.innerHTML = tableHTML;
    }

    // Weather Search
    const handleSearch = () => {
        const query = cityInput.value.trim().toLowerCase();
        if (!query) return;

        if (!isDataLoaded) {
            alert("Dữ liệu đang được tải...");
            return;
        }

        // Switch to home tab if not already there
        if (sidebarLinks['side-home'].classList.contains('hidden')) {
            switchTab('side-home');
        }

        weatherContent.classList.add('hidden');
        loader.style.display = 'block';

        setTimeout(() => {
            const cityRecords = weatherData.filter(row => {
                const cityName = (row.city || row.City || row.State || row.Country || "").toString().toLowerCase();
                return cityName.includes(query);
            });

            if (cityRecords.length === 0) {
                alert("Không tìm thấy dữ liệu.");
                loader.style.display = 'none';
                weatherContent.classList.remove('hidden');
                return;
            }

            const latestRecord = cityRecords[cityRecords.length - 1];
            const temp = latestRecord.average_temperature || latestRecord.city_temp || latestRecord.AverageTemperature;

            updateUI({
                city: latestRecord.city || latestRecord.City || latestRecord.State || latestRecord.Country,
                temperature: temp ? temp.toFixed(1) : "--",
                condition: "Dữ liệu lịch sử (" + (latestRecord.dt || "N/A") + ")",
                humidity: Math.floor(Math.random() * 40 + 40), 
                windSpeed: (Math.random() * 20 + 5).toFixed(1)
            });
        }, 800);
    };

    if (searchBtn) searchBtn.addEventListener('click', handleSearch);
    if (cityInput) cityInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSearch();
    });

    function updateUI(data) {
        cityNameEl.textContent = data.city;
        tempValueEl.textContent = data.temperature;
        conditionEl.textContent = data.condition;
        humidityEl.textContent = `${data.humidity}%`;
        windEl.textContent = `${data.windSpeed} km/h`;

        weatherCard.style.transform = 'scale(1.05)';
        setTimeout(() => weatherCard.style.transform = 'scale(1)', 300);

        loader.style.display = 'none';
        weatherContent.classList.remove('hidden');
    }

    // Modal Logic
    const aboutModal = document.getElementById('aboutModal');
    const closeBtn = document.querySelector('.close-btn');

    if (closeBtn) {
        closeBtn.addEventListener('click', () => aboutModal.style.display = 'none');
    }

    window.addEventListener('click', (e) => {
        if (e.target === aboutModal) aboutModal.style.display = 'none';
    });
});