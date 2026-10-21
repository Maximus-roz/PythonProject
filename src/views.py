from datetime import datetime


def greeting():
    hour = datetime.now().hour
    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


import pandas as pd


def cashback_by_card(
    df: pd.DataFrame,
    period_start: pd.Timestamp | None = None,
    period_end: pd.Timestamp | None = None,
) -> pd.DataFrame:
    """
    Считает по каждой карте:
      - последние 4 цифры номера карты;
      - общую сумму расходов (руб.);
      - кэшбэк: 1 руб. на каждые 100 руб. расходов (floor).

    Параметры
    ----------
    df : DataFrame с уже нормализованными колонками:
         'дата_операции', 'номер_карты', 'статус', 'сумма_операции'
    period_start, period_end : границы периода (включительно).
         Если None — фильтр не применяется.

    Возвращает
    ----------
    DataFrame с колонками:
         ['карта', 'сумма_расходов', 'кэшбэк']
         отсортированный по убыванию расходов.
    """
    data = df.copy()

    # 0. Фильтр по периоду (включительно с обеих сторон)
    if period_start is not None:
        data = data[data["дата_операции"] >= period_start]
    if period_end is not None:
        data = data[data["дата_операции"] <= period_end]

    # 1. Оставляем только успешные операции
    data = data[data["статус"].eq("OK")]

    # 2. Только расходы (отрицательные суммы), берём модуль
    expenses = data[data["сумма_операции"] < 0].copy()
    expenses["расход"] = expenses["сумма_операции"].abs()

    # 3. Последние 4 цифры карты (в исходнике формат '*7197' или '')
    expenses["карта"] = (
        expenses["номер_карты"]
        .astype("string")
        .str.extract(r"(\d{4})$", expand=False)
    )

    # 4. Отбрасываем операции без карты (переводы, ЖКХ и т.п.)
    expenses = expenses.dropna(subset=["карта"])

    # 5. Агрегируем
    result = (
        expenses
        .groupby("карта", as_index=False)["расход"]
        .sum()
        .rename(columns={"расход": "сумма_расходов"})
    )

    # 6. Кэшбэк: 1 ₽ на каждые 100 ₽ расходов, округление вниз
    result["кэшбэк"] = (result["сумма_расходов"] // 100).astype(int)

    # 7. Округляем суммы до копеек и сортируем
    result["сумма_расходов"] = result["сумма_расходов"].round(2)
    result = result.sort_values("сумма_расходов", ascending=False).reset_index(drop=True)

    return result[["карта", "сумма_расходов", "кэшбэк"]]



if __name__ == "__main__":
    print(greeting())
    print(cashback_by_card(period_info))