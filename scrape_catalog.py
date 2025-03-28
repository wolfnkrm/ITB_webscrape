# Required Libraries
# pip install selenium pandas openpyxl beautifulsoup4 lxml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

# Function to scrape data
def scrape_catalog():
    # Initialize the browser (Make sure to download the correct WebDriver for your browser)
    driver = webdriver.Chrome()  # Or use Firefox/Edge WebDriver
    driver.get("https://simajik.itb.ac.id/public-site/vmi/catalog/kimia")

    all_data = []

    # Loop through all 20 pages
    for page in range(1, 21):  # Assuming 20 pages
        print(f"Scraping page {page}...")

        # Wait for the page to load
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "card-body")))

        # Get the page source and parse it with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        items = soup.find_all('div', class_='card-body')

        # Extract data for each item
        for item in items:
            try:
                # Extract item name
                name = item.find('p', class_='item').get_text(strip=True)
                # Extract price (remove "Rp." and format it as a number)
                price = item.find_all('p')[1].get_text(strip=True).replace("Rp. ", "").replace(".", "")
                # Extract Kode and Spesifikasi from the "data-bs-content" attribute
                popover_data = item.find('input', class_='cc1')['data-bs-content']
                popover_soup = BeautifulSoup(popover_data, 'html.parser')
                kode = popover_soup.find(text=lambda x: x and "Kode:" in x).replace("Kode: ", "").strip()
                spesifikasi = popover_soup.find(text=lambda x: x and "Spesifikasi:" in x).replace("Spesifikasi: ", "").strip()

                # Append the data
                all_data.append({
                    "Item": name,
                    "Harga": price,
                    "Kode": kode,
                    "Spesifikasi": spesifikasi
                })
            except Exception as e:
                print(f"Error parsing item: {e}")

        # Click the "Next" button to go to the next page (if not on the last page)
        if page < 20:
            try:
                next_button = driver.find_element(By.LINK_TEXT, str(page + 1))
                next_button.click()
                time.sleep(2)  # Wait for the next page to load
            except Exception as e:
                print(f"Error navigating to next page: {e}")
                break

    driver.quit()
    return all_data

# Main execution
if __name__ == "__main__":
    data = scrape_catalog()

    # Save the data to an Excel file
    df = pd.DataFrame(data)
    output_file = "catalog_data.xlsx"
    df.to_excel(output_file, index=False)
    print(f"Data saved to {output_file}")
