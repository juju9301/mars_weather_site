import pytest
from playwright.sync_api import sync_playwright
from playwright.sync_api import Page

# def test_homepage(context_page):
#     context, page = context_page
#     page.goto("http://localhost:8000")
#     assert page.title() == "Expected Title"

def test_one(page: Page):
    page.goto('https://playwright.dev/python')
    

def test_two():
    with sync_playwright() as p:
        for browser_type in [p.chromium, p.firefox, p.webkit]:
            browser = browser_type.launch(headless=False)
            page = browser.new_page()
            page.goto('https://playwright.dev/python')
            # page.screenshot(path=f'example-{browser_type.name}.png')
            browser.close()