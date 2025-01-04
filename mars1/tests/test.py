import pytest
from playwright.sync_api import sync_playwright

def test_homepage(context_page):
    context, page = context_page
    page.goto("http://localhost:8000")
    assert page.title() == "Expected Title"