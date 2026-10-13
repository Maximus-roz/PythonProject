from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest
from src.load_transactions_from_csv import load_transactions


class TestLoadTransactions:

    @patch("src.load_transactions_from_csv.pd.read_csv")
    def test_load_transactions_calls_read_csv_with_correct_args(self, mock_read_csv):
        """Проверяем, что pd.read_csv вызывается с правильными аргументами."""
        # Arrange
        fake_path = Path("/fake/data/transactions.xlsx")
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
        pd.testing.assert_frame_equal(result, expected_df)

    @patch("src.load_transactions_from_csv.pd.read_csv")
    def test_load_transactions_drops_empty_rows(self, mock_read_csv):
        """Проверяем, что пустые строки удаляются через dropna(how='all')."""
        # Arrange
        fake_path = Path("/fake/data/transactions.xlsx")
        df_with_nans = pd.DataFrame(
            {
                "id": [1, None, 3],
                "state": ["done", None, "pending"],
            }
        )
        mock_read_csv.return_value = df_with_nans

        # Act
        result = load_transactions(fake_path)

        # Assert
        assert len(result) == 2
        assert result["id"].tolist() == [1, 3]

    @patch("src.load_transactions_from_csv.pd.read_csv")
    def test_load_transactions_returns_dataframe(self, mock_read_csv):
        """Возвращаемый объект — это DataFrame."""
        mock_read_csv.return_value = pd.DataFrame({"id": [1, 2]})

        result = load_transactions(Path("/fake/file.xlsx"))

        assert isinstance(result, pd.DataFrame)

    @patch("src.load_transactions_from_csv.pd.read_csv")
    def test_load_transactions_raises_if_file_missing(self, mock_read_csv):
        """Если файл отсутствует — пробрасываем исключение."""
        mock_read_csv.side_effect = FileNotFoundError("No such file")

        with pytest.raises(FileNotFoundError):
            load_transactions(Path("/fake/missing.xlsx"))

    def test_load_transactions_with_real_temp_file(self, tmp_path):
        """Интеграционный тест с реальным временным csv-файлом."""
        file_path = tmp_path / "transactions.csv"
        expected = pd.DataFrame(
            {
                "id": [1, 2],
                "state": ["done", "pending"],
                "date": ["2024-01-01", "2024-01-02"],
                "amount": [100.0, 200.0],
                "currency_name": ["RUB", "RUB"],
                "currency_code": ["643", "643"],
                "from": ["A", "C"],
                "to": ["B", "D"],
                "description": ["test1", "test2"],
            }
        )
        expected.to_csv(file_path, sep=";", index=False, header=True)

        result = load_transactions(file_path)

        assert len(result) == 2
        assert list(result.columns) == list(expected.columns)
        assert result["id"].tolist() == [1, 2]
