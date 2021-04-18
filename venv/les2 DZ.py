"""
Необходимо собрать структуры товаров по акции и сохранить их в MongoDB
пример структуры и типы обязательно хранить поля даты как объекты datetime
{
    "url": str,
    "promo_name": str,
    "product_name": str,
    "old_price": float,
    "new_price": float,
    "image_url": str,
    "date_from": "DATETIME",
    "date_to": "DATETIME",
}
"""

import datetime as dt
from pathlib import Path
from urllib.parse import urljoin
import requests
import bs4
import pymongo
import time

MONTHS = {
    "янв": 1,
    "фев": 2,
    "мар": 3,
    "апр": 4,
    "май": 5,
    "мая": 5,
    "июн": 6,
    "июл": 7,
    "авг": 8,
    "сен": 9,
    "окт": 10,
    "ноя": 11,
    "дек": 12,
}


class MagnitParse:
    def __init__(self, start_url, db_client):
        self.start_url = start_url
        self.db = db_client["data_mining_gb"]
        self.collection = self.db["magnit_products"]

    def _get_response(self, url):
        time_sleep_counts = 0
        while True:
            response = requests.get(url)
            if response.status_code == 200:
                return response
            elif response.status_code != 200:
                time_sleep_counts += 1
                print(response.status_code)
                if time_sleep_counts == 3:
                    break
                else:
                    time.sleep(0.5)

    def _get_soup(self, url):
        time_sleep_counts = 0
        while True:
            response = self._get_response(url)
            if response.status_code == 200:
                soup = bs4.BeautifulSoup(response.text, "lxml")
                return soup
            elif response.status_code != 200:
                time_sleep_counts += 1
                print(response.status_code)
                if time_sleep_counts == 3:
                    break
                else:
                    time.sleep(0.5)

    def run(self):
        soup = self._get_soup(self.start_url)
        catalog = soup.find("div", attrs={"class": "сatalogue__main"})
        for prod_a in catalog.find_all("a", recursive=False):
            product_data = self._parse(prod_a)
            self._save(product_data)

    def get_template(self):
        return {
            "product_name": lambda a: a.find("div", attrs={"class": "card-sale__title"}).text,
            "url": lambda a: urljoin(self.start_url, a.attrs.get("href", "")),
            "promo_name": lambda a: a.find("div", attrs={"class": "card-sale__name"}).text,
            "old_price": lambda a: float(
                ".".join(
                    itm for itm in a.find("div", attrs={"class": "label__price_old"}).text.split()
                )
            ),
            "new_price": lambda a: float(
                ".".join(
                    itm for itm in a.find("div", attrs={"class": "label__price_new"}).text.split()
                )
            ),
            "image_url": lambda a: urljoin(self.start_url, a.find("img").attrs.get("data-src")),
            "date_from": lambda a: self.__get_date(
                a.find("div", attrs={"class": "card-sale__date"}).text
            )[0],
            "date_to": lambda a: self.__get_date(
                a.find("div", attrs={"class": "card-sale__date"}).text
            )[1],
        }

    def __get_date(self, date_string) -> list:
        date_list = date_string.replace("Только ", "").replace("с ", "", 1).replace("\n", "").split("до")
        result = []
        now_month = dt.datetime.now().month
        for date in date_list:
            temp_date = date.split()
            # При условии что нам не покажут будущие акции и их начало
            if now_month < MONTHS[temp_date[1][:3]] and date == date_list[0]:
                year_sell = dt.datetime.now().year - 1
            else:
                year_sell = dt.datetime.now().year
            i = 0
            if date_string.find("Только") == True:
                while i < 2:
                    result.append(
                        dt.datetime(
                            year=dt.datetime.now().year,
                            day=int(temp_date[0]),
                            month=MONTHS[temp_date[1][:3]],
                        )
                    )
                    i += 1
            else:
                result.append(
                    dt.datetime(
                        year=dt.datetime.now().year,
                        day=int(temp_date[0]),
                        month=MONTHS[temp_date[1][:3]],
                    )
                )
        return result

    def _parse(self, product_a) -> dict:
        data = {}
        for key, funk in self.get_template().items():
            try:
                data[key] = funk(product_a)
            except (AttributeError, ValueError):
                pass
        return data

    def _save(self, data: dict):
        self.collection.insert_one(data)


def get_save_path(dir_name):
    dir_path = Path(__file__).parent.joinpath(dir_name)
    if not dir_path.exists():
        dir_path.mkdir()
    return dir_path


if __name__ == "__main__":
    url = "https://magnit.ru/promo/?geo=moskva"
    save_path = get_save_path("magnit_product")
    db_client = pymongo.MongoClient("mongodb://localhost:27017")
    parser = MagnitParse(url, db_client)
    parser.run()