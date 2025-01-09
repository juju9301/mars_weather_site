from playwright.sync_api import Page, BrowserType, expect
from .utils.constants import BASE_URL


def test_homepage_title(page: Page):
    page.goto(BASE_URL)
    expect(page).to_have_title('Mars Weather - Home')

# def test_headless_and_slow_mo(browser_type: BrowserType):
#     browser = browser_type.launch(headless=False, slow_mo=100)
    



def test_home_page_hero_header(page: Page):
    page.goto(BASE_URL)
    header = page.get_by_test_id('hero-header')
    expect(header).to_be_visible()
    expect(header).to_contain_text('Welcome to Mars Weather')
