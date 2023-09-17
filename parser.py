from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import json
import time
import csv

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Referer': 'https://www.avito.ru/'
}

proxies = {
    'https': 'http://107.1.93.217:80'
}

with open("data/source-page.html", encoding="utf-8") as file:
    src = file.read()

soup = BeautifulSoup(src, "lxml")

all_ads = soup.find_all(class_ = "body-title-drnL0")
all_ads_dict = {}
for ads_item in all_ads:
    item = ads_item.find("a")
    item_title = item.text.replace('\xa0', ' ')
    item_href = "https://avito.ru" + item.get("href")
    all_ads_dict[item_title] = item_href
    # print(f"{item_title}: {item_href}")

with open("data/all_ads_dict.json", "w", encoding="utf-8") as file:
    json.dump(all_ads_dict, file, indent=4, ensure_ascii=False)

service = Service(executable_path= r"C:\Users\shakh\scrap_and_price_prediction\chromedriver\chromedriver.exe")
options = webdriver.ChromeOptions()
options.add_argument("user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0")

# disable webdriver mode
options.add_argument("--disable-blink-features=AutomationControlled")

# headless mode
# options.add_argument("--headless") # фоновый режим

driver = webdriver.Chrome(service=service, options=options)

floor = "floor"
room_count = "room_count"


with open(f"data/avito_ads.csv", "w", newline='', encoding="utf-8") as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(())

try:
    count = 0
    for name, url in all_ads_dict.items():
        if count <= 2:
            driver.get(url)
            time.sleep(1)
            src = driver.page_source
            soup = BeautifulSoup(src, "lxml")

        count += 1

except Exception as ex:
    print(ex)

finally:
    driver.close()
    driver.quit()
# count = 0
# for name, url in all_ads_dict.items():
#     if count == 0:
#         req = requests.get(url, headers=headers)
#         # req = requests.get(url, proxies=proxies)
#         src = req.text
#         print(req.status_code)
#         print(url)
#     count += 1
