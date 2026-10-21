from datetime import datetime
from pathlib import Path

import pandas as pd

from src.dates_in import main_dt, parse_input_datetime, format_for_web
from src.load_transactions_from_excel import read_operations_clean
from src.currency import get_market_data

def get_datetime_from_user() -> str:
    """
    Запрашивает у пользователя дату в формате 'YYYY-MM-DD HH:MM:SS'
    и возвращает её строкой (после успешной валидации).
    """
    while True:
        time_in = input("Введите дату (в формате гггг-мм-дд чч:мм:сс): ").strip()
        try:
            parse_input_datetime(time_in)  # валидация через dates_in
            return time_in
        except ValueError:
            print("Неверный формат! Попробуйте снова.")


def get_top_transactions(
    df: pd.DataFrame,
    period_start: datetime,
    period_end: datetime,
    top_n: int = 5,
) -> pd.DataFrame:
    """
    Возвращает топ-N транзакций по сумме платежа (по модулю) за период.
    Учитываются только успешные операции.
    """
    data = df.copy()

    # Фильтр по периоду (включительно)
    data = data[
        (data["дата_операции"] >= period_start)
        & (data["дата_операции"] <= period_end)
    ]

    # Только успешные операции
    data = data[data["статус"].eq("OK")]

    # Сортируем по модулю суммы платежа (крупнейшие операции сверху)
    data = data.assign(
        _abs_amount=data["сумма_операции"].abs()
    ).sort_values("_abs_amount", ascending=False)

    # Оставляем нужные колонки (гибко — только те, что есть)
    preferred_cols = [
        "дата_операции",
        "номер_карты",
        "категория",
        "описание",
        "сумма_операции",
    ]
    cols = [c for c in preferred_cols if c in data.columns]

    return data[cols].head(top_n).reset_index(drop=True)


def print_cards_report(cards_report: pd.DataFrame) -> None:
    """Печатает отчёт по картам в читаемом виде."""
    if cards_report.empty:
        print("\nНет операций по картам за выбранный период.")
        return

    print("\n=== Кэшбэк по картам ===")
    header = f"{'Карта':<8} {'Сумма расходов, ₽':>20} {'Кэшбэк, ₽':>12}"
    print(header)
    print("-" * len(header))
    for _, row in cards_report.iterrows():
        print(
            f"{row['карта']:<8} "
            f"{row['сумма_расходов']:>20,.2f} "
            f"{row['кэшбэк']:>12}"
        )
    total_expenses = cards_report["сумма_расходов"].sum()
    total_cashback = cards_report["кэшбэк"].sum()
    print("-" * len(header))
    print(
        f"{'ИТОГО':<8} "
        f"{total_expenses:>20,.2f} "
        f"{total_cashback:>12}"
    )


def print_top_transactions(top_df: pd.DataFrame, top_n: int = 5) -> None:
    """Печатает топ-N транзакций по сумме платежа."""
    print(f"\n=== Топ-{top_n} транзакций по сумме платежа ===")
    if top_df.empty:
        print("Нет транзакций за выбранный период.")
        return

    for i, row in top_df.iterrows():
        date_str = (
            row["дата_операции"].strftime("%d.%m.%Y %H:%M:%S")
            if pd.notna(row.get("дата_операции"))
            else "—"
        )
        card = row.get("номер_карты", "") or "—"
        category = row.get("категория", "") or "—"
        description = row.get("описание", "") or "—"
        amount = row["сумма_операции"]
        print(
            f"{i + 1}. {date_str} | карта: {card} | "
            f"{category} | {description} | {amount:,.2f} ₽"
        )

def print_market_data(market_data: dict) -> None:
    """Печатает курсы валют и цены акций в читаемом виде."""
    currency_rates = market_data.get("currency_rates", {})
    stock_prices = market_data.get("stock_prices", {})

    print("\n=== Курсы валют (ЦБ РФ) ===")
    if currency_rates:
        for code, rate in currency_rates.items():
            print(f"{code}: {rate:,.4f} ₽")
    else:
        print("Нет данных по валютам.")

    print("\n=== Цены акций ===")
    if stock_prices:
        for ticker, price in stock_prices.items():
            print(f"{ticker}: {price:,.2f}")
    else:
        print("Нет данных по акциям.")

def run_report() -> None:
    """
    Главная точка входа:
      1. Получает дату от пользователя.
      2. Загружает данные из Excel.
      3. Считает отчёт по картам и топ-5 транзакций.
      4. Выводит всё в консоль, включая курсы валют и цены акций.
    """
    # 1. Дата от пользователя
    date_string = get_datetime_from_user()

    # 2. Загрузка данных
    base_path = Path(__file__).resolve().parent.parent
    operation_path = base_path / "data" / "operations.xlsx"
    df = read_operations_clean(operation_path)

    # 3. Расчёт через dates_in (там уже вызывается cashback_by_card)
    result = main_dt(date_string, df)

    # 4. Вывод
    print("\n" + "=" * 60)
    print(format_for_web(result))
    print("=" * 60)

    # Отчёт по картам
    print_cards_report(result["cards_report"])

    # Топ-5 транзакций
    top_df = get_top_transactions(
        df,
        period_start=result["period_start"],
        period_end=result["period_end"],
        top_n=5,
    )
    print_top_transactions(top_df, top_n=5)

    # Данные по валютам и акциям
    market_data = get_market_data()
    print_market_data(market_data)

if __name__ == "__main__":
    run_report()