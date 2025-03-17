import os
import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# Hardcoded JSON data for only California national parks
national_parks = {
    "Channel Islands NP": {
        "code": "CHIS",
        "api_link": "https://www.wunderground.com/history/monthly/us/ca/goleta/KSBA/date/2025-3"
    },
    "Death Valley NP": {
        "code": "DEVA",
        # Although Death Valley is partially in Nevada, this URL is used for accessing its weather data.
        "api_link": "https://www.wunderground.com/history/monthly/us/nv/north-las-vegas/KVGT/date/2025-3"
    },
    "Joshua Tree NP": {
        "code": "JOTR",
        "api_link": "https://www.wunderground.com/history/monthly/us/ca/palm-springs/KPSP/date/2025-3"
    },
    "Kings Canyon NP": {
        "code": "KICA",
        "api_link": "https://www.wunderground.com/history/monthly/us/ca/visalia/KVIS/date/2025-3"
    },
    "Lassen Volcanic NP": {
        "code": "LAVO",
        "api_link": "https://www.wunderground.com/history/monthly/us/ca/sacramento/KSMF/date/2025-3"
    },
    "Pinnacles NP": {
        "code": "PINN",
        "api_link": "https://www.wunderground.com/history/monthly/us/ca/monterey/KMRY/date/2025-3"
    },
    "Redwood NP": {
        "code": "REDW",
        "api_link": "https://www.wunderground.com/history/monthly/us/ca/crescent-city/KCEC/date/2025-3"
    },
    "Sequoia NP": {
        "code": "SEQU",
        "api_link": "https://www.wunderground.com/history/monthly/us/ca/visalia/KVIS/date/2025-3"
    },
    "Yosemite NP": {
        "code": "YOSE",
        "api_link": "https://www.wunderground.com/history/monthly/us/ca/crowley-lake/KMMH/date/2025-3"
    }
}

# Create folder to save CSV files
output_folder = "weather-data"
os.makedirs(output_folder, exist_ok=True)

# Set up Selenium WebDriver (update chromedriver path as needed)
options = Options()
options.add_argument("--headless")
service = Service("/Users/himanshunimonkar/Downloads/STA_220/chromedriver")  # Update this path if needed
driver = webdriver.Chrome(service=service, options=options)

# CSV headers for output
final_headers = [
    "Year", "Month", "Day", 
    "Temp Max", "Temp Avg", "Temp Min",
    "Dew Point Max", "Dew Point Avg", "Dew Point Min",
    "Humidity Max", "Humidity Avg", "Humidity Min",
    "Wind Speed Max", "Wind Speed Avg", "Wind Speed Min",
    "Pressure Max", "Pressure Avg", "Pressure Min",
    "Precipitation Total"
]

# Iterate over each California national park in the JSON data
for park_name, park_info in national_parks.items():
    print(f"\n=== Scraping data for {park_name} ===")
    # Build output CSV file path
    output_file = os.path.join(output_folder, f"{park_name}.csv")
    
    # Open CSV file for writing
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(final_headers)  # Write CSV headers

        # Get the base URL (everything before the "/date/" part)
        base_url = park_info["api_link"].split("/date/")[0]
        
        # Loop through years 2015 to 2024 and months January to December
        for year in range(2015, 2025):
            for month in range(1, 13):
                # Build the URL with the desired year and month
                url = f"{base_url}/date/{year}-{month}"
                print(f"Scraping: {park_name} {year}-{month:02d}")
                
                driver.get(url)
                time.sleep(5)  # Wait for page to load completely
                
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")

                # Locate the main weather table
                main_table = soup.find("table", {"aria-labelledby": "History days"})
                if not main_table:
                    print(f"Data for {park_name} {year}-{month:02d} not found. Skipping.")
                    continue  # Skip if the table is not found

                # Extract data from the table rows
                outer_row = main_table.find("tbody").find("tr")
                cells = outer_row.find_all("td")
                nested_data = []

                # Loop through each cell (column)
                for cell in cells:
                    nested_table = cell.find("table")
                    col_data = []
                    if nested_table:
                        rows = nested_table.find_all("tr")
                        if rows:
                            # Check if first row is header; skip if not a digit
                            first_cell_text = rows[0].find("td").text.strip() if rows[0].find("td") else ""
                            if not first_cell_text.isdigit():
                                rows = rows[1:]
                        for row in rows:
                            cells_in_row = row.find_all("td")
                            cell_texts = [td.text.strip() for td in cells_in_row]
                            col_data.append(cell_texts)
                    nested_data.append(col_data)

                # Determine the number of days from the first column
                num_days = len(nested_data[0]) if nested_data and nested_data[0] else 0

                # Combine data row by row
                for i in range(num_days):
                    row_combined = [year, month]  # Year and Month columns
                    day_val = nested_data[0][i][0] if i < len(nested_data[0]) and nested_data[0][i] else ""
                    row_combined.append(day_val)
                    
                    # Loop through the remaining columns
                    for col in range(1, len(nested_data)):
                        # For Precipitation column (assumed single value)
                        if col == 6:
                            value = nested_data[col][i][0] if i < len(nested_data[col]) and nested_data[col][i] else ""
                            row_combined.append(value)
                        else:
                            # For temperature, dew point, humidity, etc.
                            values = nested_data[col][i] if i < len(nested_data[col]) and nested_data[col][i] else [""] * 3
                            row_combined.extend(values)
                    
                    # Remove any empty string cells before writing
                    row_combined = [str(cell).strip() for cell in row_combined if str(cell).strip()]
                    if row_combined:
                        writer.writerow(row_combined)
    
    print(f"Cleaned weather data for {park_name} saved to {output_file}")

# Quit the WebDriver after processing all parks
driver.quit()

print("\nAll California national parks data saved in the 'weather-data' folder.")
