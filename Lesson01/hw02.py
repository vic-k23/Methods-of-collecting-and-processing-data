import requests
import config


class OpenWeather:
    """
    Класс для работы с сайтом openweathermap.org
    """

    def __init__(self):
        """
        Инициализация основных переменных
        """
        self.__headers = {
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                          "Chrome/90.0.4430.216 YaBrowser/21.5.4.607 Yowser/2.5 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;"
                      "q=0.8,application/signed-exchange;v=b3;q=0.9"
        }
        self._baseurl = "http://api.openweathermap.org/data/2.5/weather"
        self.__api_key = config.CONFIG['OpenWeather']['open_weather_api_key']
        self.weather_json = {}
        self.wind_directions = {0: "С", 45: "СВ", 90: "В", 135: "ЮВ", 180: "Ю", 225: "ЮЗ", 270: "З", 315: "СЗ"}
        self.vane = ""

    def __str__(self):
        return f"Сейчас в г.{self.weather_json['name']} "\
              f"{self.weather_json['weather'][0]['description']}, "\
              f"температура воздуха {round(self.weather_json['main']['temp'])}C, "\
              f"ощущается как {round(self.weather_json['main']['feels_like'])}C, "\
              f"давление {round(float(self.weather_json['main']['pressure']) * 0.7501)} мм рт. ст.,"\
              f"влажность {self.weather_json['main']['humidity']}%, "\
              f"ветер {self.vane} {self.weather_json['wind']['speed']} м/с"

    def get_weather_for(self, city):
        parameters = {
            'q': city,
            'units': 'metric',
            'lang': 'ru',
            'appid': self.__api_key
        }
        response = requests.get(self._baseurl, headers=self.__headers, params=parameters)
        if response.status_code == 200:
            self.weather_json = response.json()
            tester = 360
            for k in self.wind_directions.keys():
                if abs(tester) > abs(k - self.weather_json['wind']['deg']):
                    tester = k - self.weather_json['wind']['deg']
            self.vane = self.wind_directions.get(tester+self.weather_json['wind']['deg'])
        else:
            response.raise_for_status()


if __name__ == '__main__':
    weather = OpenWeather()
    weather.get_weather_for('Москва')
    print(weather)
