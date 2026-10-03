import pytest
import json
from src.generators import filter_by_currency

'''
with open("transactions.txt", "r", encoding="utf-8") as file:
    print (file.read())


with open("transactions.txt", "r", encoding="utf-8") as file:
    transactions = json.load(file)


def transactions():
    file_path = Path(__file__).parent.parent / "src" / "transactions.txt"
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)
'''


@pytest.mark.parametrize(
    "currency, expected_ids",
    [
        ("USD", [1, 3]),
        ("RUB", [2]),
        ("EUR", []),
        ("GBP", []),
    ],
)
def test_filter_by_currency_parametrized(sample_transactions, currency, expected_ids):
    result = list(filter_by_currency(sample_transactions, currency))
    assert [t["id"] for t in result] == expected_ids