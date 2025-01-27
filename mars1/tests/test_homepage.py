from playwright.sync_api import Page, BrowserType, expect
from .utils.constants import BASE_URL
from .pages.home_page import HomePage


def test_homepage_title(page: Page):
    page.goto(BASE_URL)
    expect(page).to_have_title('Mars Weather - Home')

# def test_headless_and_slow_mo(browser_type: BrowserType):
#     browser = browser_type.launch(headless=True, slow_mo=100)
    



def test_home_page_hero_header(page: Page):
    page.goto(BASE_URL)
    header = page.get_by_test_id('hero-header')
    expect(header).to_be_visible()
    expect(header).to_contain_text('Welcome to Mars Weather')

def test_logout_user_cant_create_posts_and_comments(page: Page):
    home_page = HomePage(page)
    home_page.navigate()
    expect(home_page.add_post_button).to_be_hidden()
    expect(home_page.add_comment_button).to_be_hidden()
    expect(home_page.login_to_add_post).to_be_visible()
    post_count = page.get_by_test_id('post').count()
    expect(home_page.login_to_add_comment).to_have_count(post_count)


