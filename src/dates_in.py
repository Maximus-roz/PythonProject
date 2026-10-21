from datetime import datetime, timedelta
from calendar import monthrange
from pathlib import Path

import pandas as pd

from src.views import cashback_by_card
from src.load_transactions_from_excel import read_operations_clean

def parse_input_datetime(date_string: str) -> datetime:
    """
    Парсит строку формата 'YYYY-MM-DD HH:MM:SS' в объект datetime.

    :param date_string: строка с датой и временем
    :return: объект datetime
    :raises ValueError: если формат строки некорректен
    """
    try:
        return datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        raise ValueError(
            f"Неверный формат даты: '{date_string}'. "
            f"Ожидается 'YYYY-MM-DD HH:MM:SS'. Ошибка: {e}"
        )


def get_month_start(dt: datetime) -> datetime:
    """
    Возвращает начало месяца для переданной даты (00:00:00 первого числа).
    """
    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def get_month_end(dt: datetime) -> datetime:
    """
    Возвращает последний день месяца для переданной даты (23:59:59).
    Полезно для валидации или дополнительной аналитики.
    """
    last_day = monthrange(dt.year, dt.month)[1]
    return dt.replace(day=last_day, hour=23, minute=59, second=59, microsecond=0)


def get_analysis_period(date_string: str) -> dict:
    """
    Формирует диапазон анализа: с начала месяца входящей даты
    по саму входящую дату (включительно).

    :param date_string: строка 'YYYY-MM-DD HH:MM:SS'
    :return: словарь с границами диапазона и метаданными
    """
    dt = parse_input_datetime(date_string)

    period_start = get_month_start(dt)  # 1-е число, 00:00:00
    period_end = dt  # входящая дата как есть

    # Количество дней в диапазоне (включая обе границы)
    days_count = (period_end.date() - period_start.date()).days + 1

    return {
        "input_datetime": dt,
        "period_start": period_start,
        "period_end": period_end,
        "month_end": get_month_end(dt),  # справочно
        "days_in_period": days_count,
        "year": dt.year,
        "month": dt.month,
        "formatted_range": (
            f"{period_start.strftime('%d.%m.%Y %H:%M:%S')} — "
            f"{period_end.strftime('%d.%m.%Y %H:%M:%S')}"
        ),
    }


def format_for_web(period_info: dict) -> str:
    """
    Готовит строку для вывода на веб-странице.
    """
    start = period_info["period_start"].strftime("%d.%m.%Y")
    end = period_info["period_end"].strftime("%d.%m.%Y")
    return (
        f"Период анализа: {start} – {end} "
        f"({period_info['days_in_period']} дн.)"
    )


def main_dt(date_string: str, df: pd.DataFrame) -> dict:
    """
    Главная функция. Принимает строку даты/времени и DataFrame операций,
    возвращает данные для анализа и текст для веб-страницы.
    """
    period_info = get_analysis_period(date_string)

    # Отчёт по картам за выбранный период
    period_info["cards_report"] = cashback_by_card(
        df,
        period_start=period_info["period_start"],
        period_end=period_info["period_end"],
    )

    # Текст для веб-страницы (включает блок по картам)
    period_info["web_text"] = format_for_web(period_info)
    return period_info


# ----------------------------------------------------------------------
# Демонстрация
# ----------------------------------------------------------------------
if __name__ == "__main__":
    base_path = Path(__file__).resolve().parent.parent
    operation_path = base_path / "data" / "operations.xlsx"
    df = read_operations_clean(operation_path)
    result = main_dt("time_in", df)


    print("Входная дата:      ", result["input_datetime"])
    print("Начало периода:    ", result["period_start"])
    print("Конец периода:     ", result["period_end"])
    print("Дней в периоде:    ", result["days_in_period"])
    print("Для веб-страницы:  ", result["web_text"])