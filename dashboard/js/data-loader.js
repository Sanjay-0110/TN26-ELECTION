// ===================================
// data-loader.js
// ===================================
// Loads and parses CSV data from the ../data/ folder.
// Exposes a global `electionData` object and an `init()` entry point.

const electionData = {
    partyVotes: [],      // parsed party_vote_share.csv
    results2026: [],     // parsed results_2026.csv
    results2021: []      // parsed tn21_election_results.csv
};

// ── CSV fetch helper ─────────────────────────────────────────────────────────
async function loadCSV(filename) {
    try {
        const res = await fetch(`../data/${filename}`);
        if (!res.ok) throw new Error(`HTTP ${res.status} for ${filename}`);
        return await res.text();
    } catch (err) {
        console.error(`[data-loader] Failed to load ${filename}:`, err);
        return null;
    }
}

// ── Minimal CSV parser (no external dependency) ──────────────────────────────
function parseCSV(text) {
    if (!text) return [];
    const lines = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n').split('\n');
    if (lines.length < 2) return [];

    // Parse header
    const headers = splitCSVLine(lines[0]);

    const rows = [];
    for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;
        const values = splitCSVLine(line);
        const row = {};
        headers.forEach((h, idx) => { row[h.trim()] = (values[idx] || '').trim(); });
        rows.push(row);
    }
    return rows;
}

function splitCSVLine(line) {
    const result = [];
    let current = '';
    let inQuotes = false;
    for (let i = 0; i < line.length; i++) {
        const ch = line[i];
        if (ch === '"') {
            inQuotes = !inQuotes;
        } else if (ch === ',' && !inQuotes) {
            result.push(current);
            current = '';
        } else {
            current += ch;
        }
    }
    result.push(current);
    return result;
}

// ── Party name helpers ───────────────────────────────────────────────────────

/**
 * Strips noise appended by the ECI scraper from the Leading/Trailing Party field.
 * e.g. "Tamilaga Vettri Kazhagam\nParty Wise State Trends…" → "Tamilaga Vettri Kazhagam"
 */
function cleanPartyName(raw) {
    if (!raw) return 'Unknown';
    return raw.split('\n')[0].split('Party Wise')[0].split('iParty')[0].trim();
}

/**
 * Maps long party names to short display labels used across the UI.
 */
const PARTY_SHORT = {
    'Tamilaga Vettri Kazhagam': 'TVK',
    'Dravida Munnetra Kazhagam': 'DMK',
    'All India Anna Dravida Munnetra Kazhagam': 'ADMK',
    'Indian National Congress': 'INC',
    'Bharatiya Janata Party': 'BJP',
    'Naam Tamilar Katchi': 'NTK',
    'Viduthalai Chiruthaigal Katchi': 'VCK',
    'Dravida Munnetra Kazhagam ': 'DMK',
    'Pattali Makkal Katchi': 'PMK',
    'Communist Party of India': 'CPI',
    'Communist Party of India  (Marxist)': 'CPI(M)',
    'Indian Union Muslim League': 'IUML',
    'Amma Makkal Munnetra Kazhagam': 'AMMK',
    'Desiya Murpokku Dravida Kazhagam': 'DMDK',
};

function shortPartyName(raw) {
    const cleaned = cleanPartyName(raw);
    return PARTY_SHORT[cleaned] || cleaned.slice(0, 8);
}

// ── Parse helpers shared by stats & chart modules ───────────────────────────

/** Extract vote count from "TVK{34.92%},17226209" → 17226209 */
function parseVoteCount(str) {
    if (!str) return 0;
    const nums = str.replace(/,/g, '').match(/(\d+)/g);
    return nums ? parseInt(nums[nums.length - 1]) : 0;
}

/** Extract percentage from "TVK{34.92%},17226209" → 34.92 */
function parsePercentage(str) {
    if (!str) return 0;
    const m = str.match(/(\d+\.?\d*)%/);
    return m ? parseFloat(m[1]) : 0;
}

/** Format a number with commas */
function formatNumber(n) {
    return Number(n).toLocaleString('en-IN');
}

// ── Main loader ──────────────────────────────────────────────────────────────
async function loadAllData() {
    console.log('[data-loader] Loading CSV files…');

    const [pvCSV, r26CSV, r21CSV] = await Promise.all([
        loadCSV('party_vote_share.csv'),
        loadCSV('results_2026.csv'),
        loadCSV('tn21_election_results.csv')
    ]);

    electionData.partyVotes  = parseCSV(pvCSV);
    electionData.results2026 = parseCSV(r26CSV);
    electionData.results2021 = parseCSV(r21CSV);

    console.log(`[data-loader] Loaded: ${electionData.partyVotes.length} parties, `
              + `${electionData.results2026.length} 2026 seats, `
              + `${electionData.results2021.length} 2021 seats`);

    return true;
}

// ── Page entry point ─────────────────────────────────────────────────────────
// Each page calls `initDashboard()` (defined in ui-controller.js).
// data-loader triggers that once data is ready.
async function init() {
    const ok = await loadAllData();
    if (ok) {
        if (typeof initDashboard === 'function') {
            initDashboard();
        } else {
            console.warn('[data-loader] initDashboard() not found on this page.');
        }
    }
}

document.addEventListener('DOMContentLoaded', init);
