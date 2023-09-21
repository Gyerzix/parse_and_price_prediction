from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

service = Service(executable_path=r"C:\Users\shakh\scrap_and_price_prediction\chromedriver\chromedriver.exe")
options = webdriver.ChromeOptions()
options.add_argument("user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0")

# disable webdriver mode
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(service=service, options=options)

driver.maximize_window()

# url = "https://clck.ru/35RGvD" # основная ссылка
url = "https://clck.ru/35bu8y"

try:
    driver.get(url)
    # driver.find_element(By.CLASS_NAME, "styles-box-Up_E3").click()
    scrollable_element = driver.find_element(By.CLASS_NAME, "styles-root-Q2aLw")
    # ads_count = int(driver.find_element(By.CLASS_NAME, "breadcrumbs-count-tSv33").text)
    ads_count = 98
    while True:
        count = len(driver.find_elements(By.CLASS_NAME, "styles-snippet-DBv3Q"))
        if count == ads_count:
            with open("../data/source-page.html", "w", encoding="utf-8") as file:
                file.write(driver.page_source)
            break
        else:
            driver.execute_script("arguments[0].scrollBy(0, 10000);", scrollable_element)

except Exception as ex:
    print(ex)

finally:
    driver.close()
    driver.quit()
