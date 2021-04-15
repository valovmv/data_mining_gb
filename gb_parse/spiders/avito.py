import scrapy
from pymongo import MongoClient



class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['www.avito.ru/']
    start_urls = ['https://www.avito.ru/krasnodar/kvartiry/prodam']

    __xpath_query = {
        'pagination': '//div[@class="index-content-2lnSO"]//'
                      'div[contains(@data-marker, "pagination-button")]/'
                      'span[@class="pagination-item-1WyVp"]/@data-marker',
        'ads': '//h3[@class="snippet-title"]/a[@class="snippet-link"][@itemprop="url"]/@href'}

    def parse(self, response, start=True):
        if start:
            pages_count = int(
                response.xpath(self.__xpath_query['pagination']).extract()[-1].split('(')[-1].replace(')', ''))

            for num in range(2, pages_count + 1):
                yield response.follow(
                    f'?p={num}',
                    callback=self.parse,
                    cb_kwargs={'start': False}
                )

        for link in response.xpath(self.__xpath_query['ads']):
            yield response.follow(
                link,
                callback=self.ads_parse
            )

    def ads_parse(self, response):
        result = {}
        result['title'] = \
        response.xpath('//h1[@class="title-info-title"]/span[@class="title-info-title-text"]').extract()[-1].split('>')[
            1].split('<')[0]
        result['url'] = response.url
        result['photo'] = self.find_photo_src(response.xpath('//div[@class="item-view-content"]').extract()[-1])
        result['price'] = \
        response.xpath('//div[@class="item-price"]//span[@itemprop="price"]').extract()[-1].split('"')[5]
        result['address'] = \
        response.xpath('//div[@itemprop="address"]/span[@class="item-address__string"]').extract()[-1].split('\n')[1]
        result['params'] = self.find_params(response)

        self.save_to_mongo(result)

    def find_photo_src(self, to_find: str):
        to_find = to_find.split(' ')
        result = []
        for itm in to_find:
            if itm.find('data-url=') != -1:
                result.append(itm.split('"')[1])
        return result

    def find_params(self, response):
        list = []

        selectors = response.xpath('//div[@class="item-params"]/ul[@class="item-params-list"]/li')
        for itm in selectors:
            itm = itm.extract().split('>')
            if itm[2].split(':')[0] == 'Название новостройки':
                params = {itm[2].split(':')[0]: itm[5].split('<')[0]}
            else:
                params = {itm[2].split(':')[0]: itm[3].split('<')[0]}
            list.append(params)
            params = {}

        return list

    def save_to_mongo(self, data: dict):
        client = MongoClient('mongodb://localhost:27017')
        db = client['parse_avito']
        collection = db['apartments']

        collection.insert(data)
