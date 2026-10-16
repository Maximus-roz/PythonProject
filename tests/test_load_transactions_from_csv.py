from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest
from src.load_transactions_from_csv import load_transactions


EXPECTED_COLUMNS = [
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


class TestLoadTransactions:

    @patch("src.load_transactions_from_csv.pd.read_csv")
    def test_load_transactions_calls_read_csv_with_correct_args(self, mock_read_csv):
        """Проверяем, что pd.read_csv вызывается с правильными аргументами."""
        # Arrange
        fake_path = Path("/fake/data/transactions.csv")
        expected_df = pd.DataFrame(
            {
                "id": [1],
                "state": ["done"],
                "date": ["2024-01-01"],
                "amount": [100.0],
                "currency_name": ["RUB"],
                "currency_code": ["643"],
                "from": ["A"],
                "to": ["B"],
                "description": ["test"],
            }
        )
        mock_read_csv.return_value = expected_df

        # Act
        result = load_transactions(fake_path)

        # Assert
        mock_read_csv.assert_called_once_with(
            fake_path,
            sep=";",
            names=EXPECTED_COLUMNS,
            header=0,
        )
        # Функция возвращает list[dict], а не DataFrame
        assert result == expected_df.to_dict(orient="records")

    @patch("src.load_transactions_from_csv.pd.read_csv")
    def test_load_transactions_drops_empty_rows(self, mock_read_csv):
        """Проверяем, что полностью пустые строки удаляются через dropna(how='all')."""
        # Arrange
        fake_path = Path("/fake/data/transactions.csv")
        # Полностью пустая строка (все NaN) + две нормальные
        df_with_nans = pd.DataFrame(
            {
                "id": [1, None, 3],
                "state": ["done", None, "pending"],
                "date": ["2024-01-01", None, "2024-01-03"],
                "amount": [100.0, None, 300.0],
                "currency_name": ["RUB", None, "RUB"],
                "currency_code": ["643", None, "643"],
                "from": ["A", None, "C"],
                "to": ["B", None, "D"],
                "description": ["t1", None, "t3"],
            }
        )
        mock_read_csv.return_value = df_with_nans

        # Act
        result = load_transactions(fake_path)

        # Assert
        assert len(result) == 2
        assert [row["id"] for row in result] == [1, 3]

    @patch("src.load_transactions_from_csv.pd.read_csv")
    def test_load_transactions_returns_list_of_dicts(self, mock_read_csv):
        """Возвращаемый объект — список словарей."""
        mock_read_csv.return_value = pd.DataFrame(
            {"id": [1, 2], "state": ["done", "pending"]}
        )

        result = load_transactions(Path("/fake/file.csv"))

        assert isinstance(result, list)
        assert all(isinstance(row, dict) for row in result)

    @patch("src.load_transactions_from_csv.pd.read_csv")
    def test_load_transactions_raises_if_file_missing(self, mock_read_csv):
        """Если файл отсутствует — пробрасываем исключение."""
        mock_read_csv.side_effect = FileNotFoundError("No such file")

        with pytest.raises(FileNotFoundError):
            load_transactions(Path("/fake/missing.csv"))

