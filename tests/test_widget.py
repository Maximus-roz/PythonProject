import pytest

from src.widget import mask_account_card
from src.widget import get_date


@pytest.mark.parametrize(
    "test_value, expected",
    [("Visa Platinum 7000792289606361", "Visa Platinum 7000 79** **** 6361"),
     ("Счет 73654108430135874305", "Счет **4305"),
     ("Maestro 1596837868705199", "Maestro 1596 83** **** 5199"),
     ("Счет 35383033474447895560", "Счет **5560")])
def test_mask_account_card_valid(test_value, expected):
    assert mask_account_card(test_value) == expected

@pytest.mark.parametrize(
    "test_value",
    ["", "Visa Classic 1234", "123456789012345678", " ", "dsfsd"])
def test_mask_account_card_invalid(test_value):
    with pytest.raises(ValueError):
        mask_account_card(test_value)

@pytest.mark.parametrize(
    "test_value, expected",
    [("2024-03-11T02:26:18.671407", "11.03.2024"),
     ("2024-03-15", "15.03.2024"),
     ("2024-03-15T14:30:45+03:00", "15.03.2024"),
     ("2024-03-15T14:30:45+0300", "15.03.2024")])
def test_get_date_valid(test_value, expected):
    assert get_date(test_value) == expected

@pytest.mark.parametrize(
    "test_value",
    ["", "15/03/2024", "2024-03", " ", "dsfsd"])
def test_get_date_invalid(test_value):
    with pytest.raises(ValueError):
        get_date(test_value)