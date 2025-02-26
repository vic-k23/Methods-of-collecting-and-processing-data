from sys import argv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from instagramParser.spiders.instagram import InstagramSpider
from instagramParser import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    if len(argv) <= 1:
        argv.append('cheboksary_3d')
        # argv.append('ai_machine_learning')
    for i in range(1, len(argv)):
        process.crawl(InstagramSpider, user=argv[i])

    process.start()
