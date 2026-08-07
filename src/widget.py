from masks import get_mask_card_number, get_mask_account


def mask_account_card(account_number=""):
    if not account_number:  # Проверка на пустую строку
        return "Аргумент не передан"
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

    account_number_str_join = " ".join(account_number_str)

    if len(account_number_int) == 20:
        result = get_mask_account(account_number_int)
        return f"{account_number_str_join} {result}"

    elif len(account_number_int) == 16:
        result = get_mask_card_number(account_number_int)
        return f"{account_number_str_join} {result}"

    else:
        return account_number


from datetime import datetime


def get_date(iso_string):  # преобразуем ISO-формат в формат ДД.ММ.ГГГГ
    date_new = datetime.fromisoformat(iso_string)
    return date_new.strftime("%d.%m.%Y")
