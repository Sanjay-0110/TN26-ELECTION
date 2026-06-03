// ===================================
// filter-handler.js
// ===================================
// Handles all filtering and search functionality

let filterState = {
    selectedParties: [],
    marginRange: 100000,
    searchQuery: ''
};

// Populate party filter dropdown
function initPartyFilter() {
    const parties = getUniqueParties();
    const filterSelect = document.getElementById('party-filter');
    
    // Clear existing options except the first one
    while (filterSelect.options.length > 1) {
        filterSelect.remove(1);
    }
    
    // Add party options
    parties.forEach(party => {
        const option = document.createElement('option');
        option.value = party;
        option.textContent = party;
        filterSelect.appendChild(option);
    });
    
    // Add event listener
    filterSelect.addEventListener('change', handleFilterChange);
    console.log('✓ Party filter initialized with', parties.length, 'parties');
}

// Handle filter changes
function handleFilterChange() {
    const partySelect = document.getElementById('party-filter');
    const marginRange = document.getElementById('margin-filter');
    const searchBox = document.getElementById('search-box');
    
    // Get selected parties
    filterState.selectedParties = Array.from(partySelect.selectedOptions).map(opt => opt.value);
    filterState.marginRange = parseInt(marginRange.value);
    filterState.searchQuery = searchBox.value.toLowerCase();
    
    // Update margin display
    document.getElementById('margin-value').textContent = 
        filterState.marginRange === 100000 ? 'All' : formatNumber(filterState.marginRange);
    
    // Apply filters
    applyFilters();
}

// Apply all filters
function applyFilters() {
    let filtered = [...electionData.results2026];
    
    // Filter by party
    if (filterState.selectedParties.length > 0) {
        filtered = filtered.filter(row => {
            const winningParty = cleanPartyName(row['Leading Party']);
            return filterState.selectedParties.includes(winningParty);
        });
    }
    
    // Filter by margin
    filtered = filtered.filter(row => {
        const margin = parseInt(row['Margin']) || 0;
        return margin <= filterState.marginRange;
    });
    
    // Filter by search query
    if (filterState.searchQuery) {
        filtered = filtered.filter(row => {
            const constituency = (row['Constituency'] || '').toLowerCase();
            const winner = (row['Leading Candidate'] || '').toLowerCase();
            const trailing = (row['Trailing Candidate'] || '').toLowerCase();
            
            return constituency.includes(filterState.searchQuery) ||
                   winner.includes(filterState.searchQuery) ||
                   trailing.includes(filterState.searchQuery);
        });
    }
    
    // Update UI
    tableState.filteredData = filtered;
    tableState.currentPage = 1;
    populateTable(tableState.filteredData);
    updateInspectorPanel(tableState.filteredData);
    
    console.log(`🔍 Filters applied: ${filtered.length} results`);
}

// Reset all filters
function resetFilters() {
    document.getElementById('party-filter').selectedIndex = 0;
    document.getElementById('margin-filter').value = 100000;
    document.getElementById('search-box').value = '';
    
    filterState = {
        selectedParties: [],
        marginRange: 100000,
        searchQuery: ''
    };
    
    document.getElementById('margin-value').textContent = 'All';
    
    tableState.filteredData = [...electionData.results2026];
    tableState.currentPage = 1;
    populateTable(tableState.filteredData);
    updateInspectorPanel(tableState.filteredData);
    
    console.log('✓ Filters reset');
}

// Initialize filter listeners
function initFilterHandlers() {
    // Party filter
    document.getElementById('party-filter').addEventListener('change', handleFilterChange);
    
    // Margin range
    document.getElementById('margin-filter').addEventListener('input', handleFilterChange);
    
    // Search box
    document.getElementById('search-box').addEventListener('input', handleFilterChange);
    
    // Reset button
    document.getElementById('reset-filters').addEventListener('click', resetFilters);
    
    console.log('✓ Filter handlers initialized');
}
