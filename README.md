# TN26 ELECTION ANALYSIS

## Project Overview

This project analyzes Tamil Nadu election data for 2026 and compares it with the 2021 state assembly election. It includes scraping utilities, cleaned election datasets, and exploratory analysis notes.

The repository is organized to support:
- raw election data acquisition from official election websites and Wikipedia
- data cleaning and party seat/vote share analysis
- exploratory analysis through Jupyter notebooks
- lessons learned about scraping, fuzzy matching, and pandas aggregation

## Directory Structure

- `data/`
  - `party_vote_share.csv` — party vote share data scraped from the official 2026 election results page
  - `results_2026.csv` — raw constituency-level 2026 result records scraped from the Election Commission of India site
  - `tn21_election_results.csv` — 2021 Tamil Nadu election results scraped from Wikipedia for historical comparison

- `NoteBook/`
  - `eda.ipynb` — exploratory data analysis notebook for investigating the election results

- `Scraping_data/`
  - `tn26_data_scrape.py` — scraper for 2021 and 2026 Tamil Nadu election data, using the Wikipedia API and ECI result pages
  - `tn21_data.py` — historical data scraping and parsing helper for the 2021 Tamil Nadu assembly election
  - `tn26_party-wise-vote-share.py` — (currently empty) placeholder for party vote share scraping logic

- `script/`
  - Empty folder reserved for analysis or utility scripts not yet added to the repository.

## Key Components

### `Scraping_data/tn26_data_scrape.py`

This script contains scraping logic for:
- extracting constituency result data from ECI 2026 result pages
- parsing party vote share data from the ECI summary page
- using Python `requests`, `BeautifulSoup`, and regex to collect embedded JavaScript chart data
- storing the final cleaned output CSV files in `data/`

### `Scraping_data/tn21_data.py`

This script demonstrates scraping the 2021 Tamil Nadu Legislative Assembly election results from Wikipedia using the MediaWiki API. It uses:
- the `requests` library to call `action=parse`
- `BeautifulSoup` to parse HTML returned inside JSON
- table extraction logic to save cleaned 2021 results as CSV

### `NoteBook/learning.md` and `Scraping_data/learn.md`

These notes document:
- efficient pandas aggregation techniques for counting party seats
- Python set operations for comparing constituency name lists
- the use of `rapidfuzz` for fuzzy string matching when dataset values differ slightly
- strategies for reading Wikipedia content reliably using the API instead of raw page HTML

## How to Use

1. Install required packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

2. Run the scraper(s) to refresh the datasets:

```bash
python "Scraping_data\tn26_data_scrape.py"
```

3. Open `NoteBook/eda.ipynb` to explore the cleaned datasets and perform analysis.

## Live Dashboard Outlook

A Streamlit version of the TN26 analytics dashboard is available at:

https://tn26-election-analysis.streamlit.app/

The live dashboard presents:
- an executive overview of total turnout, declared seats, and swing metrics
- interactive vote share and seat distribution visualizations
- swing analysis comparing 2026 results with 2021 baselines
- demographic and regional performance summaries
- coalition and alliance impact metrics

This README should be updated with the live app link and the current dashboard outlook whenever the Streamlit deployment changes.

## Notes and Limitations

- The `script/` folder is currently empty and can be used for future analysis scripts.
- The scraping scripts assume stable table structure on the ECI and Wikipedia pages; changes on the source websites may require updates.
- `tn26_party-wise-vote-share.py` is currently a placeholder; the vote share scraping logic is implemented in `tn26_data_scrape.py`.

## Future Improvements

Possible next steps for the project include:
- adding a dedicated analysis script in `script/` for automated seat projections and turnout comparisons
- improving the 2026 constituency scraper with more robust error handling and retry logic
- linking 2021 and 2026 constituencies using fuzzy matching to compare party performance over time
- adding visualization notebooks for vote share, party dominance, and regional trends

---

This README summarizes the current TN26 election analysis repository and provides a starting point for future data-driven work on Tamil Nadu election forecasting and review.