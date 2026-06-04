// ===================================
// table-manager.js
// ===================================
// Manages the constituency results table with sorting, filtering, pagination.
// Used primarily by index.html (index-shifts-tbody) and any page that has
// a full data table (tableBody).

let tableState = {
    currentPage:   1,
    itemsPerPage:  15,
    sortColumn:    'Margin',
    sortDir:       'desc',
    filteredData:  [],
};

// ── Full results table (index page if wired up) ──────────────────────────────

function initTable() {
    if (!electionData.results2026.length) return;
    tableState.filteredData = [...electionData.results2026];
    _sortData();
    _renderTable();
    _initPagination();
    console.log('[table] Initialized with', tableState.filteredData.length, 'rows');
}

function _renderTable() {
    const tbody = document.getElementById('tableBody');
    if (!tbody) return;

    if (tableState.filteredData.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center py-6 text-on-surface-variant">No results found</td></tr>`;
        _updatePagInfo(0);
        return;
    }

    const start = (tableState.currentPage - 1) * tableState.itemsPerPage;
    const slice = tableState.filteredData.slice(start, start + tableState.itemsPerPage);

    tbody.innerHTML = slice.map(row => {
        const constituency = row['Constituency']      || '—';
        const winner       = row['Leading Candidate'] || '—';
        const party        = shortPartyName(row['Leading Party']);
        const trailing     = row['Trailing Candidate']|| '—';
        const margin       = formatNumber(row['Margin'] || 0);
        const isNP         = party === 'TVK';
        const partyBadgeStyle = `background:${PARTY_COLORS[party] || '#333'};color:#000;`;

        return `<tr class="zebra-row hover:bg-surface-container transition-colors">
            <td class="px-6 py-4 font-semibold text-on-surface">${constituency}</td>
            <td class="px-6 py-4 text-on-surface-variant">${winner}</td>
            <td class="px-6 py-4">
                <span class="party-badge px-2 py-1 rounded text-[10px] font-bold" style="${partyBadgeStyle}">${party}</span>
            </td>
            <td class="px-6 py-4 text-on-surface-variant">${trailing}</td>
            <td class="px-6 py-4 font-label-md" style="color:${isNP ? '#00daf3' : '#ffe16d'}">${margin}</td>
        </tr>`;
    }).join('');

    _updatePagInfo(tableState.filteredData.length);
}

function _updatePagInfo(total) {
    const totalPages = Math.max(1, Math.ceil(total / tableState.itemsPerPage));
    const el = document.getElementById('page-info');
    if (el) el.textContent = `Page ${tableState.currentPage} of ${totalPages}`;

    const prev = document.getElementById('prev-page');
    const next = document.getElementById('next-page');
    if (prev) prev.disabled = tableState.currentPage === 1;
    if (next) next.disabled = tableState.currentPage >= totalPages;
}

function _initPagination() {
    document.getElementById('prev-page')?.addEventListener('click', () => {
        if (tableState.currentPage > 1) { tableState.currentPage--; _renderTable(); }
    });
    document.getElementById('next-page')?.addEventListener('click', () => {
        const max = Math.ceil(tableState.filteredData.length / tableState.itemsPerPage);
        if (tableState.currentPage < max) { tableState.currentPage++; _renderTable(); }
    });
}

function _sortData() {
    const col = tableState.sortColumn;
    tableState.filteredData.sort((a, b) => {
        let av = a[col] || '', bv = b[col] || '';
        if (col === 'Margin' || col === 'Constituency No.') {
            av = parseInt(av) || 0;
            bv = parseInt(bv) || 0;
        } else {
            av = String(av).toLowerCase();
            bv = String(bv).toLowerCase();
        }
        if (tableState.sortDir === 'asc') return av > bv ? 1 : -1;
        return av < bv ? 1 : -1;
    });
}

function sortTable(col) {
    if (tableState.sortColumn === col) {
        tableState.sortDir = tableState.sortDir === 'asc' ? 'desc' : 'asc';
    } else {
        tableState.sortColumn = col;
        tableState.sortDir    = 'asc';
    }
    tableState.currentPage = 1;
    _sortData();
    _renderTable();
}

// ── Inspector panel (index.html sidebar stats) ───────────────────────────────

function updateInspectorPanel(data) {
    const filtered = data || tableState.filteredData || electionData.results2026;
    setText('top-party-badge',  stats.leadingParty || '—');
    setText('margin-alert',     `> ${formatNumber(stats.highestMargin)}`);
    setText('close-races',      stats.closeRaces ?? countCloseRaces());
}
