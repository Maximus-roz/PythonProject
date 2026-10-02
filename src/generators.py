import json

def filter_by_currency(transactions, currency):
    for x in transactions:
        if x["operationAmount"]["currency"]["code"] == currency:
            yield x

with open("transactions.txt", "r", encoding="utf-8") as file:
    transactions = json.load(file)

def transaction_descriptions(transactions):
    for x in transactions:
        yield x.get("description", "")


def card_number_generator(start, end):
    for number in range(start, end+1):
        raw = f"{number:016d}"
        formatted = " ".join(raw[i:i+4] for i in range(0, len(raw), 4))
        yield formatted



