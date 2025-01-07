from playwright.sync_api import Page, expect

def test_homepage_title(page: Page):
    page.goto('http://localhost:8000/')
    expect(page).to_have_title('Mars Weather - Home')


def test_home_page_hero_header(page: Page):
    page.goto('http://127.0.0.1:8000/')
    header = page.get_by_test_id('hero-header')
    expect(header).to_be_visible()
    # assert header.text_content() == 'Welcome to Mars Weather'
    expect(header).to_contain_text('Welcome to Mars Weather')
