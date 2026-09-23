import pytest

from src.processing import filter_by_state

from src.processing import sort_by_date

@pytest.mark.parametrize(
    "test_value, expected",
    [(
     [{'id': 414288290, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
      {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'},
      {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
      {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'}],
[{'id': 414288290, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
{'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'}])])
def test_filter_by_state_valid(test_value, expected):
    assert filter_by_state(test_value) == expected

@pytest.mark.parametrize(
    "test_value, expected",
    [(
            [{'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
             {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'}], [])
    ])
def test_filter_by_state_canceled(test_value, expected):
    assert filter_by_state(test_value) == expected

def test_filter_by_state_empty():
    assert filter_by_state([]) == []

@pytest.fixture
def sample_data():
    return [{'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
            {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'},
            {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
            {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'}]

def test_sort_by_date_descending(sample_data):
    """Проверка сортировки по убыванию (по умолчанию)."""
    result = sort_by_date(sample_data)
    dates = [item['date'] for item in result]
    assert dates == [
        '2019-07-03T18:35:29.512364',
        '2018-10-14T08:21:33.419441',
        '2018-09-12T21:27:25.241689',
        '2018-06-30T02:08:58.425572',
    ]

def test_sort_by_date_ascending(sample_data):
    """Проверка сортировки по возрастанию."""
    result = sort_by_date(sample_data, descending=False)
    dates = [item['date'] for item in result]
    assert dates == [
        '2018-06-30T02:08:58.425572',
        '2018-09-12T21:27:25.241689',
        '2018-10-14T08:21:33.419441',
        '2019-07-03T18:35:29.512364',
    ]

def test_sort_by_date_empty_list():
    """Проверка сортировки пустого списка."""
    assert sort_by_date([]) == []
