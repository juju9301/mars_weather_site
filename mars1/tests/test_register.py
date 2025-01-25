from playwright.sync_api import Page, expect
import pytest
from faker import Faker

from .pages.register_page import RegisterPage

fake = Faker()

@pytest.fixture
def register_page(page: Page):
    register_page = RegisterPage(page)
    register_page.navigate()
    return register_page

def test_successful_register(register_page: RegisterPage):
    pass


def test_register_fail_if_password_too_short(register_page: RegisterPage):
    pass

def test_regster_fail_if_password_numeric(register_page: RegisterPage):
    pass

def test_register_fail_if_password_too_common(register_page: RegisterPage):
    pass

def test_register_fail_if_username_exists(register_page: RegisterPage):
    register_page.register(username=register_page.success_user_login, password=register_page.success_user_password)
    expect(register_page.error_user_already_registered).to_be_visible()