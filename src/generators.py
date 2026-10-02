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



