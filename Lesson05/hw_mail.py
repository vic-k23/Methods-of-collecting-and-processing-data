# Написать программу, которая собирает входящие письма из своего или тестового почтового ящика
# и сложить данные о письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный)

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient
from time import sleep
import logging

import config as cfg


class MailCollector:
    """
    Сборщик почты
    """
    def __init__(self):
        """
        Инициализация переменных объекта
        """

        # webriver browser
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # Режим без интерфейса
        chrome_options.add_argument("--start-maximized")  # Запускать развёрнутым
        self.browser = webdriver.Chrome(options=chrome_options)
        self.__headers = {
            'User Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3;q=0.9'
        }
        # Список ссылок на письма
        self.hrefs = []

        # Настройки подключения к Mongo
        self.__db_host = cfg.get_config['MongoDB']['host']
        self.__db_port = int(cfg.get_config['MongoDB']['port'])
        self.__db_tz_aware = bool(cfg.get_config['MongoDB']['tz_aware'])
        self.__db_username = cfg.get_config['MongoDB']['username']
        self.__db_password = cfg.get_config['MongoDB']['password']

        # Настройки аутентификации в почтовом ящике
        self.__mail_username = cfg.get_config['MailRu']['username']
        self.__mail_password = cfg.get_config['MailRu']['password']

        # Журналирование
        self.__logger = logging.getLogger(__name__)

    def login(self):
        """
        Функция аутентификации
        :return: None
        """
        self.browser.get("https://mail.ru/")
        elem = self.browser.find_element_by_name("login")
        elem.send_keys(self.__mail_username)
        elem.send_keys(Keys.RETURN)
        try:
            elem = WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((By.NAME, "password")))
            elem.send_keys(self.__mail_password)
            elem.send_keys(Keys.RETURN)
        except TimeoutException:
            print("Timeout while waiting for password input.")
        #     self.__browser.quit()

    def collect_hrefs(self):
        """
        Фукция собирает список ссылок на письма
        :return: None
        """
        hrefs = set()
        hrefs_len_last = -1
        hrefs_len_new = len(hrefs)
        # Пока количество элементов множества увеличивается, листаем список писем на странице
        while hrefs_len_new != hrefs_len_last:
            try:
                sleep(3)
                # Получаем список тегов a
                anchors = self.browser.find_elements_by_xpath('//a[contains(@class, "js-letter-list-item")]')
                # Запоминаем предыдущую длину множества
                hrefs_len_last = len(hrefs)
                # Из каждого тега достаём содержимое атрибута href
                for anchor in anchors:
                    hrefs.add(anchor.get_attribute('href'))
                # Получаем новую длину множества для проверки условия остановки
                hrefs_len_new = len(hrefs)
                anchors[-1].send_keys(Keys.PAGE_DOWN)

            except TimeoutError or TimeoutException:
                self.__logger.error("Timeout while waiting for letters list.")
            except StaleElementReferenceException:
                self.__logger.error("Элемент отсутствует на странице")
            except Exception as ex:
                self.__logger.error('Some exception occurred', ex.args)
                print(ex.args)
        # Сохраняем множество в список, чтобы пройтись по элементам в цикле по порядку
        self.hrefs = list(hrefs)

    def save_mails(self):
        """
        Функция сохраняет соедржимое письма в БД
        :return: None
        """
        xpath_from = '//div[@class="letter__author"]/span[@class="letter-contact"]'  # title
        xpath_date = '//div[@class="letter__author"]/div[@class="letter__date"]'  # text
        xpath_header = '//h2[@class="thread__subject"]'  # text
        xpath_body = '//div[@class="letter-body__body-content"]'  # text

        with MongoClient(self.__db_host,
                         self.__db_port,
                         tz_aware=self.__db_tz_aware,
                         username=self.__db_username,
                         password=self.__db_password) as db:
            db_collection = db['MailRu']['Letters']

            for letter in self.hrefs:
                self.browser.get(letter)
                body = WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((By.XPATH, xpath_body)))
                field_from = self.browser.find_element_by_xpath(xpath_from).get_attribute('title')
                field_date = self.browser.find_element_by_xpath(xpath_date).text
                field_header = self.browser.find_element_by_xpath(xpath_header).text
                field_body = body.text
                db_collection.update_one({'from': field_from, 'date': field_date, 'header': field_header},
                                         {'$set':{
                                             'from': field_from,
                                             'date': field_date,
                                             'header': field_header,
                                             'body': field_body
                                         }}, upsert=True)

    # Две функции для упрощения корректной работы с webdriver
    def __enter__(self):
        return self  # привязка к активному объекту with-блока

    def __exit__(self, exception_type, exception_val, trace):
        try:
            self.browser.close()
        except AttributeError:  # у объекта нет метода close
            self.__logger.error('Not closable.')
            return True  # исключение перехвачено


if __name__ == '__main__':
    with MailCollector()as mcollector:
        mcollector.login()
        mcollector.collect_hrefs()
        mcollector.save_mails()
