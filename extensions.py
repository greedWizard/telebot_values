import json
import requests
from config import keys


class APIException(Exception):
    pass


class ExchangeRatesAPI:
    @staticmethod
    def get_price(base: str, quote: str, amount: float):
        if not (base in keys) or \
            not (quote in keys):
            raise APIException(f'Не удаётся найти валюту {base}')

        if (not isinstance(amount, float)) and (not isinstance(amount, int)):
            raise APIException(f'Не удаётся перевести {amount} в число.')

        r = requests.get(
            f'https://api.exchangeratesapi.io/latest?base={keys[base]}&symbols={keys[quote]}'
        )
        result = json.loads(r.content)['rates'][keys[quote]]

        return result * amount