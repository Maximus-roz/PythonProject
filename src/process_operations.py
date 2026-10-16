import json
from pathlib import Path
from typing import Counter

from src.generators import transaction_descriptions
from src.utils import load_transactions


def process_bank_operations(
    operations: list[dict], transaction_descriptions_list: list
) -> dict:
    """Возвращает словарь, в котором ключи — это названия категорий,
    а значения — это количество операций в каждой категории."""
    descriptions = [op.get("description") for op in operations]
    # Counter посчитает частоту каждого значения
    counter = Counter(descriptions)
    # Оставляем только нужные категории, сохраняя их порядок и
    # включая категории с нулевым количеством
    result = {
        category: counter.get(category, 0) for category in transaction_descriptions_list
    }
    return result


if __name__ == "__main__":
    file_path = Path(__file__).resolve().parent.parent

    operations_path = file_path / "data" / "operations.json"
    operations = load_transactions(str(operations_path))

    transactions_path = file_path / "transactions.txt"
    with transactions_path.open("r", encoding="utf-8") as file:
        transactions = json.load(file)
    transaction_descriptions_list = list(transaction_descriptions(transactions))
