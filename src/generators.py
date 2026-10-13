import json
from pathlib import Path
import pandas as pd

def filter_by_currency(transactions, currency):
    """Фильтрует транзакции по коду валюты.

     :param transactions: DataFrame с транзакциями.
    :param currency: Код валюты для фильтрации (например, "USD", "RUB").
    :return: DataFrame с отфильтрованными транзакциями.
    """

    transactions_filtered = transactions.loc[transactions["currency_code"] == currency]
    return transactions_filtered

    # for x in transactions:
    #     if x["operationAmount"]["currency"]["code"] == currency:
    #         yield x


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

if __name__ == '__main__':
    path = Path(__file__).parent.parent / "data" / "transactions.csv"
    currency = "USD"
    df = pd.read_csv(
        path, sep=";",
        names=["id", "state", "date", "amount", "currency_name",
               "currency_code", "from", "to", "description"],
        header=0,
    ).dropna(how="all")
    result = filter_by_currency(df, currency)
    print(result)


    # result = get_survived(df)
    # print(result)
# if __name__ == "__main__":
#     path = Path(__file__).parent.parent / "transactions.txt"
#     with path.open("r", encoding="utf-8") as file:
#         transactions = json.load(file)
