import logging

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger('responses')


class CBRAPI:
    URL = "https://www.cbr-xml-daily.ru/daily.xml"

    def __init__(self, filters_list):
        self.filters = {x: {
            'name': None,
            'value': 0
        } for x in filters_list}

    def get_ex_rates(self) -> dict:
        r = requests.get(self.URL, stream=True)
        logger.debug({"response": r.content})
        elements = BeautifulSoup(r.content, 'xml').find('ValCurs').find_all("Valute")

        for elem in elements:
            for _filter in self.filters:
                if elem.find("CharCode").text == _filter:
                    self.filters[_filter]['name'] = elem.find('Name').text.lower()
                    self.filters[_filter]['value'] = float(elem.find("Value").text.replace(',', '.')) / float(
                        elem.find("Nominal").text.replace(',', '.'))

        return self.filters