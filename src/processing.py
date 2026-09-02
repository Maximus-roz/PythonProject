
def filter_by_state(data_list, state='EXECUTED'):
    """
       Фильтрует список словарей по значению ключа 'state'.
    """
    result = []
    for item in data_list:
        if item.get('state') == state:
            result.append(item)
    return result


