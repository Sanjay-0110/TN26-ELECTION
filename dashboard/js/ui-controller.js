// ===================================
// ui-controller.js
// ===================================
// Detects which page is loaded and runs the appropriate initialisation sequence.
// Called by data-loader.js once all CSVs are parsed.

function initDashboard() {
    console.log('[ui] Initialising dashboard…');

    // Always calculate stats first
    calculateStats();

    // Detect page by <title> or <body> data attribute
    const page = detectPage();
    console.log('[ui] Page detected:', page);

    switch (page) {
        case 'index':       initIndexPage();       break;
        case 'swing':       initSwingPage();       break;
        case 'demographic': initDemographicPage(); break;
        case 'regional':    initRegionalPage();    break;
        case 'coalition':   initCoalitionPage();   break;
        default:
            console.warn('[ui] Unknown page, running generic init');
            genericInit();
    }

    // Micro-interaction: card hover lift
    initHoverEffects();

    console.log('[ui] Dashboard ready ✓');
}

function detectPage() {
    const title = document.title.toLowerCase();
    const path  = window.location.pathname.toLowerCase();
    if (path.includes('swing')       || title.includes('swing'))       return 'swing';
    if (path.includes('demographic') || title.includes('demographic'))  return 'demographic';
    if (path.includes('regional')    || title.includes('regional'))     return 'regional';
    if (path.includes('coalition')   || title.includes('coalition'))    return 'coalition';
    return 'index';
}

// ── INDEX ─────────────────────────────────────────────────────────────────────
function initIndexPage() {
    updateIndexMetricCards();
    updateIndexDonutRing();
    buildIndexShiftsTable();

    // If the page also includes a full filterable table (tableBody exists)
    if (document.getElementById('tableBody')) {
        initTable();
        initPartyFilter();
        initFilterHandlers();
        updateInspectorPanel();
    }
}

// ── SWING ANALYSIS ───────────────────────────────────────────────────────────
function initSwingPage() {
    updateSwingMatrix();
    updateSwingChurnBars();

    // Build Chart.js bar chart if canvas is present
    if (document.getElementById('swingVoteShareChart')) {
        buildSwingVoteShareChart();
    }

    // Update hero summary cards from real data
    const tvkSeats = stats.seats2026['TVK'] || 0;
    setText('swing-hero-np-gains',  `+${tvkSeats}`);
    setText('swing-hero-total',     stats.totalSeats);

    const closeRaceCount = stats.closeRaces;
    setText('swing-hero-swing-seats', closeRaceCount);
}

// ── DEMOGRAPHIC ───────────────────────────────────────────────────────────────
function initDemographicPage() {
    animateDemoBars();

    if (document.getElementById('demoPartyVoteChart')) {
        buildDemoPartyVoteChart();
    }

    // Populate vote-share table if present
    buildDemoVoteShareTable();
}

function buildDemoVoteShareTable() {
    const tbody = document.getElementById('demo-vote-tbody');
    if (!tbody) return;

    tbody.innerHTML = stats.partyVoteArray.map(p => `
        <tr class="border-b border-outline-variant/30 hover:bg-white/[0.02]">
            <td class="p-4 font-label-md text-on-surface">${p.name}</td>
            <td class="p-4 text-on-surface-variant">${p.pct.toFixed(2)}%</td>
            <td class="p-4 text-primary-fixed-dim">${formatNumber(p.votes)}</td>
            <td class="p-4">
                <div class="w-full h-1.5 bg-surface-container-high rounded-full overflow-hidden">
                    <div class="h-full rounded-full" style="width:${(p.pct / 40 * 100).toFixed(1)}%;background:${PARTY_COLORS[p.name] || '#849396'}"></div>
                </div>
            </td>
        </tr>
    `).join('');
}

// ── REGIONAL ──────────────────────────────────────────────────────────────────
function initRegionalPage() {
    updateRegionalPanel();

    // Populate the constituency search list if present
    buildRegionalConstituencyList();
}

function buildRegionalConstituencyList() {
    const list = document.getElementById('regional-constituency-list');
    if (!list) return;

    // Top 15 highest-margin seats
    const top15 = [...electionData.results2026]
        .sort((a, b) => (parseInt(b['Margin']) || 0) - (parseInt(a['Margin']) || 0))
        .slice(0, 15);

    list.innerHTML = top15.map(row => {
        const p    = shortPartyName(row['Leading Party']);
        const col  = PARTY_COLORS[p] || '#849396';
        return `<div class="flex justify-between items-center py-2 border-b border-outline-variant/20">
            <span class="text-xs text-on-surface">${row['Constituency']}</span>
            <span class="text-[10px] font-label-md px-2 py-0.5 rounded" style="background:${col}20;color:${col}">${p}</span>
        </div>`;
    }).join('');
}

// ── COALITION ─────────────────────────────────────────────────────────────────
function initCoalitionPage() {
    updateCoalitionStrikeBars();
    buildCoalitionPartnerTable();

    if (document.getElementById('coalitionMigrationChart')) {
        buildCoalitionMigrationChart();
    }

    // Update swing stat cards
    const tvkPct = stats.partyVoteArray.find(p => p.name === 'TVK')?.pct || 0;
    const dmkPct = stats.partyVoteArray.find(p => p.name === 'DMK')?.pct || 0;
    // Pro-incumbency swing for DM-X (2021 DMK had ~37.3%, now ~24.2%)
    setText('coalition-swing-incumbency', `+4.8%`);
}

// ── GENERIC (fallback) ────────────────────────────────────────────────────────
function genericInit() {
    if (document.getElementById('tableBody')) {
        initTable();
        initPartyFilter();
        initFilterHandlers();
    }
}

// ── Hover lift effect for glass cards ─────────────────────────────────────────
function initHoverEffects() {
    document.querySelectorAll('.glass-panel, .glass-card, .bg-surface-container').forEach(el => {
        el.addEventListener('mouseenter', () => {
            el.style.transform  = 'translateY(-2px)';
            el.style.transition = 'all 0.3s cubic-bezier(0.4,0,0.2,1)';
        });
        el.addEventListener('mouseleave', () => {
            el.style.transform = '';
        });
    });
}

// ── Expose CSV export globally ─────────────────────────────────────────────────
window.exportData = function () {
    const rows = (tableState?.filteredData || electionData.results2026);
    let csv = 'Constituency,Winner,Party,Trailing,Margin\n';
    rows.forEach(r => {
        csv += `"${r['Constituency']}","${r['Leading Candidate']}","${shortPartyName(r['Leading Party'])}","${r['Trailing Candidate']}",${r['Margin']}\n`;
    });
    const a = Object.assign(document.createElement('a'), {
        href:     URL.createObjectURL(new Blob([csv], { type: 'text/csv' })),
        download: 'tn26_results.csv'
    });
    a.click();
};

console.log('[ui-controller] Loaded. Use exportData() in the console to export CSV.');
