import requests


class FuckingGreatAdviceAPI:
    URL = "http://fucking-great-advice.ru/api/random"

    def get_advice(self):
        response = requests.get(self.URL)
        return response.json()['text']
