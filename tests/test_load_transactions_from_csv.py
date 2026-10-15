import unittest
from unittest.mock import patch, mock_open
from pathlib import Path
import pandas as pd

from src.load_transactions_from_csv import load_transactions_csv


class TestLoadTransactionsCsv(unittest.TestCase):

    @patch("src.load_transactions_from_csv.pd.read_csv")
    def test_load_transactions_csv_success(self, mock_read_csv):
        """Тест успешной загрузки CSV файла."""
        # Подготовка мок-данных
        mock_df = pd.DataFrame(
            {
                "id": [1, 2],
                "state": ["EXECUTED", "PENDING"],
                "date": ["2023-01-01", "2023-01-02"],
                "amount": [100.0, 200.0],
                "currency_name": ["Ruble", "Dollar"],
                "currency_code": ["RUB", "USD"],
                "from": ["Card 1234", "Card 5678"],
                "to": ["Account 1111", "Account 2222"],
                "description": ["Payment 1", "Payment 2"],
            }
        )
        mock_read_csv.return_value = mock_df

        path = Path("fake/path/transactions.csv")
        result = load_transactions_csv(path)

        # Проверки
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], 1)
        self.assertEqual(result[1]["state"], "PENDING")

        # Проверяем, что read_csv был вызван с правильными аргументами
        mock_read_csv.assert_called_once_with(
            path,
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
            encoding="utf-8",
        )

    @patch("src.load_transactions_from_csv.pd.read_csv")
    def test_load_transactions_csv_empty_after_dropna(self, mock_read_csv):
        """Тест: после dropna остаётся пустой DataFrame."""
        mock_df = pd.DataFrame(
            {
                "id": [None],
                "state": [None],
                "date": [None],
                "amount": [None],
                "currency_name": [None],
                "currency_code": [None],
                "from": [None],
                "to": [None],
                "description": [None],
            }
        )
        mock_read_csv.return_value = mock_df

        result = load_transactions_csv(Path("fake.csv"))

        self.assertEqual(result, [])

    @patch("src.load_transactions_from_csv.pd.read_csv")
    def test_load_transactions_csv_returns_empty_on_exception(self, mock_read_csv):
        """Тест: при исключении возвращается пустой список."""
        mock_read_csv.side_effect = FileNotFoundError("File not found")

        result = load_transactions_csv(Path("nonexistent.csv"))

        self.assertEqual(result, [])
        mock_read_csv.assert_called_once()

    @patch("src.load_transactions_from_csv.pd.read_csv")
    def test_load_transactions_csv_empty_dataframe(self, mock_read_csv):
        """Тест: пустой DataFrame возвращает пустой список."""
        mock_read_csv.return_value = pd.DataFrame()

        result = load_transactions_csv(Path("empty.csv"))

        self.assertEqual(result, [])

    @patch("src.load_transactions_from_csv.pd.read_csv")
    def test_load_transactions_csv_multiple_exceptions(self, mock_read_csv):
        """Тест: разные типы исключений обрабатываются одинаково."""
        exceptions = [
            pd.errors.ParserError("Parse error"),
            ValueError("Invalid value"),
            OSError("OS error"),
            Exception("Generic error"),
        ]

        for exc in exceptions:
            with self.subTest(exception=type(exc).__name__):
                mock_read_csv.side_effect = exc
                result = load_transactions_csv(Path("file.csv"))
                self.assertEqual(result, [])

    @patch("src.load_transactions_from_csv.pd.read_csv")
    def test_load_transactions_csv_records_format(self, mock_read_csv):
        """Тест: результат — список словарей (records)."""
        mock_df = pd.DataFrame(
            {
                "id": [1],
                "state": ["EXECUTED"],
                "date": ["2023-01-01"],
                "amount": [150.5],
                "currency_name": ["Ruble"],
                "currency_code": ["RUB"],
                "from": ["Card"],
                "to": ["Account"],
                "description": ["Test"],
            }
        )
        mock_read_csv.return_value = mock_df

        result = load_transactions_csv(Path("file.csv"))

        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], dict)
        self.assertEqual(
            result[0],
            {
                "id": 1,
                "state": "EXECUTED",
                "date": "2023-01-01",
                "amount": 150.5,
                "currency_name": "Ruble",
                "currency_code": "RUB",
                "from": "Card",
                "to": "Account",
                "description": "Test",
            },
        )


class TestLoadTransactionsCsvIntegration(unittest.TestCase):
    """Интеграционные тесты с реальной файловой системой через patch(mock_open)."""

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=(
            "id;state;date;amount;currency_name;currency_code;from;to;description\n"
            "1;EXECUTED;2023-01-01;100;Ruble;RUB;Card;Account;Test\n"
        ),
    )
    @patch("src.load_transactions_from_csv.pd.read_csv")
    def test_with_mocked_open(self, mock_read_csv, mock_file):
        """Пример с патчем open (не влияет на pd.read_csv, но демонстрирует подход)."""
        mock_read_csv.return_value = pd.DataFrame(
            {
                "id": [1],
                "state": ["EXECUTED"],
                "date": ["2023-01-01"],
                "amount": [100],
                "currency_name": ["Ruble"],
                "currency_code": ["RUB"],
                "from": ["Card"],
                "to": ["Account"],
                "description": ["Test"],
            }
        )

        result = load_transactions_csv(Path("file.csv"))

        self.assertEqual(len(result), 1)


class TestLoadTransactionsCsvWithPatchObject(unittest.TestCase):
    """Альтернативный способ через patch.object."""

    @patch.object(pd, "read_csv")
    def test_patch_object_style(self, mock_read_csv):
        mock_read_csv.return_value = pd.DataFrame(
            {
                "id": [42],
                "state": ["DONE"],
                "date": ["2024-01-01"],
                "amount": [999.99],
                "currency_name": ["Euro"],
                "currency_code": ["EUR"],
                "from": ["A"],
                "to": ["B"],
                "description": ["Desc"],
            }
        )

        result = load_transactions_csv(Path("any.csv"))

        self.assertEqual(result[0]["id"], 42)
        self.assertEqual(result[0]["amount"], 999.99)


if __name__ == "__main__":
    unittest.main()
