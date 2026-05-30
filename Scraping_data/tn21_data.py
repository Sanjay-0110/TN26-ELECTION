import ast
from urllib import response
import ast # used instead of eval for safely parsing the JavaScript arrays from the HTML response
from bs4 import BeautifulSoup
from matplotlib.pyplot import table
import requests, re
import pandas as pd
import os
import json

from sympy import pretty


def scrape_election_data():
    # data = []
    # url = "https://en.wikipedia.org/wiki/2021_Tamil_Nadu_Legislative_Assembly_election"

    # print(f"Scraping URL: {url}...")

    # headers = {
    #             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    # }
    # response = requests.get(url, headers=headers)
    # print(response.status_code)

    # soup = BeautifulSoup(response.text, 'html.parser')
    # # print(soup.prettify())

    # # tables = soup.find_all('table', {'class': 'jquery-tablesorter'})
    # # for table in tables:
    # #     print(table)

    # pretty = soup.prettify()

    # # Simple string search
    # if '<table class="wikitable sortable"' in pretty:
    #     print("true")
    #     start = pretty.index('<table class="wikitable sortable"')
    #     end = pretty.index('</table>', start) + len('</table>')
    #     table_str = pretty[start:end]
    #     print(start)
    #     print(end)
    #     print(table_str)
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "parse",
        "page": "2021_Tamil_Nadu_Legislative_Assembly_election",
        "prop": "text",
        "format": "json"
    }

    response = requests.get(url, params=params, headers=headers)

    # Safe check before parsing
    if response.status_code == 200 and response.text.strip():
        data = response.json()
        html = data["parse"]["text"]["*"]
        soup = BeautifulSoup(html, "html.parser")

        tables = soup.find_all("table", class_="wikitable")
        print(f"Found {len(tables)} wikitables")

        # Print first row of each table to identify the right one
        for i, table in enumerate(tables):
            headers_row = table.find("tr")
            print(f"Table {i}: {headers_row.get_text(strip=True)[:80]}")
        
        table = tables[18]
        rows = []
        for tr in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            if len(cells) == 11:
                 rows.append(cells)
            elif len(cells) == 14:
                rows.append(cells[:4]+cells[5:9]+cells[10:14])  # Insert empty string for missing 'Votes' column
        
        print((rows[0]))  # Print the header row to verify correct parsing
        columns = rows[0]+['Margin']    
        df = pd.DataFrame(rows[1:], columns=columns)
        print(df.head())
        df.to_csv("tn21_election_results.csv", index=False)
    else:
        print(f"Failed: {response.status_code}")
        print(response.text[:300])
    


if __name__ == "__main__":
    scrape_election_data()
    