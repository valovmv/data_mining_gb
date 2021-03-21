# Источник: https://5ka.ru/special_offers/
# Задача организовать сбор данных,
# необходимо иметь метод сохранения данных в .json файлы
# результат: Данные скачиваются с источника, при вызове метода/функции сохранения в файл скачанные данные сохраняются
# в Json вайлы, для каждой категории товаров должен быть создан отдельный файл и содержать товары исключительно
# соответсвующие данной категории.
# пример структуры данных для файла:
# нейминг ключей можно делать отличным от примера
# {
# "name": "имя категории",
# "code": "Код соответсвующий категории (используется в запросах)",
# "products": [{PRODUCT}, {PRODUCT}........] # список словарей товаров соответсвующих данной категории
# }

import requests
import json
import time
import re

URL = 'https://5ka.ru/api/v2/special_offers/'
headers = {'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:86.0) Gecko/20100101 Firefox/86.0'}
CAT_URL = 'https://5ka.ru/api/v2/categories/'


def x5ka(url, params):
    result = []
    while url:
        response = requests.get(url, headers=headers, params=params) if params else requests.get(url, headers=headers)
        params =None
        data = response.json()
        result.extend(data.get('results'))
        url = data.get('next')
        time.sleep(1)
    return result


def create_file_from_item(item):
    data = x5ka(URL, {'categories': item['parent_group_code']})
    filename = item['parent_group_name']
    filename = re.sub(r"[#%!@*/\n/\"]", "", filename)+'.json'
    with open(filename, 'w') as file:
        file.write(json.dumps(data))
        print(f"done: {filename}")


if __name__ == '__main__':
    categories = requests.get(CAT_URL, headers=headers).json()
    for item in categories:
        create_file_from_item(item)
    print("Готово, все файлы записаны!")