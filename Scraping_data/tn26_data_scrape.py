import ast
from urllib import response
import ast # used instead of eval for safely parsing the JavaScript arrays from the HTML response
from bs4 import BeautifulSoup
from matplotlib.pyplot import table
import requests, re
import pandas as pd
import os
import json



def scrape_election_data():
    data = []
    for i in range(1, 13):
        url = f"https://results.eci.gov.in/ResultAcGenMay2026/statewiseS22{i}.htm"
        print(f"Scraping URL: {url}")

        headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        response = requests.get(url, headers=headers)
        print(response.status_code)

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')

        header_rows = table.find_all('tr')
        second_row = header_rows[1]
        headers = [th.text.strip() for th in second_row.find_all('th')]

        data_rows = table.find_all('tr')[2:]

        for row in data_rows:
            col = row.find_all('td')
            # print(f"Processing row with {len(col)} columns")
            if len(col) == 31:
                 record = {
                    'Constituency': col[0].text.strip(),
                    'Constituency No.': col[1].text.strip(),
                    'Leading Candidate': col[2].text.strip(),
                    'Leading Party': col[3].text.strip(),
                    'Trailing Candidate': col[15].text.strip(),
                    'Trailing Party': col[16].text.strip(),
                    'Margin': col[28].text.strip(),
                    'Round': col[29].text.strip(),
                    'Status': col[30].text.strip()
                }
                 data.append(record)
        
        print("Done processing rows for this URL.")
        print(f"Finished scraping {url}, total records so far: {len(data)}")

    return data

def political_party_share():
    url = "https://results.eci.gov.in/ResultAcGenMay2026/voteshareresult-S22.htm"

    headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    response = requests.get(url, headers=headers)
    print(response.status_code)

    '''The data is embedded directly in the HTML page as a JavaScript variable — no separate API call needed. 
    Just use requests.get() on that same page URL, then use regex to extract the xValues and yValues arrays 
    from the HTML response text, like this:'''

    x = re.search(r'var xValues = (\[.*?\]);', response.text).group(1)
    y = re.search(r'var yValues = (\[.*?\]);', response.text).group(1)
    
    print(x)

    parties = ast.literal_eval(x)
    votes = ast.literal_eval(y)

    vote_share = list(zip(parties, votes))
    print(vote_share)

    party_vote_share = pd.DataFrame(vote_share, columns=['Party', 'Vote Share'])
    party_vote_share.sort_values(by='Vote Share', ascending=False, inplace=True)
    print(party_vote_share.head())
    party_vote_share.to_csv("C:/Code Note/TN26 ELECTION ANALYSIS/data/party_vote_share.csv", index=False)

if __name__ == "__main__":

    # data = scrape_election_data()
    # print(f"Total records scraped: {len(data)}")

    # os.makedirs("data", exist_ok=True)
    # results_2026 = pd.DataFrame(data)
    # print(results_2026.head())
    # results_2026.to_csv("C:/Code Note/TN26 ELECTION ANALYSIS/data/results_2026.csv", index=False)
    # print(os.path.abspath("C:/Code Note/TN26 ELECTION ANALYSIS/data/results_2026.csv"))

    political_party_share()

