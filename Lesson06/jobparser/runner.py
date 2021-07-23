from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from sys import argv

from Lesson06.jobparser import settings
from Lesson06.jobparser.spiders.hhru import HhruSpider
from Lesson06.jobparser.spiders.sjru import SjruSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    vacancy = argv[1] if len(argv) > 1 else 'Data Science'

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(HhruSpider, vacancy)
    process.crawl(SjruSpider, vacancy)

    process.start()