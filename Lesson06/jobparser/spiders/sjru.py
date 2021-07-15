import scrapy
from scrapy.http import HtmlResponse
from Lesson06.jobparser.items import JobparserItem
from re import search


class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    # start_urls = ['http://superjob.ru/']

    def __init__(self, vacancy='Data Science'):
        super().__init__()
        self.start_urls = [f'https://russia.superjob.ru/vacancy/search/?keywords={vacancy}']

    def parse(self, response: HtmlResponse):
        vacancies_links = \
            response.xpath("//div[contains(@class, 'f-test-vacancy-item')]/div/div/div/div/div/a/@href").extract()
        next_page = response.xpath("//a[contains(@class, 'f-test-link-Dalshe')]/@href").extract_first()

        for link in vacancies_links:
            yield response.follow(link, callback=self.vacansy_parse)

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def vacansy_parse(self, response: HtmlResponse):
        vacancy_name = response.xpath("//div[contains(@class, 'f-test-vacancy-base-info')]"
                                      "/div/div/div/div/h1/text()").extract_first()
        vacancy_link = response.url
        vacancy_salary = ' '.join(response.xpath("//div[contains(@class, 'f-test-vacancy-base-info')]"
                                                 "/div/div/div/div/span/span[1]/span/text()").extract())
        site = 'https://russia.superjob.ru/'
        item = JobparserItem(name=vacancy_name, link=vacancy_link, salary=vacancy_salary, source_site=site)
        yield item
