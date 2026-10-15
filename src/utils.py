import json
import logging
from pathlib import Path
from typing import Any



from src.external_api import convert_to_rub

# Настройка логирования
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("masks")
logger.setLevel(logging.DEBUG)

# Чтобы не добавлять хендлеры повторно при повторном импорте
if not logger.handlers:
    file_handler = logging.FileHandler(LOG_DIR / "masks.log", encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def load_transactions(path: str) -> list[dict[str, Any]]:
    """
    Загружает список транзакций из JSON-файла.

    :param path: путь до JSON-файла
    :return: список словарей с данными о транзакциях.
             Пустой список, если файл пустой, содержит не список
             или не найден.
    """
    logger.info("Начало загрузки транзакций из файла: %s", path)

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        logger.error("Файл не найден: %s", path)
        return []
    except json.JSONDecodeError as e:
        logger.error("Ошибка декодирования JSON в файле %s: %s", path, e)
        return []
    except OSError as e:
        logger.error("Ошибка ввода-вывода при чтении файла %s: %s", path, e)
        return []

    if not isinstance(data, list):
        logger.warning(
            "Данные в файле %s не являются списком. Тип: %s",
            path,
            type(data).__name__,
        )
        return []

    logger.info("Успешно загружено %d транзакций из файла %s", len(data), path)
    return data


def get_transaction_amount(transaction: dict[str, Any]) -> float:
    """
    Возвращает сумму транзакции в рублях.

    Если валюта операции — RUB, возвращает сумму как есть.
    Если валюта — USD или EUR, конвертирует сумму в рубли
    через внешнее API.

    :param transaction: словарь с данными о транзакции
    :return: сумма транзакции в рублях (float)
    """
    logger.info("Начало обработки транзакции: %s", transaction)

    if not isinstance(transaction, dict):
        logger.error(
            "Транзакция должна быть словарём, получен тип: %s",
            type(transaction).__name__,
        )
        return 0.0

    operation_amount = transaction.get("operationAmount", {})
    amount = operation_amount.get("amount", 0)
    currency = operation_amount.get("currency", {}).get("code", "RUB")

    logger.debug("Извлечены данные: amount=%s, currency=%s", amount, currency)

    try:
        amount = float(amount)
    except (TypeError, ValueError) as e:
        logger.error("Некорректное значение суммы '%s' в транзакции: %s", amount, e)
        return 0.0

    if currency == "RUB":
        logger.info("Сумма в RUB: %.2f", amount)
        return amount

    if currency in ("USD", "EUR"):
        try:
            result = convert_to_rub(amount, currency)
            logger.info(
                "Успешная конвертация %.2f %s -> %.2f RUB",
                amount,
                currency,
                result,
            )
            return result
        except Exception as e:
            logger.error("Ошибка конвертации %.2f %s в RUB: %s", amount, currency, e)
            return 0.0

    logger.warning(
        "Неизвестная валюта '%s'. Возвращаем сумму без конвертации: %.2f",
        currency,
        amount,
    )
    return amount


if __name__ == "__main__":
    file_path = Path(__file__).resolve().parent.parent / "data" / "operations.json"

    logger.info("Запуск программы")
    transactions = load_transactions(str(file_path))

    for tx in transactions:
        amount = get_transaction_amount(tx)
        print(amount)

    print(f"Загружено транзакций: {len(transactions)}")
    logger.info("Программа завершена. Обработано транзакций: %d", len(transactions))
