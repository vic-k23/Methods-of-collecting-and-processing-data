from datetime import date
from datetime import datetime
from time import sleep
from re import search
from requests import get
from lxml import html
from pymongo import MongoClient
# Конфигурация проекта
import config as cfg


class NewsParser:
    """
    Обработчик новостей с Yandex, Lenta и Mail
    """

    def __init__(self):
        """
        Инициализатор класса
        """
        self.__yandex_base_url = 'https://yandex.ru/news/'
        self.__lenta_base_url = 'https://lenta.ru/'
        self.__mail_base_url = 'https://news.mail.ru/'
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

    def __clear_unbreakable_space(self, string: str) -> str:
        """
        Очистка строки от неразрывных пробелов
        :param string: строка, которую нужно очистить
        :return: строка с обычными пробелами вместо неразрывных
        """
        return string.replace('\xa0', ' ')

    def __save_news(self):
        """
        Сохранение новостей в БД
        :return: None
        """
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

    def get_yandex_news(self):
        """
        Сбор новостей с Yandex
        :return: None
        """
        xpath_articles = '//div[contains(@class, "news-app__top")]//article'
        xpath_href = 'descendant::a[@class="mg-card__link"]/@href'
        xpath_header = 'descendant::h2[@class="mg-card__title"]/text()'
        xpath_time = 'descendant::span[@class="mg-card-source__time"]/text()'
        xpath_source = 'descendant::a[@class="mg-card__source-link"]/text()'

        response = get(self.__yandex_base_url, headers=self.__headers)
        news_html = html.fromstring(response.text)
        htm_articles = news_html.xpath(xpath_articles)

        for article in htm_articles:
            pub_date = self.__clear_unbreakable_space(str(article.xpath(xpath_time)[0]))
            if pub_date.find('вчера') >= 0:
                pub_date = datetime(date.today().year, date.today().month, date.today().day - 1,
                                    hour=int(search(r'(\d?\d):(\d\d)', pub_date)[1]),
                                    minute=int(search(r'(\d?\d):(\d\d)', pub_date)[2]))
            else:
                pub_date = datetime(date.today().year, date.today().month, date.today().day,
                                    hour=int(search(r'(\d?\d):(\d\d)', pub_date)[1]),
                                    minute=int(search(r'(\d?\d):(\d\d)', pub_date)[2]))
            self.articles.append({
                'source': self.__clear_unbreakable_space(str(article.xpath(xpath_source)[0])),
                'header': self.__clear_unbreakable_space(article.xpath(xpath_header)[0]),
                'href': self.__clear_unbreakable_space(article.xpath(xpath_href)[0]),
                'pub_date': str(pub_date)
            })

        self.__save_news()

    def get_lenta_news(self):
        """
        Сбор новостей с Lenta
        :return: None
        """
        xpath_articles = '//section[contains(@class, "b-top7-for-main")]/descendant::div[contains(@class, "item")]' \
                         '/descendant::a[not(contains(@class, "favorite")) and not(contains(@class, "pic"))]'
        xpath_href = '@href'
        xpath_header = 'text()'
        xpath_time = 'time/@datetime'

        response = get(self.__lenta_base_url, headers=self.__headers)
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

    def get_mail_news(self):
        """
        Сбор новостей с Mail
        :return: None
        """
        xpath_articles = '//div[@class="block"]/descendant::ul/li/a'
        xpath_href = '@href'
        xpath_header = 'text()'
        xpath_time = '//span[@class="note__text breadcrumbs__text js-ago"]/@datetime'
        xpath_source = '//a[@class="link color_gray breadcrumbs__link"]/span/text()'

        response = get(self.__mail_base_url, headers=self.__headers)
        news_html = html.fromstring(response.text)
        htm_articles = news_html.xpath(xpath_articles)

        for article in htm_articles:
            response = get(article.xpath(xpath_href)[0], headers=self.__headers)
            news_html = html.fromstring(response.text)
            pub_date = news_html.xpath(xpath_time)[0]
            source = news_html.xpath(xpath_source)[0]
            self.articles.append({
                'source': source,
                'header': self.__clear_unbreakable_space(article.xpath(xpath_header)[0]),
                'href': self.__clear_unbreakable_space(article.xpath(xpath_href)[0]),
                'pub_date': pub_date
            })
            sleep(0.5)

        self.__save_news()


if __name__ == '__main__':
    from pprint import pprint

    news = NewsParser()
    news.get_yandex_news()
    news.get_lenta_news()
    news.get_mail_news()
    pprint(news.articles)
