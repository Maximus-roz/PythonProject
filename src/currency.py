import requests
import xml.etree.ElementTree as ET
import yfinance as yf

import json
import os

def load_user_settings(filename="user_settings.json"):
    # Папка, где лежит сам скрипт (src/)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Поднимаемся на уровень выше — в корень проекта
    project_root = os.path.dirname(base_dir)
    path = os.path.join(project_root, filename)

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Файл настроек не найден: {path}\n"
            f"Ожидался в корне проекта рядом с папкой src."
        )

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_cbr_currency_rates(currencies):
    """
    Получает курсы указанных валют к рублю с сайта ЦБ РФ.
    Возвращает словарь {код_валюты: курс_за_1_единицу}.
    """
    url = "https://www.cbr.ru/scripts/XML_daily.asp"
    response = requests.get(url)
    response.encoding = "windows-1251"
    root = ET.fromstring(response.text)

    rates = {}
    for valute in root.findall("Valute"):
        char_code = valute.find("CharCode").text
        if char_code in currencies:
            nominal = int(valute.find("Nominal").text)
            value = float(valute.find("Value").text.replace(",", "."))
            rates[char_code] = value / nominal
    return rates

def get_stock_prices(tickers):
    """
    Получает последнюю цену закрытия для указанных тикеров.
    Возвращает словарь {тикер: цена}.
    """
    prices = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")
            if not hist.empty:
                prices[ticker] = round(hist["Close"].iloc[-1], 2)
        except Exception as e:
            print(f"Ошибка при получении {ticker}: {e}")
    return prices

def get_market_data(settings_path="user_settings.json"):
    """
    Основная функция: читает настройки и возвращает данные по валютам и акциям.
    """
    settings = load_user_settings(settings_path)

    currencies = settings.get("user_currencies", [])
    stocks = settings.get("user_stocks", [])

    currency_rates = get_cbr_currency_rates(currencies) if currencies else {}
    stock_prices = get_stock_prices(stocks) if stocks else {}

    return {
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }

# Пример вызова
if __name__ == "__main__":
    data = get_market_data()
    print(json.dumps(data, ensure_ascii=False, indent=2))