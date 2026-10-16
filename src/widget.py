import datetime

from src.masks import get_mask_account, get_mask_card_number


def mask_account_card(account_number=""):
    """
    Маскирует номер банковской карты или счёта.

    Функция принимает строку, содержащую название карты/счёта и его номер,
    разделённые пробелами, и возвращает строку с замаскированным номером.
    Номер карты (16 цифр) маскируется как 'XXXX XX** **** XXXX',
    номер счёта (20 цифр) — как '**XXXX'.

    :param account_number: Строка с названием и номером карты/счёта.
                           По умолчанию пустая строка.
    :type account_number: str

    :return: Строка с исходным названием и замаскированным номером.
    :rtype: str

    :raises ValueError: Если аргумент не передан (пустая строка),
                        если номер карты/счёта не найден среди подстрок,
                        если длина номера не равна 16 или 20 цифрам.

    :example:
        >>> mask_account_card("Visa Platinum 7000792289606361")
        'Visa Platinum 7000 79** **** 6361'
        >>> mask_account_card("Счет 73654108430135874305")
        'Счет **4305'
    """
    if account_number is None:
        return "—"
        # отсекаем NaN и приводим к строке
    if isinstance(account_number, float) and account_number != account_number:
        return "—"
    account_number = str(account_number).strip()
    if not account_number:
        return "—"
    # if not account_number:  # Проверка на пустую строку
    #     raise ValueError("Аргумент не передан")
    #     return "Аргумент не передан"



    account_number_spl = account_number.split()
    account_number_int = None
    account_number_str = []
    substring_counter = 0
    for number in account_number_spl:  # разделение на строковые и цифровые значения
        if number.isdigit():
            account_number_int = number
            substring_counter += 1
        else:
            account_number_str.append(number)
            substring_counter += 1

    if substring_counter > 3:  # защита от большего чем 2 количества подстрок
        return account_number

    if account_number_int is None:
        raise ValueError("Номер карты или счёта не найден")

    account_number_str_join = " ".join(account_number_str)

    if len(account_number_int) == 20:
        result = get_mask_account(account_number_int)
        return f"{account_number_str_join} {result}"

    elif len(account_number_int) == 16:
        result = get_mask_card_number(account_number_int)
        return f"{account_number_str_join} {result}"

    else:
        raise ValueError("Некорректная длина номера")
        return account_number


def get_date(iso_string):
    """
    Преобразует дату из ISO-формата в формат ДД.ММ.ГГГГ.

    :param iso_string: Строка с датой в формате ISO 8601
                       (например, '2024-03-15T10:30:00' или '2024-03-15').
    :type iso_string: str

    :return: Строка с датой в формате 'ДД.ММ.ГГГГ'.
    :rtype: str

    :raises ValueError: Если переданная строка не соответствует ISO-формату.

    :example:
        >>> get_date("2024-03-15T10:30:00")
        '15.03.2024'
        >>> get_date("2024-03-15")
        '15.03.2024'
    """
    date_new = datetime.fromisoformat(iso_string)
    return date_new.strftime("%d.%m.%Y")