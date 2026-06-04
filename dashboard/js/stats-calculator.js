// ===================================
// stats-calculator.js
// ===================================
// Computes all derived statistics from the loaded CSVs.
// Must be loaded AFTER data-loader.js.

let stats = {};

// ── Seat counts ──────────────────────────────────────────────────────────────

/**
 * Count seats won by each *short* party name from results_2026.csv.
 * Returns { TVK: 108, DMK: 59, ADMK: 47, … }
 */
function calculateSeatsByParty2026() {
    const seats = {};
    electionData.results2026.forEach(row => {
        const p = shortPartyName(row['Leading Party']);
        seats[p] = (seats[p] || 0) + 1;
    });
    return seats;
}

/**
 * Count seats won by each party from tn21_election_results.csv.
 * The 2021 CSV has a column called "Party" for the winning candidate's party.
 */
function calculateSeatsByParty2021() {
    const seats = {};
    electionData.results2021.forEach(row => {
        const p = (row['Party'] || '').trim();
        if (p) seats[p] = (seats[p] || 0) + 1;
    });
    return seats;
}

// ── Vote totals ──────────────────────────────────────────────────────────────

function calculateTotalVotes() {
    return electionData.partyVotes.reduce((sum, row) => {
        return sum + parseVoteCount(row['Vote Share']);
    }, 0);
}

// ── Party vote share array (sorted by votes desc) ───────────────────────────

function buildPartyVoteArray() {
    return electionData.partyVotes.map(row => ({
        name:    row['Party'].split('{')[0].trim(),
        pct:     parsePercentage(row['Party']),
        votes:   parseVoteCount(row['Vote Share'])
    })).sort((a, b) => b.votes - a.votes);
}

// ── Margin stats ─────────────────────────────────────────────────────────────

function findHighestMargin() {
    return electionData.results2026.reduce((max, row) => {
        const m = parseInt(row['Margin']) || 0;
        return m > max ? m : max;
    }, 0);
}

function countCloseRaces(threshold = 5000) {
    return electionData.results2026.filter(row => {
        const m = parseInt(row['Margin']) || 0;
        return m > 0 && m <= threshold;
    }).length;
}

function avgMarginByParty() {
    const sums = {}, counts = {};
    electionData.results2026.forEach(row => {
        const p = shortPartyName(row['Leading Party']);
        const m = parseInt(row['Margin']) || 0;
        sums[p]   = (sums[p]   || 0) + m;
        counts[p] = (counts[p] || 0) + 1;
    });
    const result = {};
    Object.keys(sums).forEach(p => { result[p] = Math.round(sums[p] / counts[p]); });
    return result;
}

// ── Alliance helpers (mapping to the HTML's DM-X / AD-Y / NEW labels) ────────

const ALLIANCE_MAP = {
    // DM-X Alliance
    DMK: 'DM-X', INC: 'DM-X', VCK: 'DM-X', CPI: 'DM-X', 'CPI(M)': 'DM-X',
    IUML: 'DM-X', 'CPI(ML)': 'DM-X',
    // AD-Y Alliance
    ADMK: 'AD-Y', BJP: 'AD-Y', DMDK: 'AD-Y', PMK: 'AD-Y', AMMK: 'AD-Y',
    // New Alliance (TVK-led)
    TVK: 'NEW',  NTK: 'NEW',
};

function getAlliance(shortName) {
    return ALLIANCE_MAP[shortName] || 'OTHER';
}

function seatsByAlliance(seatsObj) {
    const alliances = {};
    Object.entries(seatsObj).forEach(([p, s]) => {
        const a = getAlliance(p);
        alliances[a] = (alliances[a] || 0) + s;
    });
    return alliances;
}

// ── Master calculate ─────────────────────────────────────────────────────────

function calculateStats() {
    const seats26 = calculateSeatsByParty2026();
    const seats21 = calculateSeatsByParty2021();

    stats = {
        totalVotes:      calculateTotalVotes(),
        totalSeats:      electionData.results2026.length,
        seats2026:       seats26,
        seats2021:       seats21,
        partyVoteArray:  buildPartyVoteArray(),
        highestMargin:   findHighestMargin(),
        closeRaces:      countCloseRaces(5000),
        avgMargin:       avgMarginByParty(),
        alliance2026:    seatsByAlliance(seats26),
    };

    // Leading party by seats
    stats.leadingParty = Object.entries(seats26)
        .sort((a, b) => b[1] - a[1])[0]?.[0] ?? 'N/A';

    console.log('[stats] Calculated:', stats);
    return stats;
}
