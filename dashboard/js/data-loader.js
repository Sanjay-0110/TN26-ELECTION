// ===================================
// data-loader.js
// ===================================
// Handles loading CSV files from backend
// Parses data and stores in global variables

let electionData = {
    partyVotes: [],
    results2026: [],
    results2021: []
};

// Load CSV from Python backend (Flask/FastAPI)
// The Python backend serves CSV files
async function loadCSVFromServer(filename) {
    try {
        // Option 1: Load from local data folder (if served as static files)
        const response = await fetch(`../data/${filename}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const csvText = await response.text();
        return csvText;
    } catch (error) {
        console.error(`Error loading ${filename}:`, error);
        return null;
    }
}

// Parse CSV string to JSON array
function parseCSV(csvText) {
    return Papa.parse(csvText, {
        header: true,
        skipEmptyLines: true,
        dynamicTyping: false
    }).data;
}

// Load all election data
async function loadAllData() {
    console.log('📥 Loading election data...');
    
    try {
        // Load party vote share
        const partyCSV = await loadCSVFromServer('party_vote_share.csv');
        if (partyCSV) {
            electionData.partyVotes = parseCSV(partyCSV);
            console.log('✓ Party votes loaded:', electionData.partyVotes.length, 'parties');
        }

        // Load 2026 results
        const results2026CSV = await loadCSVFromServer('results_2026.csv');
        if (results2026CSV) {
            electionData.results2026 = parseCSV(results2026CSV);
            console.log('✓ 2026 results loaded:', electionData.results2026.length, 'constituencies');
        }

        // Load 2021 results (for comparison)
        const results2021CSV = await loadCSVFromServer('tn21_election_results.csv');
        if (results2021CSV) {
            electionData.results2021 = parseCSV(results2021CSV);
            console.log('✓ 2021 results loaded:', electionData.results2021.length, 'constituencies');
        }

        console.log('✓ All data loaded successfully!');
        return true;
    } catch (error) {
        console.error('✗ Error loading data:', error);
        return false;
    }
}

// Clean and normalize party names
function cleanPartyName(partyString) {
    if (!partyString) return 'Unknown';
    // Remove extra text like "Party Wise State Trends..."
    return partyString.split('\n')[0].trim();
}

// Get unique parties from results
function getUniqueParties() {
    const parties = new Set();
    electionData.results2026.forEach(row => {
        parties.add(cleanPartyName(row['Leading Party']));
        parties.add(cleanPartyName(row['Trailing Party']));
    });
    return Array.from(parties).sort();
}

// Get unique constituencies
function getUniqueConstituencies() {
    return electionData.results2026.map(row => row['Constituency']).filter((v, i, a) => a.indexOf(v) === i);
}

// Parse vote count from string (e.g., "TVK{34.92%},17226209" -> 17226209)
function parseVoteCount(voteString) {
    if (!voteString) return 0;
    const numbers = voteString.match(/(\d+)/g);
    if (numbers) {
        // Last number is usually the vote count
        return parseInt(numbers[numbers.length - 1]);
    }
    return 0;
}

// Parse vote percentage from string
function parsePercentage(voteString) {
    if (!voteString) return 0;
    const match = voteString.match(/(\d+\.?\d*?)%/);
    if (match) {
        return parseFloat(match[1]);
    }
    return 0;
}

// Convert vote string to clean object
function parsePartyVoteData(row) {
    const partyField = row['Party'];
    const voteField = row['Vote Share'];
    
    return {
        party: partyField ? partyField.replace(/[{}]/g, '').split('{')[0].trim() : 'Unknown',
        percentage: parsePercentage(partyField),
        votes: parseVoteCount(voteField)
    };
}

// Initialize data and start dashboard
async function init() {
    const success = await loadAllData();
    if (success) {
        initDashboard();
    } else {
        document.getElementById('tableBody').innerHTML = '<tr><td colspan="5">Error loading data. Check console.</td></tr>';
    }
}

// Start when DOM is loaded
document.addEventListener('DOMContentLoaded', init);
