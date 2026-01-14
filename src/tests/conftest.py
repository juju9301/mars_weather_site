import pytest
from playwright.sync_api import Page, expect
from .pages.login_page import LoginPage


def pytest_configure(config):
    config.option.htmlpath = 'report.html'
    config.option.self_contained_html = True

