import json
from typing import Any

from src.external_api import convert_to_rub


def load_transactions(path: str) -> list[dict[str, Any]]:
    """
    Загружает список транзакций из JSON-файла.

    :param path: путь до JSON-файла
    :return: список словарей с данными о транзакциях.
             Пустой список, если файл пустой, содержит не список
             или не найден.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []

    if not isinstance(data, list):
        return []

    return data


def get_transaction_amount(transaction: dict[str, Any]) -> float:
    """
    Возвращает сумму транзакции в рублях.

    Если валюта операции — RUB, возвращает сумму как есть.
    Если валюта — USD или EUR, конвертирует сумму в рубли
    через внешнее API.

    :param transaction: словарь с данными о транзакции
    :return: сумма транзакции в рублях (float)
    """
    operation_amount = transaction.get("operationAmount", {})
    amount = operation_amount.get("amount", 0)
    currency = operation_amount.get("currency", {}).get("code", "RUB")

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return 0.0

    if currency == "RUB":
        return amount

    if currency in ("USD", "EUR"):
        return convert_to_rub(amount, currency)

    return amount


from pathlib import Path

from src.utils import get_transaction_amount, load_transactions

if __name__ == "__main__":
    file_path = Path(__file__).resolve().parent.parent / "data" / "operations.json"
    transactions = load_transactions(file_path)

    for tx in transactions:
        print(get_transaction_amount(tx))
    print(f"Загружено транзакций: {len(transactions)}")
