#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def scrape_davis_garcia_stats(url):
    """Scrapes CompuBox stats for Davis vs Garcia from BoxingScene."""
    try:
        response = requests.get(url)
        response.raise_for_status() # Raise an exception for bad status codes
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")

    # Find all tables with the relevant structure (often within a specific div)
    # Inspecting the page, the tables seem to be directly within the article content area.
    # Let's target tables directly. We might need to adjust based on actual structure.
    tables = soup.find_all("table")

    if len(tables) < 4:
        print(f"Error: Expected at least 4 tables, found {len(tables)}. Scraping might fail.")
        # Try to proceed if at least 3 tables (round stats) are found
        if len(tables) < 3:
             return None

    # --- Helper function to parse a stats table ---
    def parse_stats_table(table, stat_type):
        data = {}
        rows = table.find_all("tr")
        if not rows:
            return None
            
        headers = [th.get_text(strip=True) for th in rows[0].find_all("th")]
        num_rounds = 0
        for h in headers:
            if h.isdigit():
                num_rounds = max(num_rounds, int(h))
            
        for row in rows[1:]: # Skip header row
            cols = row.find_all("td")
            if not cols:
                continue
            boxer = cols[0].get_text(strip=True)
            if boxer not in ["DAVIS", "GARCIA"]:
                 continue # Skip rows not containing boxer names
                 
            data[boxer] = {}
            for i in range(1, min(len(cols), num_rounds + 1)): # Iterate through round columns
                round_num = i
                # Extract Landed/Thrown values
                match = re.match(r"(\d+)/(\d+)", cols[i].get_text(strip=True))
                if match:
                    landed = int(match.group(1))
                    thrown = int(match.group(2))
                    data[boxer][round_num] = {f"{stat_type}_Landed": landed, f"{stat_type}_Thrown": thrown}
                else:
                    # Handle cases like "-" or empty cells for rounds that didn't happen
                    data[boxer][round_num] = {f"{stat_type}_Landed": 0, f"{stat_type}_Thrown": 0}
        return data, num_rounds

    # --- Parse the tables ---
    total_stats, num_rounds = parse_stats_table(tables[0], "Total")
    jab_stats, _ = parse_stats_table(tables[1], "Jab")
    power_stats, _ = parse_stats_table(tables[2], "Power") # Power punches = Significant punches

    if not total_stats or not jab_stats or not power_stats:
        print("Error parsing one or more stats tables.")
        return None

    # --- Combine data into DataFrame structure ---
    match_data = []
    boxers = ["DAVIS", "GARCIA"]
    boxer_full_names = {"DAVIS": "Gervonta Davis", "GARCIA": "Hector Luis Garcia"}

    for round_num in range(1, num_rounds + 1):
        for boxer_key in boxers:
            boxer_name = boxer_full_names[boxer_key]
            opponent_key = [b for b in boxers if b != boxer_key][0]
            opponent_name = boxer_full_names[opponent_key]

            round_total = total_stats.get(boxer_key, {}).get(round_num, {"Total_Landed": 0, "Total_Thrown": 0})
            round_jab = jab_stats.get(boxer_key, {}).get(round_num, {"Jab_Landed": 0, "Jab_Thrown": 0})
            round_power = power_stats.get(boxer_key, {}).get(round_num, {"Power_Landed": 0, "Power_Thrown": 0})

            # Calculate Head/Body breakdown if possible (using final stats as approximation? No, stick to round data)
            # The tables don't give round-by-round head/body breakdown. We'll omit these or set to 0.
            head_landed = 0 # Placeholder
            body_landed = 0 # Placeholder
            
            # Ring control is not available
            ring_control_pct = 0 # Placeholder

            match_data.append({
                "Round": round_num,
                "Boxer": boxer_name,
                "Opponent": opponent_name,
                "Punches Thrown": round_total["Total_Thrown"],
                "Punches Landed": round_total["Total_Landed"],
                "Significant Punches Thrown": round_power["Power_Thrown"], # Use Power as Significant
                "Significant Punches Landed": round_power["Power_Landed"],
                "Head Punches Landed": head_landed, 
                "Body Punches Landed": body_landed,
                "Jabs Landed": round_jab["Jab_Landed"],
                "Power Punches Landed": round_power["Power_Landed"],
                "Ring Control %": ring_control_pct
            })

    df = pd.DataFrame(match_data)
    return df

if __name__ == "__main__":
    target_url = "https://www.boxingscene.com/articles/gervonta-davis-vs-hector-luis-garcia-compubox-punch-stats"
    scraped_df = scrape_davis_garcia_stats(target_url)

    if scraped_df is not None:
        output_file = "davis_garcia_stats.csv"
        scraped_df.to_csv(output_file, index=False)
        print(f"Successfully scraped data and saved to {output_file}")
    else:
        print("Failed to scrape data.")

