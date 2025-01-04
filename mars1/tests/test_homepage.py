import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

@pytest.fixture(scope="function")
def context_page(browser):
    context = browser.new_context()
    page = context.new_page()
    yield context, page
    context.close()

def test_homepage(context_page):
    context, page = context_page
    page.goto("http://localhost:8000")
    assert page.title() == "Expected Title"