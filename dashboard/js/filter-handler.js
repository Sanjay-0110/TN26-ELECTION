// ===================================
// filter-handler.js
// ===================================
// Party / margin / keyword filters for the full results table.

let filterState = {
    party:      '',
    maxMargin:  200000,
    search:     ''
};

function initPartyFilter() {
    const sel = document.getElementById('party-filter');
    if (!sel) return;

    // Clear all but the first placeholder option
    while (sel.options.length > 1) sel.remove(1);

    // Collect unique short party names from 2026 results
    const parties = [...new Set(
        electionData.results2026.map(r => shortPartyName(r['Leading Party']))
    )].sort();

    parties.forEach(p => {
        const opt = document.createElement('option');
        opt.value = opt.textContent = p;
        sel.appendChild(opt);
    });

    console.log('[filter] Party filter loaded with', parties.length, 'parties');
}

function initFilterHandlers() {
    document.getElementById('party-filter')  ?.addEventListener('change',  handleFilterChange);
    document.getElementById('margin-filter') ?.addEventListener('input',   handleFilterChange);
    document.getElementById('search-box')    ?.addEventListener('input',   handleFilterChange);
    document.getElementById('reset-filters') ?.addEventListener('click',   resetFilters);
}

function handleFilterChange() {
    filterState.party     = document.getElementById('party-filter')?.value  || '';
    filterState.maxMargin = parseInt(document.getElementById('margin-filter')?.value) || 200000;
    filterState.search    = (document.getElementById('search-box')?.value || '').toLowerCase();

    const display = document.getElementById('margin-value');
    if (display) display.textContent = filterState.maxMargin >= 200000 ? 'All' : formatNumber(filterState.maxMargin);

    applyFilters();
}

function applyFilters() {
    let data = [...electionData.results2026];

    if (filterState.party) {
        data = data.filter(r => shortPartyName(r['Leading Party']) === filterState.party);
    }
    data = data.filter(r => (parseInt(r['Margin']) || 0) <= filterState.maxMargin);

    if (filterState.search) {
        data = data.filter(r =>
            (r['Constituency']       || '').toLowerCase().includes(filterState.search) ||
            (r['Leading Candidate']  || '').toLowerCase().includes(filterState.search) ||
            (r['Trailing Candidate'] || '').toLowerCase().includes(filterState.search)
        );
    }

    tableState.filteredData = data;
    tableState.currentPage  = 1;
    _renderTable();           // defined in table-manager.js
    updateInspectorPanel(data);
    console.log(`[filter] ${data.length} results after filters`);
}

function resetFilters() {
    const pf = document.getElementById('party-filter');
    const mf = document.getElementById('margin-filter');
    const sb = document.getElementById('search-box');
    if (pf) pf.selectedIndex = 0;
    if (mf) mf.value = 200000;
    if (sb) sb.value = '';

    filterState = { party: '', maxMargin: 200000, search: '' };
    const display = document.getElementById('margin-value');
    if (display) display.textContent = 'All';

    tableState.filteredData = [...electionData.results2026];
    tableState.currentPage  = 1;
    _renderTable();
    updateInspectorPanel();
}
