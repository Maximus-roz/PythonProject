from unittest.mock import patch

import pytest

from src.main import main


@pytest.fixture
def sample_operations():
    return [
        {
            "id": 1,
            "state": "EXECUTED",
            "date": "2023-01-15T10:00:00",
            "operationAmount": {"amount": "1000", "currency": {"code": "RUB"}},
            "description": "Перевод организации",
        },
        {
            "id": 2,
            "state": "EXECUTED",
            "date": "2023-03-20T10:00:00",
            "operationAmount": {"amount": "500", "currency": {"code": "USD"}},
            "description": "Оплата услуг",
        },
        {
            "id": 3,
            "state": "CANCELED",
            "date": "2023-02-10T10:00:00",
            "operationAmount": {"amount": "2000", "currency": {"code": "RUB"}},
            "description": "Перевод другу",
        },
    ]


# 1. Выбор JSON
@patch("src.main.load_transactions")
@patch("builtins.input", side_effect=["1", "EXECUTED", "нет", "нет", "нет"])
@patch("pathlib.Path.exists", return_value=True)
def test_choice_json(mock_exists, mock_input, mock_load, sample_operations, capsys):
    mock_load.return_value = sample_operations
    main()
    out = capsys.readouterr().out
    assert "Найдено транзакций со статусом 'EXECUTED': 2" in out


# 2. Выбор CSV
@patch("src.main.load_transactions_csv")
@patch("src.main.load_transactions")
@patch("builtins.input", side_effect=["2", "EXECUTED", "нет", "нет", "нет"])
@patch("pathlib.Path.exists", return_value=True)
def test_choice_csv(
    mock_exists, mock_input, mock_load_json, mock_load_csv, sample_operations
):
    mock_load_csv.return_value = sample_operations
    main()
    mock_load_csv.assert_called_once()
    mock_load_json.assert_not_called()


# 3. Выбор XLSX
@patch("src.main.load_transactions_excel")
@patch("src.main.load_transactions_csv")
@patch("src.main.load_transactions")
@patch("builtins.input", side_effect=["3", "EXECUTED", "нет", "нет", "нет"])
@patch("pathlib.Path.exists", return_value=True)
def test_choice_excel(
    mock_exists,
    mock_input,
    mock_load_json,
    mock_load_csv,
    mock_load_excel,
    sample_operations,
):
    mock_load_excel.return_value = sample_operations
    main()
    mock_load_excel.assert_called_once()
    mock_load_json.assert_not_called()
    mock_load_csv.assert_not_called()


# 4. Неверный статус
@patch("src.main.load_transactions")
@patch("builtins.input", side_effect=["1", "WRONG", "2"])
@patch("pathlib.Path.exists", return_value=True)
def test_invalid_status(mock_exists, mock_input, mock_load, sample_operations, capsys):
    mock_load.return_value = sample_operations
    with pytest.raises(StopIteration):
        main()
    out = capsys.readouterr().out
    assert "Недопустимый статус" in out


# 5. Сортировка по убыванию -> descending=True
@patch("src.main.sort_by_date")
@patch("src.main.load_transactions")
@patch(
    "builtins.input", side_effect=["1", "EXECUTED", "да", "по убыванию", "нет", "нет"]
)
@patch("pathlib.Path.exists", return_value=True)
def test_sort_descending(
    mock_exists, mock_input, mock_load, mock_sort, sample_operations
):
    mock_load.return_value = sample_operations
    mock_sort.return_value = sample_operations
    main()
    _, kwargs = mock_sort.call_args
    assert kwargs.get("descending") is True


# 6. Сортировка по возрастанию -> descending=False
@patch("src.main.sort_by_date")
@patch("src.main.load_transactions")
@patch(
    "builtins.input",
    side_effect=["1", "EXECUTED", "да", "по возрастанию", "нет", "нет"],
)
@patch("pathlib.Path.exists", return_value=True)
def test_sort_ascending(
    mock_exists, mock_input, mock_load, mock_sort, sample_operations
):
    mock_load.return_value = sample_operations
    mock_sort.return_value = sample_operations
    main()
    _, kwargs = mock_sort.call_args
    assert kwargs.get("descending") is False


# 7. Фильтр только RUB через filter_by_currency
@patch("src.main.filter_by_currency")
@patch("src.main.load_transactions")
@patch("builtins.input", side_effect=["1", "EXECUTED", "нет", "да", "нет"])
@patch("pathlib.Path.exists", return_value=True)
def test_only_rub(
    mock_exists, mock_input, mock_load, mock_filter, sample_operations, capsys
):
    mock_load.return_value = sample_operations
    # Возвращаем генератор, как в реальной функции
    mock_filter.return_value = iter([sample_operations[0]])
    main()
    mock_filter.assert_called_once()
    args, _ = mock_filter.call_args
    assert args[1] == "RUB"
    out = capsys.readouterr().out
    assert "Всего банковских операций в выборке: 1" in out


# 8. Поиск по слову
@patch("src.main.process_bank_search")
@patch("src.main.load_transactions")
@patch("builtins.input", side_effect=["1", "EXECUTED", "нет", "нет", "да", "Перевод"])
@patch("pathlib.Path.exists", return_value=True)
def test_search_by_word(
    mock_exists, mock_input, mock_load, mock_search, sample_operations
):
    mock_load.return_value = sample_operations
    mock_search.return_value = [sample_operations[0]]
    main()
    args, _ = mock_search.call_args
    assert args[1] == "Перевод"


# 9. Пустая выборка
@patch("src.main.process_bank_search", return_value=[])
@patch("src.main.load_transactions")
@patch("builtins.input", side_effect=["1", "EXECUTED", "нет", "нет", "да", "НетТакого"])
@patch("pathlib.Path.exists", return_value=True)
def test_empty_result(
    mock_exists, mock_input, mock_load, mock_search, sample_operations, capsys
):
    mock_load.return_value = sample_operations
    main()
    out = capsys.readouterr().out
    assert "Не найдено ни одной транзакции" in out


# 10. Финальный вывод
@patch("src.main.load_transactions")
@patch("builtins.input", side_effect=["1", "EXECUTED", "нет", "нет", "нет"])
@patch("pathlib.Path.exists", return_value=True)
def test_final_output(mock_exists, mock_input, mock_load, sample_operations, capsys):
    mock_load.return_value = sample_operations
    main()
    out = capsys.readouterr().out
    assert "Распечатываю итоговый список транзакций" in out
    assert "Всего банковских операций в выборке: 2" in out
    # Проверяем, что транзакции напечатаны как JSON
    assert '"id": 1' in out
