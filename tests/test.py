import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

def test_homepage(browser):
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://localhost:8000")
    assert page.title() == "Expected Title"
    context.close()