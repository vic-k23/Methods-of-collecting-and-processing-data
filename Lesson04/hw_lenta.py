from requests import get
from lxml import html
from pymongo import MongoClient
import config as cfg


class LentaNewsParser:
    """
    Обработчик новостей с Yandex
    """

    def __init__(self):
        """
        Инициализатор класса
        """
        self.__base_url = 'https://lenta.ru/'
        self.__headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/91.0.4472.106 YaBrowser/21.6.0.616 Yowser/2.5 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3;q=0.9'
        }
        # Настройки БД
        self.__db_params = {
            'host': cfg.get_config['MongoDB']['host'],
            'port': int(cfg.get_config['MongoDB']['port']),
            'tz_aware': bool(cfg.get_config['MongoDB']['tz_aware']),
            'username': cfg.get_config['MongoDB']['username'],
            'password': cfg.get_config['MongoDB']['password']
        }

        self.articles = []

    def get_news(self):
        xpath_articles = '//section[contains(@class, "b-top7-for-main")]/descendant::div[contains(@class, "item")]' \
                         '/descendant::a[not(contains(@class, "favorite")) and not(contains(@class, "pic"))]'
        xpath_href = '@href'
        xpath_header = 'text()'
        xpath_time = 'time/@datetime'

        response = get(self.__base_url, headers=self.__headers)
        news_html = html.fromstring(response.text)
        htm_articles = news_html.xpath(xpath_articles)

        for article in htm_articles:
            self.articles.append({
                'source': 'Lenta.ru',
                'header': self.__clear_unbreakable_space(article.xpath(xpath_header)[0]),
                'href': self.__clear_unbreakable_space(article.xpath(xpath_href)[0]),
                'pub_date': self.__clear_unbreakable_space(article.xpath(xpath_time)[0].strip())
            })

        self.__save_news()

    def __clear_unbreakable_space(self, string: str) -> str:
        return string.replace('\xa0', ' ')

    def __save_news(self):
        with MongoClient(self.__db_params['host'],
                         self.__db_params['port'],
                         tz_aware=self.__db_params['tz_aware'],
                         username=self.__db_params['username'],
                         password=self.__db_params['password']) as db:
            collection = db['NewsAgragator']['NewsCollection']
            for article in self.articles:
                collection.update_one(
                    {
                        'source': article['source'],
                        'header': article['header']
                    },
                    {
                        '$set': article
                    },
                    upsert=True
                )


if __name__ == '__main__':
    from pprint import pprint

    ya_news = LentaNewsParser()
    ya_news.get_news()
    pprint(ya_news.articles)
