from scrapy import Spider
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from Lesson07.leroymerlinparser.leroymerlinparser.items import LeroymerlinparserItem


class LeroymerlinSpider(Spider):
    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru', 'cloudinary.com']
    # start_urls = ['http://leroymerlin.ru/']

    def __init__(self, search):
        super(LeroymerlinSpider, self).__init__()
        self.catalog = search
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}']

    def parse(self, response: HtmlResponse):
        products_links = response.xpath("//a[@data-qa-product-image]")
        next_page = response.xpath('//a[@data-qa-pagination-item="right"]/@href').extract_first()
        for link in products_links:
            yield response.follow(link, callback=self.parse_products)

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_products(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroymerlinparserItem(), response=response)
        loader.add_xpath('name', '//h1[@slot="title"]/text()')
        loader.add_xpath('price', '//meta[@itemprop="price"]/@content')
        loader.add_xpath('photos', '//uc-pdp-media-carousel//img[@itemprop="image"]/@src')
        loader.add_xpath('characteristicks', '//div[@class="def-list__group"]')
        loader.add_value('link', response.url)
        loader.add_value('tags', self.catalog)
        yield loader.load_item()
