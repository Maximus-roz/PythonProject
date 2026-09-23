import pytest

from src.masks import get_mask_account, get_mask_card_number


@pytest.mark.parametrize(
    "test_number, mask_card_number", [("1234567890123456", "1234 56** **** 3456")]
)
def test_get_mask_card_number_valid(test_number, mask_card_number):
    assert get_mask_card_number(test_number) == mask_card_number


@pytest.mark.parametrize(
    "test_number", ["", "1234", "123456789012345678", " ", "dsfsd"]
)
def test_get_mask_card_number_invalid(test_number):
    with pytest.raises(ValueError):
        get_mask_card_number(test_number)


@pytest.mark.parametrize(
    "test_number, account_number", [("12345678901234567890", "**7890")]
)
def test_get_mask_account_valid(test_number, account_number):
    assert get_mask_account(test_number) == account_number


@pytest.mark.parametrize("test_number", ["", "1234", " ", "dsfsd"])
def test_get_mask_account_invalid(test_number):
    with pytest.raises(ValueError):
        get_mask_account(test_number)
