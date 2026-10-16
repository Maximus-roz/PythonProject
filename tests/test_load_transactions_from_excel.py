from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from src.load_transactions_from_excel import load_transactions_excel


class TestLoadTransactionsExcel:
    """Тесты для функции load_transactions_excel."""

    @patch("src.load_transactions_from_excel.pd.read_excel")
    def test_load_transactions_excel_returns_list_of_dicts(self, mock_read_excel):
        """Проверяет, что функция возвращает список словарей."""
        mock_df = pd.DataFrame(
            {
                "id": [1, 2],
                "state": ["EXECUTED", "PENDING"],
                "date": ["2024-01-01", "2024-01-02"],
                "amount": [100.0, 200.0],
                "currency_name": ["Ruble", "Dollar"],
                "currency_code": ["RUB", "USD"],
                "from": ["Card 1234", "Card 5678"],
                "to": ["Account 1111", "Account 2222"],
                "description": ["Оплата", "Перевод"],
            }
        )
        mock_read_excel.return_value = mock_df

        result = load_transactions_excel(Path("dummy.xlsx"))

        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(item, dict) for item in result)
        assert result[0]["id"] == 1
        assert result[1]["state"] == "PENDING"

    @patch("src.load_transactions_from_excel.pd.read_excel")
    def test_load_transactions_excel_calls_read_excel_with_correct_args(
        self, mock_read_excel
    ):
        """Проверяет, что pd.read_excel вызывается с правильными аргументами."""
        mock_read_excel.return_value = pd.DataFrame(
            columns=[
                "id",
                "state",
                "date",
                "amount",
                "currency_name",
                "currency_code",
                "from",
                "to",
                "description",
            ]
        )

        test_path = Path("data/transactions_excel.xlsx")
        load_transactions_excel(test_path)

        mock_read_excel.assert_called_once_with(
            test_path,
            names=[
                "id",
                "state",
                "date",
                "amount",
                "currency_name",
                "currency_code",
                "from",
                "to",
                "description",
            ],
            header=0,
        )

    @patch("src.load_transactions_from_excel.pd.read_excel")
    def test_load_transactions_excel_drops_empty_rows(self, mock_read_excel):
        """Проверяет, что пустые строки отбрасываются через dropna(how='all')."""
        mock_df = pd.DataFrame(
            {
                "id": [1, None],
                "state": ["EXECUTED", None],
                "date": ["2024-01-01", None],
                "amount": [100.0, None],
                "currency_name": ["Ruble", None],
                "currency_code": ["RUB", None],
                "from": ["Card 1234", None],
                "to": ["Account 1111", None],
                "description": ["Оплата", None],
            }
        )
        mock_read_excel.return_value = mock_df

        result = load_transactions_excel(Path("dummy.xlsx"))

        assert len(result) == 1
        assert result[0]["id"] == 1

    @patch("src.load_transactions_from_excel.pd.read_excel")
    def test_load_transactions_excel_empty_file(self, mock_read_excel):
        """Проверяет поведение при пустом файле (только заголовки)."""
        mock_read_excel.return_value = pd.DataFrame(
            columns=[
                "id",
                "state",
                "date",
                "amount",
                "currency_name",
                "currency_code",
                "from",
                "to",
                "description",
            ]
        )

        result = load_transactions_excel(Path("empty.xlsx"))

        assert result == []

    @patch("src.load_transactions_from_excel.pd.read_excel")
    def test_load_transactions_excel_file_not_found(self, mock_read_excel):
        """Проверяет проброс исключения, если файл не найден."""
        mock_read_excel.side_effect = FileNotFoundError("File not found")

        with pytest.raises(FileNotFoundError):
            load_transactions_excel(Path("nonexistent.xlsx"))

    @patch("src.load_transactions_from_excel.pd.read_excel")
    def test_load_transactions_excel_uses_path_object(self, mock_read_excel):
        """Проверяет, что Path передаётся в pd.read_excel как есть."""
        mock_read_excel.return_value = pd.DataFrame(
            columns=[
                "id",
                "state",
                "date",
                "amount",
                "currency_name",
                "currency_code",
                "from",
                "to",
                "description",
            ]
        )

        test_path = Path("/tmp/test.xlsx")
        load_transactions_excel(test_path)

        args, _ = mock_read_excel.call_args
        assert isinstance(args[0], Path)
        assert args[0] == test_path
