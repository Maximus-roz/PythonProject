import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from src.reports import spending_by_category
from src.decorators import DEFAULT_REPORTS_DIR


@pytest.fixture
def sample_df() -> pd.DataFrame:
    return pd.DataFrame({
        "дата_операции": pd.to_datetime([
            "2021-12-30", "2021-12-15", "2021-10-20",
            "2021-09-01", "2021-12-05", "2021-12-01",
        ]),
        "сумма_платежа": [-100.0, -200.0, -50.0, -10.0, 500.0, -30.0],
        "категория": ["Супермаркеты", "Супермаркеты", "Супермаркеты",
                      "Супермаркеты", "Супермаркеты", "Фастфуд"],
    })


def test_spending_by_category_basic(sample_df, tmp_path, monkeypatch):
    monkeypatch.setattr("src.decorators.DEFAULT_REPORTS_DIR", tmp_path)

    res = spending_by_category(sample_df, "Супермаркеты", "2021-12-31")
    # Внутри 3 месяцев: 30.12, 15.12, 20.10, 01.12.
    # 01.09 — вне периода; +500 — доход, отбрасывается; Фастфуд — не наша категория.
    assert len(res) == 3
    assert (res["сумма_платежа"] < 0).all()


def test_spending_by_category_case_insensitive(sample_df, tmp_path, monkeypatch):
    monkeypatch.setattr("src.decorators.DEFAULT_REPORTS_DIR", tmp_path)
    res = spending_by_category(sample_df, "  суперМАРКЕТЫ  ", "2021-12-31")
    assert len(res) == 3


def test_spending_by_category_writes_default_file(sample_df, tmp_path, monkeypatch):
    monkeypatch.setattr("src.decorators.DEFAULT_REPORTS_DIR", tmp_path)
    spending_by_category(sample_df, "Супермаркеты", "2021-12-31")

    files = list(tmp_path.glob("spending_by_category_report_*.json"))
    assert files, "Отчёт-файл не создан"
    payload = json.loads(files[0].read_text(encoding="utf-8"))
    assert len(payload["data"]) == 3


def test_spending_by_category_invalid_date(sample_df):
    with pytest.raises(ValueError):
        spending_by_category(sample_df, "Супермаркеты", "не-дата")


def test_decorator_with_filename(sample_df, tmp_path, monkeypatch):
    """Декоратор с параметром — своё имя файла."""
    from src.decorators import report_to_file
    monkeypatch.setattr("src.decorators.DEFAULT_REPORTS_DIR", tmp_path)

    @report_to_file("custom.json")
    def dummy(df):
        return df.head(1)

    dummy(sample_df)
    assert (tmp_path / "custom.json").exists()