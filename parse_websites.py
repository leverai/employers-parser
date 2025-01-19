import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
import re
from itertools import islice


chrome_options = Options()
# chrome_options.add_argument("--headless")  
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--enable-unsafe-swiftshader")
service = Service("M:\\chromedriver\\chromedriver.exe") 


input_file = "pages0to1.csv"
output_file = "updated_employers.csv"


driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    
    with open(input_file, mode='r', encoding='utf-8-sig') as infile, open(output_file, mode='w', encoding='utf-8-sig', newline='') as outfile:
        reader = csv.reader(infile, delimiter=";")
        writer = csv.writer(outfile, delimiter=";")
        index = 0
        
        header = next(reader)
        writer.writerow(header + ["Contacts"]) 

        
        for row in islice(reader, 23, None):
            
            link = row[2] if len(row) > 1 else None
            link = row[2] if row[2] != 'Empty' else None
            
            if link:
                try:
                   
                    driver.get(link)
                    time.sleep(1)  
                    
                    page_source = driver.page_source
                    contact_data = {
                        "emails": [],
                        "phones": [],
                        "social_links": [],
                        "error": None
                    }
                    # Поиск email
                    contact_data["emails"] = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', page_source)

                    # Поиск телефона
                    contact_data["phones"] = re.findall(r'\+7\s?(?:\(\d{3,4}\)\s?|\d{3})\s?\d{3}[-\s]?\d{2}[-\s]?\d{2}', page_source)

                    # Поиск ссылок на социальные сети
                    contact_data["social_links"] = re.findall(r'https?://(?:www\.)?(vk|facebook|instagram|linkedin|twitter|telegram|wa)\.(com|ru)/([^\s"\']+)', page_source)
                    # Проверка на страницу "Контакты"
                    try:
                        contact_link = driver.find_element(By.PARTIAL_LINK_TEXT, "Контакт")
                        if contact_link.is_displayed():
                            contact_link.click()
                            time.sleep(1)
                        else:
                            print("Contact link is hidden.")
                        
                       
                        contact_page_source = driver.page_source
                        # print(contact_page_source)
                        contact_data["emails"].extend(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', contact_page_source))
                        contact_data["social_links"].extend(re.findall(r'https?://(?:www\.)?(vk|facebook|instagram|linkedin|twitter|telegram|wa|t)\.(com|ru|me)/([^\s"\']+)', contact_page_source))
                        contact_data["phones"].extend(re.findall(r'\+7\s?(?:\(\d{3,4}\)\s?|\d{3})\s?\d{3}[-\s]?\d{2}[-\s]?\d{2}', contact_page_source))
                    except NoSuchElementException:
                        pass  
                    def is_placeholder(phone):
                        return re.match(r'\+7\s?\((900|999)\)\s?(\d{3})[-\s]?(\d{2})[-\s]?(\d{2})', phone)
                    valid_phones = [phone for phone in contact_data["phones"] if not is_placeholder(phone)]
                    full_links = [f"https://{link[0]}.{link[1]}/{link[2]}" if len(link) == 3 and link[2].find("api") == -1 else f"https://{link[0]}.{link[1]}" for link in contact_data["social_links"]]
                    contact_data["emails"] = list(set(contact_data["emails"]))
                    contact_data["phones"] = list(set(valid_phones))
                    contact_data["social_links"] = list(set(full_links))
                    # Записываем данные
                    writer.writerow(
                        row + contact_data["emails"] + contact_data["social_links"] + contact_data["phones"]
                    )
                except Exception as e:
                    writer.writerow(row + ["", "", "Error"])
            else:
                writer.writerow(row + ["No Link", "No Link"])
            index+=1
finally:
    
    driver.quit()