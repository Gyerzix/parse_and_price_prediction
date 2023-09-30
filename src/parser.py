import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import requests
from bs4 import BeautifulSoup
import numpy as np
import json
import re
import time
import csv

load_dotenv()
key = os.getenv('API_KEY')

with open("../data/source-page.html", encoding="utf-8") as file:
    src = file.read()

soup = BeautifulSoup(src, "lxml")

all_ads = soup.find_all(class_="body-title-drnL0")
all_ads_dict = {}
for ads_item in all_ads:
    item = ads_item.find("a")
    item_title = item.text.replace('\xa0', ' ')
    item_href = "https://avito.ru" + item.get("href")
    all_ads_dict[item_title] = item_href

with open("../data/all_ads_dict.json", "w", encoding="utf-8") as file:
    json.dump(all_ads_dict, file, indent=4, ensure_ascii=False)

service = Service(executable_path=r"C:\Users\shakh\scrap_and_price_prediction\chromedriver\chromedriver.exe")
options = webdriver.ChromeOptions()
options.add_argument("user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0")

# disable webdriver mode
options.add_argument("--disable-blink-features=AutomationControlled")

options.page_load_strategy = 'none'

# headless mode
# options.add_argument("--headless") # фоновый режим

driver = webdriver.Chrome(service=service, options=options)

driver.maximize_window()

# about the flat
ID = "id"
room_count = "room_count"
type_of_rooms = "type_of_rooms"
full_area = "full_area"
kitchen_area = "kitchen_area"
living_area = "living_area"
flat_floor = "flat_floor"
balcony = "balcony"
ceiling_height = "ceiling_height"
bathroom = "bathroom"
windows = "windows"
renovation = "renovation"
warm_floor = "warm_floor"
furniture = "furniture"
technic = "technic"

# about the house
type_of_house = "type_of_house"
year_of_build = "year_of_build"
house_floors = "house_floors"
passenger_elevator = "passenger_elevator"
freight_elevator = "freight_elevator"
yard = "yard"
parking = "parking"

# location
location = "location"
geo_lat = "geo_lat"
geo_lon = "geo_lon"

# price
price = "price"
price_per_m2 = "price_per_m2"

with open(f"../data/avito_ads.csv", "w", newline='', encoding="utf-8") as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow((ID, room_count, type_of_rooms, full_area, living_area, flat_floor,
                     balcony, ceiling_height, bathroom, windows, renovation, warm_floor,
                     furniture, technic, location, geo_lat, geo_lon, year_of_build, house_floors,
                     passenger_elevator, freight_elevator, yard, parking, price_per_m2, price))


def get_item(items, pattern):
    m_features = ["Общая площадь", "Площадь кухни", "Жилая площадь", "Высота потолков"]
    result = [item.text for item in items if re.search(pattern, item.text)]
    if not result:
        result = np.nan
    else:
        result = result[0].split(':')[1].strip()
        if pattern in m_features:
            result = float(result.split('\xa0')[0].strip())
    return result


def prep_loc(locs):
    list_of_loc = locs[0].text.split(' ')
    result = list_of_loc[0]
    if result in ["от", "до"]:
        result = list_of_loc[1]
    return result


try:
    count = 0
    for name, url in all_ads_dict.items():
        if count == 0:
            driver.get(url)
            time.sleep(5)
            driver.execute_script("window.stop();")
            src = driver.page_source
            soup = BeautifulSoup(src, "lxml")

            ID = soup.find('span', {'data-marker': 'item-view/item-id'}).text.split('\xa0')[1]
            locations = soup.find_all(class_="style-item-address-georeferences-item-interval-ujKs2")  # all locations
            location = prep_loc(locations)
            price = int("".join(soup.find('span', {'data-marker': 'item-view/item-price'}).text.split('\xa0')))
            list_of_price_per_m2 = soup.find(class_="style-item-price-sub-price-_5RUD").text.split('\xa0')
            price_per_m2 = int(list_of_price_per_m2[0] + list_of_price_per_m2[1])

            flat_features = soup.find_all(class_="params-paramsList__item-appQw")
            room_count = get_item(flat_features, "Количество комнат")
            type_of_rooms = get_item(flat_features, "Тип комнат")
            full_area = get_item(flat_features, "Общая площадь")
            kitchen_area = get_item(flat_features, "Площадь кухни")
            living_area = get_item(flat_features, "Жилая площадь")
            flat_floor = get_item(flat_features, "Этаж")[0]
            balcony = get_item(flat_features, "Балкон или лоджия")
            ceiling_height = get_item(flat_features, "Высота потолков")
            bathroom = get_item(flat_features, "Санузел")
            windows = get_item(flat_features, "Окна")
            renovation = get_item(flat_features, "Ремонт")
            warm_floor = get_item(flat_features, "Тёплый пол")
            furniture = get_item(flat_features, "Мебель")
            technic = get_item(flat_features, "Техника")

            house_features = soup.find_all(class_="style-item-params-list-item-aXXql")
            type_of_house = get_item(house_features, "Тип дома")
            year_of_build = get_item(house_features, "Год постройки")
            house_floors = get_item(house_features, "Этажей в доме")
            passenger_elevator = get_item(house_features, "Пассажирский лифт")
            freight_elevator = get_item(house_features, "Грузовой лифт")
            passenger_elevator = int(passenger_elevator) if passenger_elevator not in ("нет", np.nan) else 0
            freight_elevator = int(freight_elevator) if freight_elevator not in ("нет", np.nan) else 0
            yard = get_item(house_features, "Двор")
            parking = get_item(house_features, "Парковка")

            address = soup.find(class_="style-item-address__string-wt61A").text

            url = f"https://geocode-maps.yandex.ru/1.x/?apikey={key}&geocode={address}&format=json"
            res = requests.get(url)
            data = json.loads(res.text)
            geolocation = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split(' ')
            geo_lat, geo_lon = geolocation[0], geolocation[1]
            print(geo_lat, geo_lon)

            with open(f"../data/avito_ads.csv", "a", newline='',
                      encoding="utf-8") as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow((ID, room_count, type_of_rooms, full_area, living_area, flat_floor,
                                 balcony, ceiling_height, bathroom, windows, renovation, warm_floor,
                                 furniture, technic, location, geo_lat, geo_lon, year_of_build, house_floors,
                                 passenger_elevator, freight_elevator, yard, parking, price_per_m2, price))
        count += 1

except Exception as ex:
    print(ex)

finally:
    driver.close()
    driver.quit()
