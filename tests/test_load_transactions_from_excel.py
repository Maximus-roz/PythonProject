from pathlib import Path
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest

from src.load_transactions_from_excel import load_transactions


class TestLoadTransactions:
    """Тесты для функции load_transactions."""

    @patch("src.load_transactions_from_excel.pd.read_excel")
    def test_calls_read_excel_with_correct_args(self, mock_read_excel):
        """Проверяем, что pd.read_excel вызывается с нужными аргументами."""
        # Готовим фейковый DataFrame
        fake_df = pd.DataFrame(
            [
                {
                    "id": 1,
                    "state": "EXECUTED",
                    "date": "2024-01-01",
                    "amount": 100,
                    "currency_name": "USD",
                    "currency_code": "USD",
                    "from": "A",
                    "to": "B",
                    "description": "test",
                }
            ]
        )
        # Мок для dropna().to_dict() цепочки
        mock_read_excel.return_value = MagicMock(
            dropna=MagicMock(return_value=MagicMock(
                to_dict=MagicMock(return_value=fake_df.to_dict(orient="records"))
            ))
        )

        path = Path("/tmp/test.xlsx")
        result = load_transactions(path)

        # Проверяем аргументы вызова
        mock_read_excel.assert_called_once_with(
            path,
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
        assert result == fake_df.to_dict(orient="records")
        assert isinstance(result, list)
        assert isinstance(result[0], dict)

    @patch("src.load_transactions_from_excel.pd.read_excel")
    def test_dropna_called_with_how_all(self, mock_read_excel):
        """Проверяем, что dropna вызывается с how='all'."""
        mock_df = MagicMock()
        mock_read_excel.return_value = mock_df
        mock_df.dropna.return_value.to_dict.return_value = []

        load_transactions(Path("/tmp/test.xlsx"))

        mock_df.dropna.assert_called_once_with(how="all")
        mock_df.dropna.return_value.to_dict.assert_called_once_with(orient="records")

    @patch("src.load_transactions_from_excel.pd.read_excel")
    def test_empty_dataframe_returns_empty_list(self, mock_read_excel):
        """Пустой DataFrame → пустой список."""
        empty_df = pd.DataFrame(
            columns=[
                "id", "state", "date", "amount",
                "currency_name", "currency_code",
                "from", "to", "description",
            ]
        )
        mock_read_excel.return_value = empty_df

        result = load_transactions(Path("/tmp/empty.xlsx"))

        assert result == []

    @patch("src.load_transactions_from_excel.pd.read_excel")
    def test_returns_list_of_dicts(self, mock_read_excel):
        """Возвращаемый тип — list[dict]."""
        df = pd.DataFrame(
            [
                {"id": 1, "state": "EXECUTED", "date": "2024-01-01",
                 "amount": 10, "currency_name": "USD", "currency_code": "USD",
                 "from": "A", "to": "B", "description": "x"},
                {"id": 2, "state": "PENDING", "date": "2024-01-02",
                 "amount": 20, "currency_name": "EUR", "currency_code": "EUR",
                 "from": "C", "to": "D", "description": "y"},
            ]
        )
        mock_read_excel.return_value = df

        result = load_transactions(Path("/tmp/test.xlsx"))

        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(row, dict) for row in result)
        assert result[0]["id"] == 1
        assert result[1]["currency_code"] == "EUR"