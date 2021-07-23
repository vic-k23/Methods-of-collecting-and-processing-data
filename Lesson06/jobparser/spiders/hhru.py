import scrapy
from scrapy.http import HtmlResponse
from Lesson06.jobparser.items import JobparserItem
from re import search


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    # start_urls = ['http://hh.ru/']

    def __init__(self, vacancy='Data Science'):
        super().__init__()
        self.start_urls = [f'https://hh.ru/search/vacancy?st=searchVacancy&text={vacancy}']

    def parse(self, response: HtmlResponse):
        vacancies_links = response.xpath("//a[@data-qa='vacancy-serp__vacancy-title']/@href").extract()
        next_page = response.xpath("//a[@data-qa='pager-next']/@href").extract_first()

        for link in vacancies_links:
            yield response.follow(link, callback=self.vacansy_parse)

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def vacansy_parse(self, response: HtmlResponse):
        vacancy_name = response.xpath("//h1/text()").extract_first()
        vacancy_link = response.url
        site = 'https://hh.ru/'
        vacancy_salary = ' '.join(response.xpath("//p[@class='vacancy-salary']/span/text()").extract())
        item = JobparserItem(name=vacancy_name, link=vacancy_link, salary=vacancy_salary, source_site=site)
        yield item
