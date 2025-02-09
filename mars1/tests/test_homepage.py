from playwright.sync_api import Page, BrowserType, expect
from .pages.home_page import HomePage
from .pages.login_page import LoginPage
import pytest

@pytest.fixture
def home_page(page: Page):
    home_page = HomePage(page)
    home_page.navigate()

    yield home_page




def test_homepage_title(home_page: HomePage, page: Page):
    expect(page).to_have_title('Mars Weather - Home')

# def test_headless_and_slow_mo(browser_type: BrowserType):
#     browser = browser_type.launch(headless=True, slow_mo=100)

def test_home_page_hero_header(home_page: HomePage):
    expect(home_page.hero_header).to_be_visible()
    expect(home_page.hero_header).to_contain_text('Welcome to Mars Weather')

def test_logout_user_cant_create_posts_and_comments(home_page: HomePage, page: Page):
    expect(home_page.add_post_button).to_be_hidden()
    expect(home_page.add_comment_button).to_be_hidden()
    expect(home_page.login_to_add_post).to_be_visible()
    post_count = page.get_by_test_id('post').count()
    expect(home_page.login_to_add_comment).to_have_count(post_count)

def test_nasa_pic_section_is_displayed(home_page: HomePage):
    expect(home_page.apod_content).to_be_visible()
    expect(home_page.apod_media).to_be_visible()
    expect(home_page.apod_text_title).to_be_visible()
    expect(home_page.apod_text).to_be_visible()

def test_apod_section_hidden_if_nasa_pic_request_resulted_in_404(page: Page):
    home_page = HomePage(page)
    page.route('https://api.nasa.gov/planetary/*', lambda route: route.fulfill(
        status=404,
        content_type='text/plain',
        body='Not Found'
    ))
    home_page.navigate()
    expect(home_page.apod_section).not_to_be_visible()
    expect(home_page.apod_title).not_to_be_visible()
    expect(home_page.apod_content).not_to_be_visible()
    expect(home_page.recent_sol_title).to_be_visible()