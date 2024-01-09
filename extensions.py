import requests
from dataclasses import dataclass
from config import keys
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
filehandler = logging.FileHandler('bot.log')
logger.addHandler(filehandler)


class APIException(Exception):
    @property
    def message(self):
        return 'Не удалось сделать запрос к бирже'


@dataclass
class BadRequestError(APIException):
    base: str
    quote: str

    @property
    def message(self):
        return (
            f'Не удалось конвертировать валюту из {self.base} в {self.quote}'
        )


@dataclass
class ExchangeTimeoutError(APIException):
    @property
    def message(self):
        return f'Не удалось получить ответ от удаленного сервера'


@dataclass
class ExchangeTimeoutHTTPClientError(APIException):
    @property
    def message(self):
        return f'Не удалось получить ответ от удаленного сервера за отведенное время'


class HTTPClient:
    timeout_exception = ExchangeTimeoutHTTPClientError
    is_client_error: bool = False

    def make_get_request(self, url):
        res = requests.get(url, timeout=3)
        return res

    def fetch_the_exchange_rate(self, url, base, quote):
        try:
            valid_url = url.format(base=base, quote=quote)
            response = self.make_get_request(valid_url)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            return self.timeout_exception

        if response.json()['success'] == False:
            self.is_client_error = True
            return response.json()['error']['info']

        return response


@dataclass
class ExchangeService:
    http_client: HTTPClient
    api_url = (
        'https://api.exchangeratesapi.io/latest?base={base}&symbols={quote}'
    )

    def get_price(self, base: str, quote: str, amount: float):
        check_base = keys.get(base, False)
        check_quote = keys.get(quote, False)

        if not check_base or not check_quote:
            raise APIException(f'Не удаётся найти валюту {base}')

        if type(amount) not in [float, int]:
            raise APIException(f'Не удаётся перевести {amount} в число.')

        try:
            response = self.http_client.fetch_the_exchange_rate(
                self.api_url, check_base, check_quote
            )
        except self.http_client.timeout_exception:
            raise ExchangeTimeoutError

        if self.http_client.is_client_error:
            logger.error(f'%s', response)
            raise BadRequestError(base, quote)

        result = response.json()['rates'][keys[quote]]

        return result * amount
