from playwright.sync_api import Page, expect, Response, APIResponse, APIRequestContext
from .utils.constants import BASE_URL

api_url = BASE_URL + 'api/get_weather_data'

def test_return_all_sols(page: Page):
    # response: Response = page.goto(api_url)
    api_ctx: APIRequestContext = page.request
    api_response: APIResponse = api_ctx.get(api_url)
    expect(api_response).to_be_ok()
    assert len(api_response.json()) > 10
