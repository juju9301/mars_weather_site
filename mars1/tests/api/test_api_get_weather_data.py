from playwright.sync_api import Page, expect, APIResponse
import pytest
from ..utils.constants import BASE_URL
from ..utils.helpers import get_weather_from_fixture, get_weather_fixture_len

api_url = BASE_URL + 'api/get_weather_data'


def test_return_all_sols(page: Page):
    api_response: APIResponse = page.request.get(api_url)
    expect(api_response).to_be_ok()
    assert len(api_response.json()) == get_weather_fixture_len()

def test_get_weather_data_by_id(page: Page):
    weather = get_weather_from_fixture([2, 4, 6])
    data = {'ids': [int(record['pk']) for record in weather]}
    api_response = page.request.get(api_url, data=data)
    expect(api_response).to_be_ok()
    assert [record['id'] for record in api_response.json()] == data['ids']

def test_get_weather_data_by_sol(page: Page):
    weather = get_weather_from_fixture([2, 4, 6])
    data = {'sols': [int(record['fields']['sol']) for record in weather]}
    api_response = page.request.get(api_url, data=data)
    expect(api_response).to_be_ok()
    assert [record['sol'] for record in api_response.json()] == data['sols']

def test_get_weather_data_by_terrestrial_date(page: Page):
    weather = get_weather_from_fixture([2, 4, 6])
    data = {'terrestrial_dates': [record['fields']['terrestrial_date'] for record in weather]}
    api_response = page.request.get(api_url, data=data)
    expect(api_response).to_be_ok()
    assert [record['terrestrial_date'] for record in api_response.json()] == data['terrestrial_dates']

# Test cases for Weather object filtering

def test_response_is_empty_if_attrs_from_different_sols(page: Page):
    weather = get_weather_from_fixture([2, 4, 6])
    data = {
        'ids': [int(weather[0]['pk'])],
        'sols': [int(weather[1]['fields']['sol'])],
        'terrestrial_dates': [weather[2]['fields']['terrestrial_date']]
    }
    api_response = page.request.get(api_url, data=data)
    expect(api_response).to_be_ok()
    assert api_response.json() == []

def test_response_contains_only_record_with_all_three_params_matching(page: Page):
    weather = get_weather_from_fixture([3, 4, 8])
    data = {
        'ids': [int(weather[0]['pk']), int(weather[1]['pk'])],
        'sols': [int(weather[1]['fields']['sol']), int(weather[2]['fields']['sol'])],
        'terrestrial_dates': [weather[1]['fields']['terrestrial_date'], weather[0]['fields']['terrestrial_date']]
    }
    api_response = page.request.get(api_url, data=data)
    expect(api_response).to_be_ok()
    assert len(api_response.json()) == 1
    assert api_response.json()[0]['id'] == int(weather[1]['pk'])

# Test cases for error messages

@pytest.mark.parametrize('data,error_message', [
    ({'ids': 1}, "'ids' must be a list of integers"),
    ({'ids': 'random_string'}, "'ids' must be a list of integers"), 
    ({'ids': [1, 'hello', 5]}, "All values in 'ids' must be integers"),
    ({'ids': [1, None, 5]}, "All values in 'ids' must be integers"),
    ({'sols': 14}, "'sols' must be a list of integers"),
    ({'sols': 'randomstring'}, "'sols' must be a list of integers"),
    ({'sols': [45, '633', 90]}, "All values in 'sols' must be integers"),
    ({'terrestrial_dates': '2001-11-11'}, "'terrestrial_dates' must be a list of strings"),
    ({'terrestrial_dates': 25}, "'terrestrial_dates' must be a list of strings"),
    ({'terrestrial_dates': [45, '2022-11-11']}, "All values in 'terrestrial_dates' must be strings")
])  
def test_error_messages(page: Page, data, error_message):
    api_response = page.request.get(api_url, data=data)
    expect(api_response).not_to_be_ok()
    assert api_response.json()['error'] == error_message

