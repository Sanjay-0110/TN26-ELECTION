// ===================================
// table-manager.js
// ===================================
// Manages the results table with sorting and pagination

let tableState = {
    currentPage: 1,
    itemsPerPage: 15,
    sortColumn: 0,
    sortDirection: 'asc',
    filteredData: []
};

// Populate table with data
function populateTable(data) {
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = '';
    
    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 20px;">No results found</td></tr>';
        return;
    }
    
    // Calculate pagination
    const startIndex = (tableState.currentPage - 1) * tableState.itemsPerPage;
    const endIndex = startIndex + tableState.itemsPerPage;
    const paginatedData = data.slice(startIndex, endIndex);
    
    // Populate rows
    paginatedData.forEach(row => {
        const tr = document.createElement('tr');
        
        const constituency = row['Constituency'] || 'N/A';
        const winner = row['Leading Candidate'] || 'N/A';
        const party = cleanPartyName(row['Leading Party'] || 'N/A');
        const trailing = row['Trailing Candidate'] || 'N/A';
        const margin = row['Margin'] ? formatNumber(row['Margin']) : 'N/A';
        
        tr.innerHTML = `
            <td>${constituency}</td>
            <td>${winner}</td>
            <td><span class="party-badge">${party}</span></td>
            <td>${trailing}</td>
            <td style="font-weight: 600; color: #667eea;">${margin}</td>
        `;
        
        tbody.appendChild(tr);
    });
    
    // Update pagination info
    updatePaginationInfo(data.length);
}

// Update pagination
function updatePaginationInfo(totalItems) {
    const totalPages = Math.ceil(totalItems / tableState.itemsPerPage);
    const pageInfo = document.getElementById('page-info');
    pageInfo.textContent = `Page ${tableState.currentPage} of ${totalPages}`;
    
    // Disable/enable buttons
    document.getElementById('prev-page').disabled = tableState.currentPage === 1;
    document.getElementById('next-page').disabled = tableState.currentPage === totalPages;
}

// Sort table data
function sortTable(columnIndex) {
    // Toggle sort direction
    if (tableState.sortColumn === columnIndex) {
        tableState.sortDirection = tableState.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        tableState.sortColumn = columnIndex;
        tableState.sortDirection = 'asc';
    }
    
    const columns = ['Constituency', 'Leading Candidate', 'Leading Party', 'Trailing Candidate', 'Margin'];
    const sortBy = columns[columnIndex];
    
    tableState.filteredData.sort((a, b) => {
        let aVal = a[sortBy] || '';
        let bVal = b[sortBy] || '';
        
        // Try to parse as numbers if sorting by Margin
        if (sortBy === 'Margin') {
            aVal = parseInt(aVal) || 0;
            bVal = parseInt(bVal) || 0;
        } else {
            aVal = String(aVal).toLowerCase();
            bVal = String(bVal).toLowerCase();
        }
        
        if (tableState.sortDirection === 'asc') {
            return aVal > bVal ? 1 : -1;
        } else {
            return aVal < bVal ? 1 : -1;
        }
    });
    
    tableState.currentPage = 1; // Reset to first page
    populateTable(tableState.filteredData);
}

// Initialize pagination buttons
function initPagination() {
    document.getElementById('prev-page').addEventListener('click', () => {
        if (tableState.currentPage > 1) {
            tableState.currentPage--;
            populateTable(tableState.filteredData);
        }
    });
    
    document.getElementById('next-page').addEventListener('click', () => {
        const totalPages = Math.ceil(tableState.filteredData.length / tableState.itemsPerPage);
        if (tableState.currentPage < totalPages) {
            tableState.currentPage++;
            populateTable(tableState.filteredData);
        }
    });
}

// Initialize table
function initTable() {
    tableState.filteredData = [...electionData.results2026];
    populateTable(tableState.filteredData);
    initPagination();
    console.log('✓ Table initialized');
}
