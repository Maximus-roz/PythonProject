import os
from dotenv import load_dotenv
load_dotenv()
import requests

API_URL = "https://api.apilayer.com/exchangerates_data/convert"


def convert_to_rub(amount: float, from_currency: str) -> float:
    """
    Конвертирует сумму из указанной валюты в рубли через
    Exchange Rates Data API (apilayer.com).

    :param amount: сумма для конвертации
    :param from_currency: код валюты (например, "USD", "EUR")
    :return: сумма в рублях (float).
    Если API недоступно или ключ отсутствует — возвращает 0.0.
    """
    api_key = os.getenv("EXCHANGE_RATES_API_KEY")
    if not api_key:
        print('проблема с API KEY')
        return 0.0

    headers = {"apikey": api_key}
    params = {
        "to": "RUB",
        "from": from_currency,
        "amount": amount,
    }

    try:
        response = requests.get(API_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return float(data["result"])

    except (requests.RequestException, KeyError, TypeError, ValueError):
        return 0.0