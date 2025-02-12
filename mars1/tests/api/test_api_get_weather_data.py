from playwright.sync_api import Page, expect, Response, APIResponse, APIRequestContext
import pytest
from ..utils.constants import BASE_URL

api_url = BASE_URL + 'api/get_weather_data'

test_data = [
    {"terrestrial_date": "2025-01-06", "sol": 4415},
    {"terrestrial_date": "2025-01-04", "sol": 4413}
]

def test_return_all_sols(page: Page):
    # response: Response = page.goto(api_url)
    api_ctx: APIRequestContext = page.request
    api_response: APIResponse = api_ctx.get(api_url)
    expect(api_response).to_be_ok()
    assert len(api_response.json()) > 10

@pytest.mark.parametrize('key', [
    ('terrestrial_date'),
    ('sol')
])
def test_get_weather_data_by_single_param(page: Page, key):
    data = [item[key] for item in test_data]
    api_response = page.request.get(api_url, data={f'{key}s': data})
    expect(api_response).to_be_ok()
    assert len(api_response.json()) == len(data)
    assert [record[key] for record in api_response.json()] == data

@pytest.mark.parametrize('data,error_message', [
    ({'ids': 1}, "'ids' must be a list of integers"),
    ({'ids': 'random_string'}, "'ids' must be a list of integers"), 
    ({'ids': [1, 'hello', 5]}, "All values in 'ids' must be integers"),
    ({'ids': [1, None, 5]}, "All values in 'ids' must be integers"),
    ({'sols': 14}, "'sols' must be a list of integers"),
    ({'sols': 56}, "'sols' must be a list of integers"),
    ({'sols': [45, '633', 90]}, "All values in 'sols' must be integers"),
    ({'terrestrial_dates': '2001-11-11'}, "'terrestrial_dates' must be a list of strings"),
    ({'terrestrial_dates': 25}, "'terrestrial_dates' must be a list of strings"),
    ({'terrestrial_dates': [45, '2022-11-11']}, "All values in 'terrestrial_dates' must be strings")
])  
def test_error_messages(page: Page, data, error_message):
    api_response = page.request.get(api_url, data=data)
    expect(api_response).not_to_be_ok()
    assert api_response.json()['error'] == error_message

