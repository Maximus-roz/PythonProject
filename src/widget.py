from masks import get_mask_card_number
from masks import get_mask_account

def mask_account_card(account_number):
    account_number_spl = account_number.split()
    account_number_int = ""
    account_number_str = ""
    for number in account_number_spl:
        if number.isdigit():
            account_number_int = number
        elif number.isalpha():
            account_number_str = number

    if len(account_number_int) == 20:
        result = get_mask_account(account_number_int)
        print(f"{account_number_str} {result}")
        return f"{account_number_str} {result}"


    elif len(account_number_int) == 16:
        result = get_mask_card_number(account_number_int)
        return f"{account_number_str} {result}"

1234567812345678
123456



    


