from playwright.sync_api import Page, Response, Request, expect
from .utils.constants import BASE_URL, API_GET_USERS_URL
from playwright.sync_api import Playwright
# def test_request_response(page: Page):
#     response: Response = page.goto(BASE_URL)
#     print(response.status)
#     print(response.all_headers())
#     print(response.headers_array())
#     # print(response.body())
#     print(response.text())
#     # print(response.json())
#     request: Request = response.request

# def test_monitoring_traffic(page: Page):
#     page.on('request', lambda request: print(f'>>{request.method} {request.url}'))
#     page.on('response', lambda response: print(f'<<{response.status} {response.url}'))
#     page.goto(BASE_URL)

def test_user_get_api(playwright: Playwright):
    api_call = playwright.request.new_context()
    api_response = api_call.get(API_GET_USERS_URL)
    expect(api_response).to_be_ok()
    json = api_response.json()
    assert json[0]['id'] == 1
    
