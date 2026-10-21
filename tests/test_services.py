import pytest
from src.services import investment_bank


def test_with_list_negative_amounts():
    txs = [{"Дата операции": "2024-05-01", "Сумма операции": -1712}]
    assert investment_bank("2024-05", txs, 50) == 38.0


def test_filter_by_month():
    txs = [
        {"Дата операции": "2024-05-01", "Сумма операции": -1712},
        {"Дата операции": "2024-06-01", "Сумма операции": -3001},
    ]
    assert investment_bank("2024-05", txs, 50) == 38.0


def test_positive_transactions_skipped():
    txs = [{"Дата операции": "2024-05-01", "Сумма операции": 5046}]
    assert investment_bank("2024-05", txs, 50) == 0.0


def test_invalid_month():
    with pytest.raises(ValueError):
        investment_bank("2024/05", [], 50)


def test_invalid_limit():
    with pytest.raises(ValueError):
        investment_bank("2024-05", [], 0)


def test_load_from_excel_smoke():
    # Проверка, что функция умеет читать реальный файл без падения
    saved = investment_bank("2021-12", limit=50)
    assert isinstance(saved, float)
    assert saved >= 0