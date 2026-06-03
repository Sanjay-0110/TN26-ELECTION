// ===================================
// stats-calculator.js
// ===================================
// Calculates statistics from election data

let stats = {};

// Calculate total votes
function calculateTotalVotes() {
    let total = 0;
    electionData.partyVotes.forEach(row => {
        const voteCount = parseVoteCount(row['Vote Share']);
        total += voteCount;
    });
    return total;
}

// Calculate total constituencies
function calculateTotalConstituencies() {
    return new Set(electionData.results2026.map(row => row['Constituency'])).size;
}

// Find leading party
function findLeadingParty() {
    if (electionData.partyVotes.length === 0) return 'N/A';
    
    let leadingParty = electionData.partyVotes[0];
    let maxVotes = parseVoteCount(leadingParty['Vote Share']);
    
    electionData.partyVotes.forEach(row => {
        const votes = parseVoteCount(row['Vote Share']);
        if (votes > maxVotes) {
            maxVotes = votes;
            leadingParty = row;
        }
    });
    
    return leadingParty['Party'].split('{')[0].trim();
}

// Find highest margin
function findHighestMargin() {
    let maxMargin = 0;
    
    electionData.results2026.forEach(row => {
        const margin = parseInt(row['Margin']) || 0;
        if (margin > maxMargin) {
            maxMargin = margin;
        }
    });
    
    return maxMargin;
}

// Calculate vote share by party
function calculateVoteShareByParty() {
    const voteShare = {};
    
    electionData.partyVotes.forEach(row => {
        const party = row['Party'].split('{')[0].trim();
        const percentage = parsePercentage(row['Party']);
        const votes = parseVoteCount(row['Vote Share']);
        
        voteShare[party] = {
            percentage: percentage,
            votes: votes,
            label: party
        };
    });
    
    return voteShare;
}

// Calculate seats won by party
function calculateSeatsByParty() {
    const seats = {};
    
    electionData.results2026.forEach(row => {
        const party = cleanPartyName(row['Leading Party']);
        if (!seats[party]) {
            seats[party] = 0;
        }
        seats[party]++;
    });
    
    return seats;
}

// Calculate average margin by party
function calculateAverageMarginByParty() {
    const margins = {};
    const counts = {};
    
    electionData.results2026.forEach(row => {
        const party = cleanPartyName(row['Leading Party']);
        const margin = parseInt(row['Margin']) || 0;
        
        if (!margins[party]) {
            margins[party] = 0;
            counts[party] = 0;
        }
        margins[party] += margin;
        counts[party]++;
    });
    
    const avgMargins = {};
    for (let party in margins) {
        avgMargins[party] = (margins[party] / counts[party]).toFixed(0);
    }
    
    return avgMargins;
}

// Calculate party performance (2021 vs 2026)
function comparePartyPerformance() {
    const comparison = {};
    
    // Get 2026 data
    const seats2026 = calculateSeatsByParty();
    
    // Count seats from 2021 data if available
    const seats2021 = {};
    electionData.results2021.forEach(row => {
        const party = cleanPartyName(row['Leading Party'] || row['Winner Party']);
        if (!seats2021[party]) {
            seats2021[party] = 0;
        }
        seats2021[party]++;
    });
    
    // Build comparison
    const allParties = new Set([...Object.keys(seats2026), ...Object.keys(seats2021)]);
    allParties.forEach(party => {
        comparison[party] = {
            '2021': seats2021[party] || 0,
            '2026': seats2026[party] || 0,
            'change': (seats2026[party] || 0) - (seats2021[party] || 0)
        };
    });
    
    return comparison;
}

// Calculate number of close races
function countCloseRaces(data, threshold = 5000) {
    if (!Array.isArray(data)) {
        return 0;
    }
    return data.reduce((count, row) => {
        const margin = parseInt(row['Margin']) || 0;
        return count + (margin > 0 && margin <= threshold ? 1 : 0);
    }, 0);
}

// Calculate statistics
function calculateStats() {
    stats = {
        totalVotes: calculateTotalVotes(),
        totalConstituencies: calculateTotalConstituencies(),
        leadingParty: findLeadingParty(),
        highestMargin: findHighestMargin(),
        voteShareByParty: calculateVoteShareByParty(),
        seatsByParty: calculateSeatsByParty(),
        avgMarginByParty: calculateAverageMarginByParty(),
        partyComparison: comparePartyPerformance()
    };
    
    console.log('📊 Statistics calculated:', stats);
    return stats;
}

// Format number with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// Format percentage
function formatPercentage(num) {
    return (num || 0).toFixed(2) + '%';
}
