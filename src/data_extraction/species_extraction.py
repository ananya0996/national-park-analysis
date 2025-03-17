import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

download_dir = "/Users/himanshunimonkar/Downloads/STA_220/Animals"
chrome_options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=chrome_options)
driver.get("https://irma.nps.gov/NPSpecies/Search/SpeciesList/YOSE")

try:
    # Click 'Include Park Synonyms' checkbox
    include_synonyms = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//label[contains(text(), 'Include Park Synonyms')]/ancestor::tr//input[@type='button']"))
    )
    include_synonyms.click()

    # Select 'Full list with details' radio button
    full_list_details = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//label[contains(text(), 'Full list with details')]/preceding-sibling::input[@type='button']"))
    )
    full_list_details.click()

    # Click 'Search' button using its ID
    search_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "button-1021"))
    )
    search_button.click()

    # Wait for and click the 'Download' button using its ID
    download_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, "button-1142"))
    )
    download_button.click()

    # Wait for the download to complete
    time.sleep(15)

except TimeoutException as e:
    print(e)
finally:
    driver.quit()
