import requests
import config
import json


class GithubWorker:
    """
    Класс для работы с Github
    """

    def __init__(self):
        """
        Инициализатор класса
        """

        self.__headers = {
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                          "Chrome/90.0.4430.216 YaBrowser/21.5.4.607 Yowser/2.5 Safari/537.36",
            "Accept": "application/vnd.github.v3+json"
        }

        self._base_url = "https://api.github.com/"

        self.last_user = ""
        self.last_user_repositories = []

    def __str__(self):
        lst = self.last_user_repositories['items'] if 'items' in self.last_user_repositories \
            else self.last_user_repositories
        repos_names = [repo['name'] for repo in lst]
        return f"User {self.last_user} has next repositories:\n" + "\n".join(repos_names)

    def get_user_repositories(self, user):
        """
        Получает список репозиториев для пользователя.
        :param user: пользователь для которого нужно получить список репозиториев
        :return: JSON объект списка репозиториев, либо вызывает исключение с кодом ошибки запроса, если ответ не 200 ОК
        """
        user_repositories_url = f"https://api.github.com/users/{user}/repos"
        params = {
            # all, public, private, forks, sources, member, internal. Note: For GitHub AE, can be one of all, private,
            # forks, sources, member, internal
            'type': 'all',
            'page': 1,
            # max 100
            'per_page': 30,
            # created, updated, pushed, full_name
            'sort': 'created'
        }
        response = requests.get(user_repositories_url, headers=self.__headers, params=params)
        if response.status_code == 200:
            self.last_user = user
            self.last_user_repositories.clear()
            self.last_user_repositories = response.json()
            return self.last_user_repositories
        else:
            return response.raise_for_status()

    def search_for_user_repositories(self, user):
        """
        Ищет список репозиториев для пользователя.
        :param user: пользователь для которого нужно найти список репозиториев
        :return: JSON объект списка репозиториев, либо вызывает исключение с кодом ошибки запроса, если ответ не 200 ОК
        """
        search_url = f"{self._base_url}search/repositories?q=user:{user}"
        params = {
                    'sort': 'best match',
                    'order': 'desc',
                    'per_page': 30,
                    'page': 1
                }
        response = requests.get(search_url, headers=self.__headers, params=params)
        if response.status_code == 200:
            self.last_user = user
            self.last_user_repositories.clear()
            self.last_user_repositories = response.json()

            return self.last_user_repositories
        else:
            return response.raise_for_status()

    def save_repository_list(self, file=""):
        """
        Сохраняет список репозиториев в файл. По-умолчанию <user>_repositories.json в папке проекта
        :param file: можно передать имя файла
        :return: ничего не возвращает
        """
        if file == "":
            file = config.pj(config.PROJECT_PATH, f'{self.last_user}_repositories.json')
        else:
            file = config.pj(config.PROJECT_PATH, file)

        with open(file, 'w') as f:
            json.dump(self.last_user_repositories, f)


if __name__ == '__main__':
    from pprint import pprint
    ghw = GithubWorker()
    user_name = input("Для кого найти список репозиториев? Введите login пользователя: ")
    pprint(ghw.search_for_user_repositories(user_name))
    print("*" * 20)
    print(ghw)
    ghw.save_repository_list()
