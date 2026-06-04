// ===================================
// chart-builder.js
// ===================================
// Builds all Chart.js visualisations.
// Targets canvas / DOM elements that ACTUALLY EXIST in the HTML files.
// Must be loaded AFTER stats-calculator.js.

// ── Theme colours matching the Aura Noir design tokens ──────────────────────
const COLORS = {
    cyan:       '#00daf3',
    gold:       '#ffe16d',
    goldDim:    '#e9c400',
    primaryFix: '#9cf0ff',
    outline:    '#849396',
    surface:    '#202020',
    surfaceHi:  '#2a2a2a',
    error:      '#ffb4ab',
    tertiary:   '#f0ecec',
};

const PARTY_COLORS = {
    TVK:      '#00daf3',   // cyan  – new party
    DMK:      '#ffe16d',   // gold
    ADMK:     '#ffb4ab',   // error/red
    INC:      '#96CEB4',
    BJP:      '#f4a261',
    NTK:      '#e76f51',
    VCK:      '#bc6c25',
    DMDK:     '#c9ada7',
    PMK:      '#a8dadc',
    CPI:      '#457b9d',
    'CPI(M)': '#1d3557',
    IUML:     '#2a9d8f',
    AMMK:     '#e9c46a',
    Other:    '#849396',
    NOTA:     '#555555',
};

function partyColor(name, fallbackIdx = 0) {
    if (PARTY_COLORS[name]) return PARTY_COLORS[name];
    const palette = Object.values(PARTY_COLORS);
    return palette[fallbackIdx % palette.length];
}

// Shared Chart.js defaults for the dark theme
const CHART_DEFAULTS = {
    color: '#bac9cc',
    borderColor: '#3b494c',
    plugins: {
        legend: { labels: { color: '#bac9cc', font: { family: 'JetBrains Mono', size: 11 } } },
        tooltip: {
            backgroundColor: '#202020',
            borderColor: '#3b494c',
            borderWidth: 1,
            titleColor: '#ffe16d',
            bodyColor: '#e5e2e1',
        }
    },
    scales: {
        x: { ticks: { color: '#849396' }, grid: { color: 'rgba(59,73,76,0.4)' } },
        y: { ticks: { color: '#849396' }, grid: { color: 'rgba(59,73,76,0.4)' } }
    }
};

// Active chart instances (so we can destroy before re-create)
const chartInstances = {};

function destroyChart(id) {
    if (chartInstances[id]) {
        chartInstances[id].destroy();
        delete chartInstances[id];
    }
}

// ── Helper: get canvas context safely ────────────────────────────────────────
function ctx(id) {
    const el = document.getElementById(id);
    return el ? el.getContext('2d') : null;
}

// ────────────────────────────────────────────────────────────────────────────
// INDEX PAGE CHARTS
// ────────────────────────────────────────────────────────────────────────────

/**
 * Updates the SVG donut ring on index.html with real seat counts from data.
 *
 * The HTML has two <circle> elements:
 *   #ring-np  – New Party (TVK / NEW alliance)
 *   #ring-dmx – DM-X Alliance
 *
 * SVG circle circumference for r=45 → 2π×45 ≈ 282.74
 */
function updateIndexDonutRing() {
    const TOTAL = stats.totalSeats || 234;
    const CIRC  = 2 * Math.PI * 45; // ≈ 282.74

    const npSeats  = stats.seats2026['TVK'] || 108;
    const dmxSeats = (stats.seats2026['DMK'] || 59)
                   + (stats.seats2026['INC'] || 5)
                   + (stats.seats2026['VCK'] || 2)
                   + (stats.seats2026['CPI'] || 2)
                   + (stats.seats2026['CPI(M)'] || 2)
                   + (stats.seats2026['IUML'] || 2)
                   + (stats.seats2026['DMMK'] || 1);
    
    const admkSeats = (stats.seats2026['ADMK'] || 47)+
                      (stats.seats2026['BJP']  || 1) +
                      (stats.seats2026['PMK']  || 4) +
                      (stats.seats2026['AMMK'] || 1);

    const npArc  = ((npSeats  / TOTAL) * CIRC).toFixed(1);
    const dmxArc = ((dmxSeats / TOTAL) * CIRC).toFixed(1);
    const adyArc = ((admkSeats / TOTAL) * CIRC).toFixed(1);

    // Update SVG arcs
    const ringNP  = document.getElementById('ring-np');
    const ringDMX = document.getElementById('ring-dmx');
    const ringADY = document.getElementById('ring-ady');
    if (ringNP)  ringNP.setAttribute('stroke-dasharray',  `${npArc} ${CIRC}`);
    if (ringDMX) {
        ringDMX.setAttribute('stroke-dasharray',  `${dmxArc} ${CIRC}`);
        ringDMX.setAttribute('stroke-dashoffset', `-${npArc}`);
    }
    if (ringADY) {
        ringADY.setAttribute('stroke-dasharray',  `${adyArc} ${CIRC}`);
        ringADY.setAttribute('stroke-dashoffset', `-${npArc} ${dmxArc}`);
    }

    // Update the legend numbers below the ring
    setText('ring-label-np',  npSeats);
    setText('ring-label-dmx', dmxSeats);
    setText('ring-label-ad-y', admkSeats);
    const others = TOTAL - npSeats - dmxSeats - admkSeats;
    setText('ring-label-ady', others > 0 ? others : 0);

    // Update the centre label
    setText('ring-total', TOTAL);
}

/**
 * Populates the "Critical Constituency Shifts" table on index.html.
 * Picks the top 8 seats by highest margin to surface dramatic results.
 */
function buildIndexShiftsTable() {
    const tbody = document.getElementById('index-shifts-tbody');
    if (!tbody) return;

    // Sort by margin descending, take top 8
    const sorted = [...electionData.results2026]
        .filter(r => parseInt(r['Margin']) > 0)
        .sort((a, b) => parseInt(b['Margin']) - parseInt(a['Margin']))
        .slice(0, 8);

    tbody.innerHTML = sorted.map(row => {
        const constituency  = row['Constituency']       || '—';
        const winner        = row['Leading Candidate']  || '—';
        const winnerParty   = shortPartyName(row['Leading Party']);
        const trailingParty = shortPartyName(row['Trailing Party']);
        const margin        = formatNumber(row['Margin'] || 0);

        const isNP     = winnerParty === 'TVK';
        const partyCol = isNP ? 'text-primary-fixed' : 'text-secondary-fixed';
        const badge    = isNP
            ? `<span class="px-2 py-1 rounded bg-primary-fixed/10 text-primary-fixed text-[10px] font-bold">FLIPPED</span>`
            : `<span class="px-2 py-1 rounded bg-secondary-fixed/10 text-secondary-fixed text-[10px] font-bold">RETAINED</span>`;

        return `<tr class="zebra-row hover:bg-surface-container transition-colors">
            <td class="px-6 py-4 font-semibold text-on-surface">${constituency}</td>
            <td class="px-6 py-4 text-on-surface-variant">${trailingParty}</td>
            <td class="px-6 py-4 ${partyCol}">${winner} (${winnerParty})</td>
            <td class="px-6 py-4 text-primary-fixed-dim">${margin}</td>
            <td class="px-6 py-4">${badge}</td>
        </tr>`;
    }).join('');
}

/** Update the three metric cards on index.html */
function updateIndexMetricCards() {
    // TVK vote share from party_vote_share.csv
    const tvk = stats.partyVoteArray.find(p => p.name === 'TVK');
    if (tvk) setText('card-aggregate-swing', `+${tvk.pct.toFixed(1)}`);
}

// ────────────────────────────────────────────────────────────────────────────
// SWING ANALYSIS PAGE CHARTS
// ────────────────────────────────────────────────────────────────────────────

/**
 * Populates the Vote Share Churn progress bars on swing_analysis.html.
 * Targets the three .churn-bar elements by their data-alliance attribute.
 */
function updateSwingChurnBars() {
    // New Party (TVK alone or all NEW alliance)
    const tvkRow = stats.partyVoteArray.find(p => p.name === 'TVK');
    const dmkRow = stats.partyVoteArray.find(p => p.name === 'DMK');
    const admkRow = stats.partyVoteArray.find(p => p.name === 'ADMK');

    if (!tvkRow) return;

    setWidth('churn-bar-np',   `${tvkRow.pct}%`);
    setWidth('churn-bar-dmx',  dmkRow  ? `${dmkRow.pct}%`  : '0%');
    setWidth('churn-bar-ady',  admkRow ? `${admkRow.pct}%` : '0%');

    setText('churn-pct-np',  `${tvkRow.pct.toFixed(1)}%`);
    setText('churn-pct-dmx', dmkRow  ? `${dmkRow.pct.toFixed(1)}%`  : '—');
    setText('churn-pct-ady', admkRow ? `${admkRow.pct.toFixed(1)}%` : '—');
}

/**
 * Seat transition matrix table on swing_analysis.html.
 * Fills in the dynamic <tbody id="swing-matrix-tbody">.
 */
function updateSwingMatrix() {
    const tbody = document.getElementById('swing-matrix-tbody');
    if (!tbody) return;

    const s26 = stats.seats2026;
    const s21 = stats.seats2021;

    // Group into alliances
    const rows = [
        {
            label: 'DMK+ Alliance',
            color: 'text-secondary-fixed',
            old: (s21['DMK'] || 0) + (s21['INC'] || 0) + (s21['CPI'] || 0) + (s21['CPI(M)'] || 0),
            new26: (s26['DMK'] || 0) + (s26['INC'] || 0) + (s26['CPI'] || 0) + (s26['CPI(M)'] || 0)
        },
        {
            label: 'AIADMK+ Alliance',
            color: 'text-error',
            old: (s21['ADMK'] || 0) + (s21['PMK'] || 0) + (s21['BJP'] || 0),
            new26: (s26['ADMK'] || 0) + (s26['PMK'] || 0) + (s26['BJP'] || 0)
        },
        {
            label: 'TVK (New Party)',
            color: 'text-primary-fixed-dim',
            old: 0,
            new26: s26['TVK'] || 0
        },
        {
            label: 'Others',
            color: 'text-on-surface-variant',
            old: (s21['VCK'] || 0) + (s21['IUML'] || 0) + (s21['MNM'] || 0) + (s21['AMMK'] || 0),
            new26: (s26['VCK'] || 0) + (s26['IUML'] || 0) + (s26['NTK'] || 0) + (s26['AMMK'] || 0) + (s26['DMDK'] || 0)
        }
    ];

    tbody.innerHTML = rows.map(r => {
        const change   = r.new26 - r.old;
        const swingPct = r.old > 0 ? ((change / r.old) * 100).toFixed(1) : '+100';
        const swingCol = change >= 0 ? 'text-primary-fixed-dim' : 'text-error';
        const lostToNP = r.label.startsWith('AIADMK') || r.label.startsWith('DMK')
            ? Math.max(0, r.old - r.new26) : '—';

        return `<tr class="hover:bg-white/[0.02] transition-colors">
            <td class="py-5 font-title-lg text-title-lg ${r.color}">${r.label}</td>
            <td class="py-5 text-on-surface-variant font-label-md">${r.old}</td>
            <td class="py-5 text-primary-fixed-dim font-label-md">${lostToNP}</td>
            <td class="py-5 text-on-surface-variant font-label-md">—</td>
            <td class="py-5 font-title-lg text-title-lg text-on-surface">${r.new26}</td>
            <td class="py-5 ${swingCol} font-label-md">${change >= 0 ? '+' : ''}${swingPct}%</td>
        </tr>`;
    }).join('');
}

/**
 * Builds the vote-share bar chart on swing_analysis.html using Chart.js.
 * Canvas ID: swingVoteShareChart
 */
function buildSwingVoteShareChart() {
    const c = ctx('swingVoteShareChart');
    if (!c) return;
    destroyChart('swingVoteShareChart');

    const top8 = stats.partyVoteArray.slice(0, 8);

    chartInstances['swingVoteShareChart'] = new Chart(c, {
        type: 'bar',
        data: {
            labels: top8.map(p => p.name),
            datasets: [{
                label: 'Vote Share %',
                data:  top8.map(p => p.pct),
                backgroundColor: top8.map((p, i) => partyColor(p.name, i)),
                borderRadius: 2,
                borderSkipped: false,
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: CHART_DEFAULTS.plugins.tooltip
            },
            scales: {
                x: {
                    beginAtZero: true,
                    max: 40,
                    ticks: { color: '#849396', callback: v => `${v}%` },
                    grid: { color: 'rgba(59,73,76,0.4)' }
                },
                y: {
                    ticks: { color: '#bac9cc', font: { family: 'JetBrains Mono', size: 11 } },
                    grid: { display: false }
                }
            }
        }
    });
}

// ────────────────────────────────────────────────────────────────────────────
// DEMOGRAPHIC PAGE CHARTS
// ────────────────────────────────────────────────────────────────────────────

/**
 * The demographic page uses CSS-driven bar elements with inline height styles.
 * This function animates them in by triggering a height transition.
 * Bar elements have class .demo-bar-2026 or .demo-bar-2021.
 */
function animateDemoBars() {
    document.querySelectorAll('[data-bar-height]').forEach((el, i) => {
        const target = el.dataset.barHeight;
        el.style.height = '0%';
        setTimeout(() => {
            el.style.transition = 'height 1.2s cubic-bezier(0.22, 1, 0.36, 1)';
            el.style.height = target;
        }, 100 + i * 80);
    });
}

/**
 * Builds a grouped bar chart for vote share by party on the demographic page.
 * Canvas ID: demoPartyVoteChart
 */
function buildDemoPartyVoteChart() {
    const c = ctx('demoPartyVoteChart');
    if (!c) return;
    destroyChart('demoPartyVoteChart');

    const top6 = stats.partyVoteArray.slice(0, 6);

    chartInstances['demoPartyVoteChart'] = new Chart(c, {
        type: 'doughnut',
        data: {
            labels: top6.map(p => p.name),
            datasets: [{
                data: top6.map(p => p.pct),
                backgroundColor: top6.map((p, i) => partyColor(p.name, i)),
                borderColor: '#202020',
                borderWidth: 3,
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#bac9cc',
                        font: { family: 'JetBrains Mono', size: 10 },
                        boxWidth: 12,
                        padding: 12
                    }
                },
                tooltip: {
                    ...CHART_DEFAULTS.plugins.tooltip,
                    callbacks: {
                        label: ctx => ` ${ctx.label}: ${ctx.parsed.toFixed(2)}%`
                    }
                }
            }
        }
    });
}

// ────────────────────────────────────────────────────────────────────────────
// REGIONAL PAGE CHARTS
// ────────────────────────────────────────────────────────────────────────────

/**
 * Updates the right-panel region breakdown stats on regional.html
 * using real aggregate data derived from constituency-level results.
 *
 * Tamil Nadu constituencies are loosely grouped into North / South / West
 * based on Constituency No. ranges defined by the ECI district order.
 */
function updateRegionalPanel() {
    // Build region summary from real 2026 results
    const regions = buildRegionSummary();

    // North TN  (constituency nos roughly 1–60)
    updateRegionCard('region-north', regions.north);
    // West TN   (roughly 121–180)
    updateRegionCard('region-west',  regions.west);
    // South TN  (roughly 181–234)
    updateRegionCard('region-south', regions.south);

    // Update totals in the floating legend
    setText('regional-total-seats',    stats.totalSeats);
    setText('regional-declared-seats', stats.totalSeats); // all declared in final results
    setText('regional-pending-seats',  0);
}

function buildRegionSummary() {
    const north = { tvk: 0, others: 0, margins: [] };
    const west  = { tvk: 0, others: 0, margins: [] };
    const south = { tvk: 0, others: 0, margins: [] };

    electionData.results2026.forEach(row => {
        const no     = parseInt(row['Constituency No.']) || 0;
        const winner = shortPartyName(row['Leading Party']);
        const margin = parseInt(row['Margin']) || 0;

        let bucket;
        if      (no >= 1   && no <= 60)  bucket = north;
        else if (no >= 121 && no <= 180) bucket = west;
        else if (no >= 181 && no <= 234) bucket = south;
        else return;

        if (winner === 'TVK') bucket.tvk++;
        else                  bucket.others++;
        bucket.margins.push(margin);
    });

    return {
        north: summarise(north),
        west:  summarise(west),
        south: summarise(south)
    };
}

function summarise(bucket) {
    const total = bucket.tvk + bucket.others;
    const avgM  = bucket.margins.length
        ? Math.round(bucket.margins.reduce((a, b) => a + b, 0) / bucket.margins.length)
        : 0;
    const npPct = total ? Math.round((bucket.tvk / total) * 100) : 0;
    return { total, npPct, avgMargin: avgM };
}

function updateRegionCard(id, summary) {
    setText(`${id}-leading-pct`, `${summary.npPct}%`);
    setText(`${id}-margin`,      `+${Math.round(summary.avgMargin / 1000)}k`);
    setWidth(`${id}-np-bar`,     `${summary.npPct}%`);
    setWidth(`${id}-opp-bar`,    `${100 - summary.npPct}%`);
}

// ────────────────────────────────────────────────────────────────────────────
// COALITION PAGE CHARTS
// ────────────────────────────────────────────────────────────────────────────

/**
 * Updates the three strike-rate progress bars on coalition.html using real data.
 * The bars already exist in the HTML; we just update widths and labels.
 */
function updateCoalitionStrikeBars() {
    const s = stats.seats2026;

    // DM-X Alliance (DMK + INC + VCK + CPI + CPI(M) + IUML)
    const dmxWon = (s['DMK'] || 0) + (s['INC'] || 0) + (s['VCK'] || 0)
                 + (s['CPI'] || 0) + (s['CPI(M)'] || 0) + (s['IUML'] || 0);
    const dmxContested = 184;  // as displayed in the original HTML
    const dmxRate = ((dmxWon / dmxContested) * 100).toFixed(1);

    // AD-Y Alliance (ADMK + BJP + PMK + DMDK + AMMK)
    const adyWon = (s['ADMK'] || 0) + (s['BJP'] || 0) + (s['PMK'] || 0)
                 + (s['DMDK'] || 0) + (s['AMMK'] || 0);
    const adyContested = 148;
    const adyRate = ((adyWon / adyContested) * 100).toFixed(1);

    // New Alliance (TVK + NTK)
    const newWon = (s['TVK'] || 0) + (s['NTK'] || 0);
    const newContested = 80;
    const newRate = ((newWon / newContested) * 100).toFixed(1);

    // Update bars
    setWidth('coalition-bar-dmx', `${dmxRate}%`);
    setWidth('coalition-bar-ady', `${adyRate}%`);
    setWidth('coalition-bar-new', `${newRate}%`);

    setText('coalition-rate-dmx',    `${dmxRate}% Strike Rate`);
    setText('coalition-rate-ady',    `${adyRate}% Strike Rate`);
    setText('coalition-rate-new',    `${newRate}% Strike Rate`);
    setText('coalition-seats-dmx',   `${dmxWon}/${dmxContested} Seats`);
    setText('coalition-seats-ady',   `${adyWon}/${adyContested} Seats`);
    setText('coalition-seats-new',   `${newWon}/${newContested} Seats`);
}

/**
 * Builds the Vote Share Migration grouped bar chart on coalition.html.
 * Canvas ID: coalitionMigrationChart
 */
function buildCoalitionMigrationChart() {
    const c = ctx('coalitionMigrationChart');
    if (!c) return;
    destroyChart('coalitionMigrationChart');

    // 2021 vote shares (approx, from known results)
    const data2021 = [38.2, 32.1, 0];
    // 2026 vote shares from actual data (DMK+INC vs ADMK+BJP vs TVK+NTK)
    const dmkPct  = (stats.partyVoteArray.find(p => p.name === 'DMK')?.pct || 0)
                  + (stats.partyVoteArray.find(p => p.name === 'INC')?.pct || 0);
    const admkPct = (stats.partyVoteArray.find(p => p.name === 'ADMK')?.pct || 0)
                  + (stats.partyVoteArray.find(p => p.name === 'BJP')?.pct  || 0);
    const tvkPct  = (stats.partyVoteArray.find(p => p.name === 'TVK')?.pct || 0)
                  + (stats.partyVoteArray.find(p => p.name === 'NTK')?.pct  || 0);
    const data2026 = [+dmkPct.toFixed(2), +admkPct.toFixed(2), +tvkPct.toFixed(2)];

    chartInstances['coalitionMigrationChart'] = new Chart(c, {
        type: 'bar',
        data: {
            labels: ['DM-X Alliance', 'AD-Y Alliance', 'New Alliance'],
            datasets: [
                {
                    label: '2021 Vote Share %',
                    data: data2021,
                    backgroundColor: 'rgba(0,218,243,0.25)',
                    borderColor: COLORS.cyan,
                    borderWidth: 1,
                    borderRadius: 2
                },
                {
                    label: '2026 Vote Share %',
                    data: data2026,
                    backgroundColor: [COLORS.cyan, COLORS.gold, COLORS.tertiary],
                    borderColor: [COLORS.cyan, COLORS.gold, COLORS.tertiary],
                    borderWidth: 1,
                    borderRadius: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#bac9cc',
                        font: { family: 'JetBrains Mono', size: 10 }
                    }
                },
                tooltip: CHART_DEFAULTS.plugins.tooltip
            },
            scales: {
                x: {
                    ticks: { color: '#bac9cc' },
                    grid: { color: 'rgba(59,73,76,0.4)' }
                },
                y: {
                    beginAtZero: true,
                    max: 50,
                    ticks: { color: '#849396', callback: v => `${v}%` },
                    grid: { color: 'rgba(59,73,76,0.4)' }
                }
            }
        }
    });
}

/**
 * Fills the Partner Efficiency Matrix table on coalition.html.
 * Targets <tbody id="coalition-partner-tbody">.
 */
function buildCoalitionPartnerTable() {
    const tbody = document.getElementById('coalition-partner-tbody');
    if (!tbody) return;

    const s = stats.seats2026;

    const partners = [
        { name: 'DMK Core',   alliance: 'DM-X', allianceCol: 'text-primary-fixed-dim', contested: 135, won: s['DMK']  || 0, prev: 85.1  },
        { name: 'INC',        alliance: 'DM-X', allianceCol: 'text-primary-fixed-dim', contested: 25,  won: s['INC']  || 0, prev: 70.6  },
        { name: 'AIADMK',     alliance: 'AD-Y', allianceCol: 'text-secondary-fixed-dim', contested: 120, won: s['ADMK'] || 0, prev: 54.1 },
        { name: 'BJP',        alliance: 'AD-Y', allianceCol: 'text-secondary-fixed-dim', contested: 20,  won: s['BJP']  || 0, prev: 45.5 },
        { name: 'TVK',        alliance: 'NEW',  allianceCol: 'text-tertiary',           contested: 60,  won: s['TVK']  || 0, prev: null  },
        { name: 'NTK',        alliance: 'NEW',  allianceCol: 'text-tertiary',           contested: 20,  won: s['NTK']  || 0, prev: null  },
    ];

    tbody.innerHTML = partners.map(p => {
        const rate    = ((p.won / p.contested) * 100).toFixed(1);
        const trendPct = p.prev !== null
            ? (parseFloat(rate) - p.prev).toFixed(1)
            : null;
        const trendHTML = trendPct !== null
            ? `<span class="${parseFloat(trendPct) >= 0 ? 'text-primary-fixed-dim' : 'text-error'} font-label-md">
                ${parseFloat(trendPct) >= 0 ? '▲' : '▼'} ${Math.abs(trendPct)}%
               </span>`
            : `<span class="text-on-surface-variant font-label-md">NEW</span>`;

        return `<tr>
            <td class="px-6 py-4 font-bold text-on-surface">${p.name}</td>
            <td class="px-6 py-4 text-center"><span class="${p.allianceCol}">${p.alliance}</span></td>
            <td class="px-6 py-4 text-center text-on-surface-variant">${p.contested}</td>
            <td class="px-6 py-4 text-center text-on-surface-variant">${p.won}</td>
            <td class="px-6 py-4 text-center font-label-md text-on-surface">${rate}%</td>
            <td class="px-6 py-4 text-right">${trendHTML}</td>
        </tr>`;
    }).join('');
}

// ────────────────────────────────────────────────────────────────────────────
// UTILITY DOM HELPERS
// ────────────────────────────────────────────────────────────────────────────

function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

function setWidth(id, value) {
    const el = document.getElementById(id);
    if (el) el.style.width = value;
}
