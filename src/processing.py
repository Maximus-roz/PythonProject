def filter_by_state(
    data_list: list[dict[str, any]], state: str = "EXECUTED"
) -> list[dict[str, any]]:
    """
    Фильтрует список словарей по значению ключа 'state'.
    """
    result = []
    for item in data_list:
        if item.get("state") == state:
            result.append(item)
    return result


def sort_by_date(
    data_list: list[dict[str, any]], descending=True
) -> list[dict[str, any]]:
    """
    Сортирует список словарей по ключу 'date'.
    """
    return sorted(data_list, key=lambda x: x.get("date", ""), reverse=descending)
