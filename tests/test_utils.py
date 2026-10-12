import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from src.utils import get_transaction_amount, load_transactions


# ============================================================
# load_transactions
# ============================================================
class TestLoadTransactions:
    """Тесты для load_transactions."""

    def test_load_valid_file(self, tmp_path: Path) -> None:
        """Корректный JSON со списком — возвращается список словарей."""
        data = [
            {
                "id": 1,
                "operationAmount": {"amount": "100", "currency": {"code": "RUB"}},
            },
            {
                "id": 2,
                "operationAmount": {"amount": "200", "currency": {"code": "USD"}},
            },
        ]
        file_path = tmp_path / "operations.json"
        file_path.write_text(json.dumps(data), encoding="utf-8")

        result = load_transactions(str(file_path))

        assert result == data
        assert isinstance(result, list)
        assert all(isinstance(item, dict) for item in result)

    def test_file_not_found(self, tmp_path: Path) -> None:
        """Несуществующий файл — возвращается пустой список."""
        missing = tmp_path / "no_such_file.json"
        result = load_transactions(str(missing))
        assert result == []

    def test_empty_file(self, tmp_path: Path) -> None:
        """Пустой файл — возвращается пустой список."""
        file_path = tmp_path / "empty.json"
        file_path.write_text("", encoding="utf-8")

        result = load_transactions(str(file_path))
        assert result == []

    def test_invalid_json(self, tmp_path: Path) -> None:
        """Битый JSON — возвращается пустой список."""
        file_path = tmp_path / "broken.json"
        file_path.write_text("{not valid json", encoding="utf-8")

        result = load_transactions(str(file_path))
        assert result == []

    def test_root_is_not_list_dict(self, tmp_path: Path) -> None:
        """Корень — объект, а не список — возвращается пустой список."""
        file_path = tmp_path / "dict.json"
        file_path.write_text(json.dumps({"a": 1}), encoding="utf-8")

        result = load_transactions(str(file_path))
        assert result == []

    def test_root_is_not_list_string(self, tmp_path: Path) -> None:
        """Корень — строка — возвращается пустой список."""
        file_path = tmp_path / "str.json"
        file_path.write_text(json.dumps("hello"), encoding="utf-8")

        result = load_transactions(str(file_path))
        assert result == []

    def test_root_is_empty_list(self, tmp_path: Path) -> None:
        """Валидный пустой список — возвращается []."""
        file_path = tmp_path / "empty_list.json"
        file_path.write_text("[]", encoding="utf-8")

        result = load_transactions(str(file_path))
        assert result == []


# ============================================================
# get_transaction_amount
# ============================================================
class TestGetTransactionAmount:
    """Тесты для get_transaction_amount."""

    def test_rub_no_conversion(self) -> None:
        """RUB — сумма возвращается без изменений, API не вызывается."""
        tx = {
            "operationAmount": {
                "amount": "1000.50",
                "currency": {"code": "RUB"},
            }
        }

        with patch("src.utils.convert_to_rub") as mock_convert:
            result = get_transaction_amount(tx)

        assert result == 1000.50
        mock_convert.assert_not_called()

    def test_usd_calls_conversion(self) -> None:
        """USD — вызывается convert_to_rub с правильными аргументами."""
        tx = {
            "operationAmount": {
                "amount": "100",
                "currency": {"code": "USD"},
            }
        }

        with patch("src.utils.convert_to_rub", return_value=9200.0) as mock_convert:
            result = get_transaction_amount(tx)

        assert result == 9200.0
        mock_convert.assert_called_once_with(100.0, "USD")

    def test_eur_calls_conversion(self) -> None:
        """EUR — вызывается convert_to_rub."""
        tx = {
            "operationAmount": {
                "amount": "50",
                "currency": {"code": "EUR"},
            }
        }

        with patch("src.utils.convert_to_rub", return_value=5250.0) as mock_convert:
            result = get_transaction_amount(tx)

        assert result == 5250.0
        mock_convert.assert_called_once_with(50.0, "EUR")

    def test_unknown_currency_returns_amount(self) -> None:
        """Неизвестная валюта — возвращается исходная сумма, API не вызывается."""
        tx = {
            "operationAmount": {
                "amount": "10",
                "currency": {"code": "GBP"},
            }
        }

        with patch("src.utils.convert_to_rub") as mock_convert:
            result = get_transaction_amount(tx)

        assert result == 10.0
        mock_convert.assert_not_called()

    def test_missing_operation_amount(self) -> None:
        """Нет ключа operationAmount — возвращается 0.0."""
        result = get_transaction_amount({})
        assert result == 0.0

    def test_missing_amount(self) -> None:
        """Нет ключа amount — возвращается 0.0."""
        tx = {"operationAmount": {"currency": {"code": "RUB"}}}
        result = get_transaction_amount(tx)
        assert result == 0.0

    def test_invalid_amount_type(self) -> None:
        """amount не число — возвращается 0.0."""
        tx = {
            "operationAmount": {
                "amount": "not-a-number",
                "currency": {"code": "RUB"},
            }
        }
        result = get_transaction_amount(tx)
        assert result == 0.0

    def test_missing_currency_defaults_to_rub(self) -> None:
        """Нет ключа currency — валюта по умолчанию RUB, конвертация не вызывается."""
        tx = {"operationAmount": {"amount": "100"}}

        with patch("src.utils.convert_to_rub") as mock_convert:
            result = get_transaction_amount(tx)

        assert result == 100.0
        mock_convert.assert_not_called()

    def test_amount_as_number_not_string(self) -> None:
        """amount может прийти числом, а не строкой."""
        tx = {
            "operationAmount": {
                "amount": 250,
                "currency": {"code": "RUB"},
            }
        }
        result = get_transaction_amount(tx)
        assert result == 250.0
