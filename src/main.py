import json
from pathlib import Path

from src.load_transactions_from_csv import load_transactions_csv
from src.load_transactions_from_excel import load_transactions_excel
from src.process_search import process_bank_search
from src.processing import sort_by_date, filter_by_state
from src.utils import load_transactions
from src.generators import filter_by_currency


def main():
    base_path = Path(__file__).resolve().parent.parent
    operations_path = base_path / "data" / "operations.json"
    path_csv = base_path / "data" / "transactions.csv"
    path_excel = base_path / "data" / "transactions_excel.xlsx"

    print("Привет! Добро пожаловать в программу работы с банковскими транзакциями.")

    while True:
        print("Выберите необходимый пункт меню:")
        print("1. Получить информацию о транзакциях из JSON-файла")
        print("2. Получить информацию о транзакциях из CSV-файла")
        print("3. Получить информацию о транзакциях из XLSX-файла")
        choice = input("Ваш выбор (1-3): ").strip()

        load_op = None

        if choice == "1":
            if not operations_path.exists():
                print(f"Файл не найден: {operations_path}")
                continue
            load_op = load_transactions(str(operations_path))

        elif choice == "2":
            if not path_csv.exists():
                print(f"Файл не найден: {path_csv}")
                continue
            load_op = load_transactions_csv(str(path_csv))

        elif choice == "3":
            if not path_excel.exists():
                print(f"Файл не найден: {path_excel}")
                continue
            load_op = load_transactions_excel(str(path_excel))

        else:
            print("Неверный выбор. Пожалуйста, введите 1, 2 или 3.")
            continue

        # ------------------------------------------------------------------
        # Фильтрация по статусу
        # ------------------------------------------------------------------
        print("Введите статус, по которому необходимо выполнить фильтрацию.")
        status = (
            input(
                "Доступные для фильтровки статусы:\nEXECUTED\nCANCELED\nPENDING\nВведите статус: "
            )
            .strip()
            .upper()
        )

        if status not in {"EXECUTED", "CANCELED", "PENDING"}:
            print("Недопустимый статус. Фильтрация не выполнена.")
            continue

        result = filter_by_state(load_op, status)
        print(f"Найдено транзакций со статусом '{status}': {len(result)}")

        # ------------------------------------------------------------------
        # Сортировка по дате
        # ------------------------------------------------------------------
        date_request = input("Отсортировать операции по дате? Да/Нет: ").strip().lower()
        if date_request == "да":
            direction = (
                input(
                    "Отсортировать по возрастанию или по убыванию? по возрастанию/по убыванию: "
                )
                .strip()
                .lower()
            )

            if direction == "по возрастанию":
                result = sort_by_date(result, descending=False)
            elif direction == "по убыванию":
                result = sort_by_date(result, descending=True)
            else:
                print("Недопустимый вариант сортировки. Сортировка не выполнена.")

        # ------------------------------------------------------------------
        # Фильтр по валюте (через генератор filter_by_currency)
        # ------------------------------------------------------------------
        currency_request = (
            input("Выводить только рублевые транзакции? Да/Нет: ").strip().lower()
        )
        if currency_request == "да":
            result = list(filter_by_currency(result, "RUB"))

        # ------------------------------------------------------------------
        # Поиск по слову в описании
        # ------------------------------------------------------------------
        search_request = (
            input(
                "Отфильтровать список транзакций по определенному слову в описании? Да/Нет: "
            )
            .strip()
            .lower()
        )
        if search_request == "да":
            search_word = input("Введите слово для поиска: ").strip()
            result = process_bank_search(result, search_word)

        # ------------------------------------------------------------------
        # Финальный вывод
        # ------------------------------------------------------------------
        print("Распечатываю итоговый список транзакций...")

        if not result:
            print(
                "Программа: Не найдено ни одной транзакции, "
                "подходящей под ваши условия фильтрации"
            )
        else:
            print(f"Всего банковских операций в выборке: {len(result)}")
            for op in result:
                print(json.dumps(op, ensure_ascii=False, indent=2))

        break


if __name__ == "__main__":
    main()
