from pathlib import Path

import pandas as pd


def read_operations(file_path: str = "operations.xlsx", sheet_name: str = "Отчет по операциям") -> pd.DataFrame:
    """
    Считывает данные операций из Excel-файла.

    Параметры:
        file_path (str): путь к файлу Excel.
        sheet_name (str): имя листа с данными.

    Возвращает:
        pd.DataFrame: датафрейм с операциями.
    """
    df = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        dtype={
            "Номер карты": str,
            "Статус": str,
            "Валюта операции": str,
            "Валюта платежа": str,
            "Категория": str,
            "MCC": "Int64",
            "Описание": str,
        },
        parse_dates=["Дата операции", "Дата платежа"],
    )
    return df

def read_operations_clean(file_path: str = "operations.xlsx") -> pd.DataFrame:
    df = read_operations(file_path)

    # Нормализуем имена столбцов (snake_case)
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r"[^\w]+", "_", regex=True)
    )

    # --- ДАТА: в исходнике ДД.ММ.ГГГГ, читаем однозначно ---
    date_col_candidates = ["дата_операции", "дата_платежа", "date"]
    for col in date_col_candidates:
        if col in df.columns:
            df[col] = pd.to_datetime(
                df[col],
                format="%d.%m.%Y",   # день.месяц.год — как в файле
                errors="coerce",
            )
            break
    else:
        # на случай, если колонка называется иначе — попробуем найти по слову 'дат'
        date_cols = [c for c in df.columns if "дат" in c]
        if not date_cols:
            raise ValueError("Не найдена колонка с датой в DataFrame")
        df[date_cols[0]] = pd.to_datetime(
            df[date_cols[0]], format="%d.%m.%Y", errors="coerce"
        )

    # Приводим числовые поля
    numeric_cols = [
        "сумма_операции", "сумма_платежа", "кэшбэк",
        "бонусы_включая_кэшбэк", "округление_на_инвесткопилку",
        "сумма_операции_с_округлением",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Категория/описание/статус — убираем пробелы
    for col in ["статус", "категория", "описание"]:
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip()

    return df




if __name__ == "__main__":

    base_path = Path(__file__).resolve().parent.parent
    operation_path = base_path / "data" / "operations.xlsx"
    print(read_operations_clean(operation_path))