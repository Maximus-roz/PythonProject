# tests/test_main.py
import builtins
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd
import pytest

from src import main as main_module
from src.main import (
    get_datetime_from_user,
    get_top_transactions,
    print_cards_report,
    print_market_data,
    print_top_transactions,
    run_report,
)


# ---------- фикстуры ----------

@pytest.fixture
def df_ops() -> pd.DataFrame:
    """Минимальный DataFrame, совместимый с read_operations_clean."""
    return pd.DataFrame(
        {
            "дата_операции": pd.to_datetime(
                [
                    "2021-12-01 10:00:00",
                    "2021-12-15 12:30:00",
                    "2021-12-31 23:59:00",
                    "2022-01-01 00:00:01",  # вне периода
                    "2021-11-30 09:00:00",  # вне периода
                ]
            ),
            "номер_карты": ["*7197", "*5091", "*4556", "*7197", "*5091"],
            "статус": ["OK", "OK", "FAILED", "OK", "OK"],
            "категория": ["Супермаркеты", "Каршеринг", "Переводы", "Фастфуд", "Аптеки"],
            "описание": ["Колхоз", "Ситидрайв", "Иван С.", "Rumyanyj Khleb", "Аптека Вита"],
            "сумма_операции": [-100.0, -5000.0, -9999.0, -50.0, -30.0],
        }
    )


@pytest.fixture
def cards_report() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "карта": ["*7197", "*5091"],
            "сумма_расходов": [1234.56, 5000.00],
            "кэшбэк": [12, 50],
        }
    )


# ---------- get_top_transactions ----------

def test_get_top_transactions_filters_period_and_status(df_ops):
    res = get_top_transactions(
        df_ops,
        period_start=datetime(2021, 12, 1),
        period_end=datetime(2021, 12, 31, 23, 59, 59),
        top_n=5,
    )
    # В период попадают 3 строки: 01.12 OK, 15.12 OK, 31.12 FAILED.
    # FAILED отфильтровывается → остаётся 2.
    assert len(res) == 2
    # Обе — успешные
    assert set(res["номер_карты"]) == {"*7197", "*5091"}


def test_get_top_transactions_sorted_by_abs_desc(df_ops):
    res = get_top_transactions(
        df_ops,
        period_start=datetime(2021, 12, 1),
        period_end=datetime(2021, 12, 31, 23, 59, 59),
        top_n=5,
    )
    # -5000 должен быть первым (|−5000| > |−100|)
    assert res.iloc[0]["сумма_операции"] == -5000.0
    assert res.iloc[1]["сумма_операции"] == -100.0


def test_get_top_transactions_top_n(df_ops):
    res = get_top_transactions(
        df_ops,
        period_start=datetime(2021, 12, 1),
        period_end=datetime(2021, 12, 31, 23, 59, 59),
        top_n=1,
    )
    assert len(res) == 1
    assert res.iloc[0]["сумма_операции"] == -5000.0


def test_get_top_transactions_empty_period(df_ops):
    res = get_top_transactions(
        df_ops,
        period_start=datetime(2020, 1, 1),
        period_end=datetime(2020, 1, 31),
    )
    assert res.empty


# ---------- print_cards_report ----------

def test_print_cards_report_output(cards_report, capsys):
    print_cards_report(cards_report)
    out = capsys.readouterr().out
    assert "Кэшбэк по картам" in out
    assert "*7197" in out
    assert "*5091" in out
    assert "ИТОГО" in out
    assert "1,234.56" in out
    assert "5,000.00" in out


def test_print_cards_report_empty(capsys):
    print_cards_report(pd.DataFrame(columns=["карта", "сумма_расходов", "кэшбэк"]))
    out = capsys.readouterr().out
    assert "Нет операций по картам" in out


# ---------- print_top_transactions ----------

def test_print_top_transactions_output(capsys):
    top = pd.DataFrame(
        {
            "дата_операции": [pd.Timestamp("2021-12-15 12:30:00")],
            "номер_карты": ["*5091"],
            "категория": ["Каршеринг"],
            "описание": ["Ситидрайв"],
            "сумма_операции": [-5000.0],
        }
    )
    print_top_transactions(top, top_n=5)
    out = capsys.readouterr().out
    assert "Топ-5 транзакций" in out
    assert "15.12.2021 12:30:00" in out
    assert "*5091" in out
    assert "Каршеринг" in out
    assert "Ситидрайв" in out
    assert "-5,000.00 ₽" in out


def test_print_top_transactions_empty(capsys):
    print_top_transactions(pd.DataFrame(), top_n=5)
    out = capsys.readouterr().out
    assert "Нет транзакций" in out


def test_print_top_transactions_missing_optional_fields(capsys):
    """Нет номер_карты/категории/описания — должны подставиться прочерки."""
    top = pd.DataFrame(
        {
            "дата_операции": [pd.Timestamp("2021-12-15")],
            "сумма_операции": [-100.0],
        }
    )
    print_top_transactions(top, top_n=1)
    out = capsys.readouterr().out
    assert "—" in out
    assert "-100.00 ₽" in out


# ---------- print_market_data ----------

def test_print_market_data_output(capsys):
    print_market_data(
        {
            "currency_rates": {"USD": 75.1234, "EUR": 85.5678},
            "stock_prices": {"AAPL": 150.25, "MSFT": 300.5},
        }
    )
    out = capsys.readouterr().out
    assert "Курсы валют" in out
    assert "USD: 75.1234 ₽" in out
    assert "EUR: 85.5678 ₽" in out
    assert "Цены акций" in out
    assert "AAPL: 150.25" in out
    assert "MSFT: 300.50" in out


def test_print_market_data_empty(capsys):
    print_market_data({"currency_rates": {}, "stock_prices": {}})
    out = capsys.readouterr().out
    assert "Нет данных по валютам" in out
    assert "Нет данных по акциям" in out


# ---------- get_datetime_from_user ----------

def test_get_datetime_from_user_valid(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda *_: "2021-12-31 10:00:00")
    assert get_datetime_from_user() == "2021-12-31 10:00:00"


def test_get_datetime_from_user_retries(monkeypatch, capsys):
    inputs = iter(["не-дата", "тоже нет", "2021-12-31 10:00:00"])
    monkeypatch.setattr(builtins, "input", lambda *_: next(inputs))
    result = get_datetime_from_user()
    out = capsys.readouterr().out
    assert result == "2021-12-31 10:00:00"
    assert out.count("Неверный формат") == 2


# ---------- run_report (интеграционный, с моками) ----------

def test_run_report_smoke(monkeypatch, df_ops, capsys, tmp_path):
    # 1) input — отдаём валидную дату
    monkeypatch.setattr(builtins, "input", lambda *_: "2021-12-31 23:59:59")

    # 2) чтение Excel — подменяем на фикстуру
    monkeypatch.setattr(main_module, "read_operations_clean", lambda _p: df_ops)

    # 3) main_dt — возвращаем готовый result
    period_start = datetime(2021, 10, 1)
    period_end = datetime(2021, 12, 31, 23, 59, 59)
    fake_result = {
        "period_start": period_start,
        "period_end": period_end,
        "cards_report": pd.DataFrame(
            {
                "карта": ["*7197"],
                "сумма_расходов": [100.0],
                "кэшбэк": [1],
            }
        ),
    }
    monkeypatch.setattr(main_module, "main_dt", lambda _d, _df: fake_result)
    monkeypatch.setattr(main_module, "format_for_web", lambda r: "WEB-FORMATTED")

    # 4) рыночные данные — без сети
    monkeypatch.setattr(
        main_module,
        "get_market_data",
        lambda: {
            "currency_rates": {"USD": 75.0},
            "stock_prices": {"AAPL": 150.0},
        },
    )

    # 5) Path для data/operations.xlsx — не важно, т.к. read подменён,
    #    но подстрахуемся: создадим пустой файл в tmp_path и подменим base.
    #    Проще: monkeypatch Path(__file__).resolve().parent.parent не нужно,
    #    т.к. read_operations_clean игнорирует аргумент.

    run_report()

    out = capsys.readouterr().out
    assert "WEB-FORMATTED" in out
    assert "Кэшбэк по картам" in out
    assert "*7197" in out
    assert "Топ-5 транзакций" in out
    assert "Курсы валют" in out
    assert "USD: 75.0000 ₽" in out
    assert "AAPL: 150.00" in out