from bs4 import BeautifulSoup
import requests
from re import search, sub, findall
import pandas as pd


class HeadHanterParser:
    """
    Парсер сайта Headhanter
    """

    def __init__(self):
        """
        Инициализатор класса
        """
        # Основной адрес поиска
        self.__base_url = "https://hh.ru"
        self.__search_url = f"{self.__base_url}/search/vacancy"
        # Заголовки
        self.__headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/90.0.4430.216 YaBrowser/21.5.4.607 Yowser/2.5 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml'
        }
        # Базовые параметры
        self.__params = {
            'area': 1,
            'st': 'searchVacancy',
            'items_on_page': 50,
            'page': 0,
            'text': 'Data science'
        }
        # Список параметров
        self._vacancy_list = []
        # Номер следующей страницы, если есть
        self.__next_page = 0

    def get_dataframe(self):
        """
        Функция преобразует имеющийся список вакансий в pandas.DataFrame
        :return: pandas.DataFrame or None
        """
        return pd.DataFrame(self._vacancy_list)

    def get_vacancies_for(self, position='Data science', pages_count=1):
        """
        Собрать список вакансий для должности
        :param position: должность, для которой нужно собрать вакансии
        :param pages_count: количество страниц, которые нужно обработать
        :return: список словарей с описанием вакансии
        """
        self.__params['text'] = position
        self._vacancy_list = []
        while self.__next_page is not None and self.__next_page < pages_count:
            self.__process_soup__(self.__get_soup__())

    def __get_soup__(self):
        """
        Получает html страницу для должности
        :param position: должность, по которой будем собирать вакансии
        :return: BeautifulSoup object
        """

        html_doc = requests.get(self.__search_url, headers=self.__headers, params=self.__params).content
        soup = BeautifulSoup(html_doc, 'html.parser')
        vacancies = soup.findAll('div', attrs={'class': 'vacancy-serp-item'})
        pager_next = soup.find('a', attrs={'data-qa': "pager-next"})
        if pager_next is not None:
            self.__next_page = int(search(r"&page=(\d+)", pager_next.get('href'))[1])
            self.__params['page'] = self.__next_page
        else:
            self.__next_page = None
        return vacancies

    def __process_soup__(self, vacancies_soup: BeautifulSoup) -> list:
        """
        Обрабатывает bs4-object, собирая список словарей с описанием вакансии
        :param html_doc: bs4-object, полученный в функции __get_html__
        :return: список словарей с описанием вакансии
        """
        for vacancy in vacancies_soup:
            dic_vacancy = {}
            title = vacancy.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'})
            dic_vacancy['name'] = ' '.join(title.contents)
            dic_vacancy['link'] = title.get('href')
            compensation = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
            dic_vacancy['compensation'] = "Не указано" if compensation is None \
                else self.__get_compensation_range(''.join(compensation.contents))
            employer = vacancy.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'})
            if employer is None:
                dic_vacancy['employer_name'] = \
                    ''.join(vacancy.find('div', attrs={'class': 'vacancy-serp-item__meta-info-company'}).contents)
                dic_vacancy['employer_link'] = ""
            else:
                dic_vacancy['employer_name'] = ' '.join(employer.contents)
                dic_vacancy['employer_link'] = f"{self.__base_url}{employer.get('href')}"
            dic_vacancy['vacancy_address'] = \
                vacancy.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-address'}).contents[0]
            dic_vacancy['pub_date'] = \
                ''.join(vacancy.find('span', attrs={
                    'class': "vacancy-serp-item__publication-date vacancy-serp-item__publication-date_long"
                }).contents)

            self._vacancy_list.append(dic_vacancy)

    def __get_compensation_range(self, compensation: str) -> tuple:
        """
        Ищет максимальную и минимальную зарплату и валюту в строке
        :param compensation: строка, содержащая данные о зарплате
        :return: кортеж с минимальной зарплатой, максимальной зарплатой, валютой
        """
        try:
            compensation = sub(r'\s', '', compensation)
            min_comp = ''
            max_comp = ''
            min_max = findall(r"\d+", compensation)
            if len(min_max) == 1:
                if search("от", compensation) is not None:
                    min_comp = min_max[0]
                elif search("до", compensation) is not None:
                    max_comp = min_max[0]
                else:
                    min_comp = min_max[0]
                    max_comp = min_max[0]
            else:
                min_comp = min_max[0]
                max_comp = min_max[1]
            currency = search(r"\D+$", compensation)
        except TypeError as e:
            print(compensation)
            print(e.args)

        return min_comp, max_comp, currency[0] if currency is not None else "Unrecognized"


if __name__ == '__main__':
    hh = HeadHanterParser()
    hh.get_vacancies_for('Data Science', 2)
    hh.get_dataframe().to_csv('results.csv')
