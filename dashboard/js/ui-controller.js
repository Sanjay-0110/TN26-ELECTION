// ===================================
// ui-controller.js
// ===================================
// Main dashboard controller - orchestrates all components

function initDashboard() {
    console.log('🚀 Initializing dashboard...');
    
    try {
        // Step 1: Calculate statistics
        calculateStats();
        
        // Step 2: Update summary cards
        updateSummaryCards();
        
        // Step 3: Initialize table
        initTable();
        
        // Step 4: Initialize charts
        initializeCharts();
        
        // Step 5: Initialize filters
        initPartyFilter();
        initFilterHandlers();
        
        // Step 6: Initialize inspector panel
        updateInspectorPanel(tableState.filteredData);
        
        console.log('✓ Dashboard initialized successfully!');
    } catch (error) {
        console.error('✗ Dashboard initialization error:', error);
    }
}

// Update summary cards with statistics
function updateSummaryCards() {
    document.getElementById('total-votes').textContent = formatNumber(stats.totalVotes);
    document.getElementById('total-constituencies').textContent = stats.totalConstituencies;
    document.getElementById('leading-party').textContent = stats.leadingParty;
    document.getElementById('highest-margin').textContent = formatNumber(stats.highestMargin);
    
    console.log('✓ Summary cards updated');
}

function updateInspectorPanel(data) {
    const topParty = stats.leadingParty || 'N/A';
    const marginValue = stats.highestMargin ? `> ${formatNumber(stats.highestMargin)}` : 'N/A';
    const closeRaces = countCloseRaces(data || tableState.filteredData || electionData.results2026, 5000);

    document.getElementById('top-party-badge').textContent = topParty;
    document.getElementById('margin-alert').textContent = marginValue;
    document.getElementById('close-races').textContent = closeRaces;

    console.log('✓ Inspector panel updated');
}

// Add styling for party badges in table
document.addEventListener('DOMContentLoaded', () => {
    const style = document.createElement('style');
    style.textContent = `
        .party-badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85em;
            white-space: nowrap;
        }
    `;
    document.head.appendChild(style);
});

// Export data as CSV
function exportTableAsCSV() {
    let csv = 'Constituency,Winner,Party,Trailing,Margin\n';
    
    tableState.filteredData.forEach(row => {
        const constituency = row['Constituency'];
        const winner = row['Leading Candidate'];
        const party = cleanPartyName(row['Leading Party']);
        const trailing = row['Trailing Candidate'];
        const margin = row['Margin'];
        
        csv += `"${constituency}","${winner}","${party}","${trailing}",${margin}\n`;
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'tn26_election_results.csv';
    a.click();
    window.URL.revokeObjectURL(url);
    
    console.log('✓ Data exported as CSV');
}

// Print dashboard
function printDashboard() {
    window.print();
}

// Add these functions to window for console access
window.exportData = exportTableAsCSV;
window.printDash = printDashboard;
window.resetAllFilters = resetFilters;

console.log('Available commands in console:');
console.log('- exportData() : Export results as CSV');
console.log('- printDash() : Print dashboard');
console.log('- resetAllFilters() : Reset all filters');
