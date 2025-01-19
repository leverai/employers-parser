import csv
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import sys, os
print(sys.argv[0])         
path = os.path.dirname(sys.argv[0])   
fullpath = os.path.abspath(path)

# Настройки Chrome
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Запуск в фоновом режиме
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-software-rasterizer")
chrome_options.add_argument("--disable-webgl")
chrome_options.add_argument("--disable-bluetooth")
chrome_options.add_argument('--ignore-certificate-errors-spki-list')


service = Service("M:\\chromedriver\\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)

page_index = 0

# URL первой страницы
baseUrl = "https://kirov.hh.ru/employers_company/obrazovatelnye_uchrezhdeniya?customDomain=1&page="
url = baseUrl+str(page_index)

output_file = path+"\employers_data.csv"



with open(output_file, mode="w", newline="", encoding="utf-8-sig") as file:
    writer = csv.writer(file, delimiter=";")  
    writer.writerow(["Name", "Page", "Website"])  
    

    while True:
        url = baseUrl+str(page_index)
        print(url)
        driver.get(url)
        time.sleep(1)
        # page_source = driver.page_source
        # print(page_source)
        employers = driver.find_elements(By.CLASS_NAME, "employer--u3kJFXzDlcEGXYWV")
        if len(employers) == 0: break
        employer_links = [employer.find_element(By.TAG_NAME, "a").get_attribute("href") for employer in employers]
        print("Страница "+ str(page_index))
       
        for employer_link in employer_links:
            driver.get(employer_link)
            time.sleep(1)  
            
            noindex_templates = driver.find_elements(By.CSS_SELECTOR, "template#HH-Lux-InitialState")
            last_template = noindex_templates[0]
            json_data = json.loads(last_template.get_attribute("innerHTML"))
            employer_name = json_data.get("employerInfo", {}).get("name", {})
            try:
                if noindex_templates:
                    employer_website = json_data.get("employerInfo", {}).get("site", {}).get("href")
                    print(f"Employer page: {employer_link}")
                    print(f"Employer website: {employer_website}")
                else:
                    employer_website = None
                    print(f"Employer page: {employer_link}")
                    print("No employer website found")

            except Exception as e:
                print(f"Error processing employer page {employer_link}: {e}")
                employer_website = "Empty"
                
            writer.writerow([employer_name, employer_link, employer_website])
        page_index+=1
    

driver.quit()
print(f"Data saved to {output_file}")
