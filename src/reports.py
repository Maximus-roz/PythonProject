"""
Отчёт «Траты по категории» за последние 3 месяца.
"""
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Optional

import pandas as pd

from src.decorators import report_to_file

logger = logging.getLogger(__name__)


def _find_date_column(df: pd.DataFrame) -> str:
    """Ищет колонку с датой (с учётом того, что после clean-функции имя — snake_case)."""
    for candidate in ("дата_операции", "дата_платежа", "date"):
        if candidate in df.columns:
            return candidate
    # fallback — первая колонка, где есть слово «дат»
    for col in df.columns:
        if "дат" in col.lower():
            return col
    raise ValueError("Не найдена колонка с датой в DataFrame")


def _find_amount_column(df: pd.DataFrame) -> str:
    for candidate in ("сумма_платежа", "сумма_операции", "amount"):
        if candidate in df.columns:
            return candidate
    raise ValueError("Не найдена колонка с суммой")


@report_to_file()
def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None) -> pd.DataFrame:
    """
    Возвращает траты по указанной категории за последние 3 месяца
    (от переданной даты; если дата не передана — от сегодняшней).

    Параметры:
        transactions : pd.DataFrame — транзакции (после read_operations_clean)
        category     : str — название категории
        date         : str | None — опорная дата в формате "YYYY-MM-DD" (или "DD.MM.YYYY")

    Возвращает:
        pd.DataFrame — отфильтрованные транзакции (только траты, т.е. < 0).
    """
    if transactions.empty:
        logger.warning("Пустой DataFrame на входе")
        return transactions.copy()

    # 1) опорная дата
    if date is None:
        end_date = datetime.now()
    else:
        end_date = pd.to_datetime(date, dayfirst=True, errors="coerce")
        if pd.isna(end_date):
            raise ValueError(f"Не удалось разобрать дату: {date!r}")
        end_date = end_date.to_pydatetime()

    start_date = end_date - relativedelta(months=3)
    logger.info("Период отчёта: %s .. %s, категория=%r", start_date.date(), end_date.date(), category)

    # 2) колонки
    date_col = _find_date_column(transactions)
    amount_col = _find_amount_column(transactions)

    if "категория" not in transactions.columns:
        raise ValueError("В DataFrame нет колонки 'категория'")

    # 3) фильтрация
    df = transactions.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    mask = (
        (df[date_col] >= pd.Timestamp(start_date))
        & (df[date_col] <= pd.Timestamp(end_date))
        & (df["категория"].astype("string").str.strip().str.casefold()
           == category.strip().casefold())
        & (pd.to_numeric(df[amount_col], errors="coerce") < 0)
    )

    result = df.loc[mask].copy()

    logger.info("Найдено %d операций по категории %r", len(result), category)
    return result


if __name__ == "__main__":
    import logging
    from pathlib import Path
    from src.load_transactions_from_excel import read_operations_clean

    logging.basicConfig(level=logging.INFO)

    base_path = Path(__file__).resolve().parent.parent
    ops = read_operations_clean(str(base_path / "data" / "operations.xlsx"))

    res = spending_by_category(ops, "Супермаркеты", "2021-12-31")
    print(res.head())
    print("Всего:", len(res), "| Сумма:", res["сумма_платежа"].sum())

# if __name__ == "__main__":
#     from src.decorators import report_to_file
#
#     @report_to_file("supermarkets_dec_2021.json")
#     def custom_report(transactions, category, date):