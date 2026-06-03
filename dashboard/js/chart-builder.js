// ===================================
// chart-builder.js
// ===================================
// Creates and manages all charts using Chart.js

let charts = {
    voteShareChart: null,
    percentageChart: null,
    comparisonChart: null
};

const chartColors = {
    'TVK': '#FF6B6B',
    'DMK': '#4ECDC4',
    'ADMK': '#45B7D1',
    'INC': '#96CEB4',
    'BJP': '#FFEAA7',
    'NTK': '#DDA15E',
    'VCK': '#BC6C25',
    'DMDK': '#C9ADA7'
};

function getColor(partyName, index) {
    if (chartColors[partyName]) {
        return chartColors[partyName];
    }
    const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA15E', '#BC6C25', '#C9ADA7'];
    return colors[index % colors.length];
}

// Build Vote Share Pie Chart
function buildVoteShareChart() {
    const ctx = document.getElementById('voteShareChart').getContext('2d');
    
    const labels = [];
    const data = [];
    const colors = [];
    
    electionData.partyVotes.forEach((row, index) => {
        const party = row['Party'].split('{')[0].trim();
        const votes = parseVoteCount(row['Vote Share']);
        labels.push(party);
        data.push(votes);
        colors.push(getColor(party, index));
    });
    
    if (charts.voteShareChart) {
        charts.voteShareChart.destroy();
    }
    
    charts.voteShareChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                label: 'Total Votes',
                data: data,
                backgroundColor: colors,
                borderColor: '#fff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        font: { size: 12 },
                        padding: 15
                    }
                }
            }
        }
    });
    
    console.log('✓ Vote Share Chart created');
}

// Build Percentage Bar Chart
function buildPercentageChart() {
    const ctx = document.getElementById('percentageChart').getContext('2d');
    
    const labels = [];
    const data = [];
    const colors = [];
    
    electionData.partyVotes.forEach((row, index) => {
        const party = row['Party'].split('{')[0].trim();
        const percentage = parsePercentage(row['Party']);
        labels.push(party);
        data.push(percentage);
        colors.push(getColor(party, index));
    });
    
    if (charts.percentageChart) {
        charts.percentageChart.destroy();
    }
    
    charts.percentageChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Vote Share %',
                data: data,
                backgroundColor: colors,
                borderColor: colors,
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    max: 40
                }
            }
        }
    });
    
    console.log('✓ Percentage Chart created');
}

// Build Comparison Chart (2021 vs 2026)
function buildComparisonChart() {
    const ctx = document.getElementById('comparisonChart').getContext('2d');
    const comparison = stats.partyComparison;
    
    const labels = Object.keys(comparison).sort((a, b) => {
        const changeA = comparison[a].change;
        const changeB = comparison[b].change;
        return changeB - changeA;
    });
    
    const data2021 = labels.map(party => comparison[party]['2021']);
    const data2026 = labels.map(party => comparison[party]['2026']);
    
    if (charts.comparisonChart) {
        charts.comparisonChart.destroy();
    }
    
    charts.comparisonChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: '2021 Seats',
                    data: data2021,
                    backgroundColor: '#95E1D3',
                    borderColor: '#38ada9',
                    borderWidth: 1
                },
                {
                    label: '2026 Seats',
                    data: data2026,
                    backgroundColor: '#667eea',
                    borderColor: '#764ba2',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    position: 'top'
                }
            }
        }
    });
    
    console.log('✓ Comparison Chart created');
}

// Initialize all charts
function initializeCharts() {
    console.log('📈 Initializing charts...');
    buildVoteShareChart();
    buildPercentageChart();
    buildComparisonChart();
}

// Update charts based on filter
function updateCharts(filteredData) {
    // Recalculate stats with filtered data
    // This would involve creating filtered datasets
    // For now, we can refresh the main charts
    initializeCharts();
}
