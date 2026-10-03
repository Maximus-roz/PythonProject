import json
from pathlib import Path


def filter_by_currency(transactions, currency):
    """Фильтрует транзакции по коду валюты.

    Проходит по списку транзакций и возвращает только те, у которых
    код валюты операции совпадает с заданным.

    :param transactions: Список транзакций (словарей) для фильтрации.
    :param currency: Код валюты для фильтрации (например, "USD", "RUB").
    :yield: Транзакция (словарь), валюта которой совпадает с заданной.
    """
    for x in transactions:
        if x["operationAmount"]["currency"]["code"] == currency:
            yield x


def transaction_descriptions(transactions):
    """Возвращает описания транзакций по очереди.

    Генерирует описание каждой операции из переданного списка транзакций.
    Если у транзакции отсутствует поле "description", возвращается пустая строка.

    :param transactions: Список транзакций (словарей).
    :yield: Описание транзакции (строка) или пустая строка, если описание отсутствует.
    """
    for x in transactions:
        yield x.get("description", "")


def card_number_generator(start, end):
    """Генерирует номера банковских карт в формате XXXX XXXX XXXX XXXX.

    Формирует последовательные 16-значные номера карт в заданном диапазоне
    и разбивает их на группы по 4 цифры, разделённые пробелами.

    :param start: Начальное число диапазона (включительно).
    :param end: Конечное число диапазона (включительно).
    :yield: Отформатированный номер карты (строка вида "XXXX XXXX XXXX XXXX").
    """
    for number in range(start, end + 1):
        raw = f"{number:016d}"
        formatted = " ".join(raw[i : i + 4] for i in range(0, len(raw), 4))
        yield formatted


if __name__ == "__main__":
    path = Path(__file__).parent.parent / "transactions.txt"
    with path.open("r", encoding="utf-8") as file:
        transactions = json.load(file)