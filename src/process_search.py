import re

from pathlib import Path
from src.utils import load_transactions

def process_bank_search(operations:list[dict], search_data:str)->list[dict]:
    """Возвращает список словарей, у которых в описании есть строка поиска. """
    if not search_data:
        return operations

    # Экранируем строку поиска, чтобы спецсимволы не ломали регулярное выражение
    pattern = re.compile(re.escape(search_data), re.IGNORECASE)

    result = []

    for op in operations:

        description = op.get("description", "")

        # Проверка, что это строка (на случай некорректных данных)
        if isinstance(description, str) and pattern.search(description):
            result.append(op)

    return result

if __name__ == "__main__":
    file_path = Path(__file__).resolve().parent.parent

    operations_path = file_path / "data" / "operations.json"
    operations = load_transactions(str(operations_path))

    search_data = "перевод"
    filtered = process_bank_search(operations, search_data)
    print(f"Всего операций: {len(operations)}")
    print(f"Найдено по запросу '{search_data}': {len(filtered)}")
