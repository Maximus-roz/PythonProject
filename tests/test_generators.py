import json
from pathlib import Path

import pytest

from src.generators import (
    card_number_generator,
    filter_by_currency,
    transaction_descriptions,
)


@pytest.mark.parametrize(
    "currency, expected_ids",
    [
        ("USD", [939719570, 142264268, 895315941]),
        ("RUB", [873106923, 594226727]),
        ("EUR", []),
        ("", []),
    ],
)
def test_filter_by_currency_parametrized(transactions, currency, expected_ids):
    result = list(filter_by_currency(transactions, currency))
    assert [tx["id"] for tx in result] == expected_ids


path = Path(__file__).parent.parent / "transactions.txt"
with path.open("r", encoding="utf-8") as file:
    transactions = json.load(file)


@pytest.fixture
def transactions():
    return [
        {
            "id": 939719570,
            "state": "EXECUTED",
            "date": "2018-06-30T02:08:58.425572",
            "operationAmount": {
                "amount": "9824.07",
                "currency": {"name": "USD", "code": "USD"},
            },
            "description": "Перевод организации",
            "from": "Счет 75106830613657916952",
            "to": "Счет 11776614605963066702",
        },
        {
            "id": 142264268,
            "state": "EXECUTED",
            "date": "2019-04-04T23:20:05.206878",
            "operationAmount": {
                "amount": "79114.93",
                "currency": {"name": "USD", "code": "USD"},
            },
            "description": "Перевод со счета на счет",
            "from": "Счет 19708645243227258542",
            "to": "Счет 75651667383060284188",
        },
        {
            "id": 873106923,
            "state": "EXECUTED",
            "date": "2019-03-23T01:09:46.296404",
            "operationAmount": {
                "amount": "43318.34",
                "currency": {"name": "руб.", "code": "RUB"},
            },
            "description": "Перевод со счета на счет",
            "from": "Счет 44812258784861134719",
            "to": "Счет 74489636417521191160",
        },
        {
            "id": 895315941,
            "state": "EXECUTED",
            "date": "2018-08-19T04:27:37.904916",
            "operationAmount": {
                "amount": "56883.54",
                "currency": {"name": "USD", "code": "USD"},
            },
            "description": "Перевод с карты на карту",
            "from": "Visa Classic 6831982476737658",
            "to": "Visa Platinum 8990922113665229",
        },
        {
            "id": 594226727,
            "state": "CANCELED",
            "date": "2018-09-12T21:27:25.241689",
            "operationAmount": {
                "amount": "67314.70",
                "currency": {"name": "руб.", "code": "RUB"},
            },
            "description": "Перевод организации",
            "from": "Visa Platinum 1246377376343588",
            "to": "Счет 14211924144426031657",
        },
    ]


def test_transaction_descriptions_returns_all_descriptions(transactions):
    """Проверяет, что возвращаются описания всех транзакций в правильном порядке."""
    expected = [
        "Перевод организации",
        "Перевод со счета на счет",
        "Перевод со счета на счет",
        "Перевод с карты на карту",
        "Перевод организации",
    ]
    assert list(transaction_descriptions(transactions)) == expected


def test_transaction_descriptions_empty_list():
    """Проверяет работу функции с пустым списком."""
    assert list(transaction_descriptions([])) == []


def test_single_number():
    """Тест генерации одного номера"""
    generator = card_number_generator(1, 1)
    result = list(generator)

    assert len(result) == 1
    assert result[0] == "0000 0000 0000 0001"


def test_small_range():
    """Тест генерации небольшого диапазона"""
    generator = card_number_generator(1, 5)
    result = list(generator)

    expected = [
        "0000 0000 0000 0001",
        "0000 0000 0000 0002",
        "0000 0000 0000 0003",
        "0000 0000 0000 0004",
        "0000 0000 0000 0005",
    ]

    assert result == expected
    assert len(result) == 5


def test_boundary_values():
    """Тест крайних значений диапазона"""
    # Минимальное значение (1)
    generator = card_number_generator(1, 1)
    result = list(generator)
    assert result[0] == "0000 0000 0000 0001"

    # Максимальное 16-значное число
    max_16_digit = 9999999999999999
    generator = card_number_generator(max_16_digit, max_16_digit)
    result = list(generator)
    assert result[0] == "9999 9999 9999 9999"
