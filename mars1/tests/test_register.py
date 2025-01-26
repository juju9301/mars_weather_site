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

def test_successful_register(register_page: RegisterPage, page: Page):
    username = fake.user_name()
    password = fake.password(length=8)
    register_page.register(username, password)
    expect(page).to_have_url(register_page.base_url)
    expect(register_page.nav_greeting).to_be_visible()
    expect(register_page.nav_greeting).to_have_text(f'Hello, {username}')
    expect(register_page.nav_login_button).to_be_hidden()
    expect(register_page.nav_logout_button).to_be_visible()
    expect(register_page.nav_register_button).to_be_hidden()


def test_register_fail_if_password_too_short(register_page: RegisterPage, page: Page):
    username = fake.user_name()
    password = fake.password(length=7)
    register_page.register(username, password)
    expect(page).to_have_url(register_page.url)
    expect(register_page.register_form).to_be_visible()
    expect(register_page.error_password_short).to_be_visible()
    expect(register_page.error_list).to_have_count(1)

def test_regster_fail_if_password_numeric(register_page: RegisterPage, page: Page):
    username = fake.user_name()
    password = fake.password(length=8, lower_case=False, upper_case=False, special_chars=False)
    register_page.register(username, password)
    expect(page).to_have_url(register_page.url)
    expect(register_page.register_form).to_be_visible()
    expect(register_page.error_password_numeric).to_be_visible()
    expect(register_page.error_list).to_have_count(1)

def test_register_fail_if_password_too_common(register_page: RegisterPage, page: Page):
    username = fake.user_name()
    # password = fake.password(length=8, digits=False, special_chars=False)
    register_page.register(username, 'qwertY123456')
    expect(page).to_have_url(register_page.url)
    expect(register_page.register_form).to_be_visible()
    expect(register_page.error_password_too_common).to_be_visible()
    expect(register_page.error_list).to_have_count(1)

def test_register_fail_if_username_exists(register_page: RegisterPage):
    register_page.register(username=register_page.success_user_login, password=register_page.success_user_password)
    expect(register_page.register_form).to_be_visible()
    expect(register_page.error_user_already_registered).to_be_visible()

def test_register_fail_if_passwords_dont_match(register_page: RegisterPage):
    username = fake.user_name()
    password = fake.password(length=8)
    confirm_pass = fake.password(length=9)
    register_page.register(username, password, confirm_pass)
    expect(register_page.register_form).to_be_visible()
    expect(register_page.error_passwords_dont_match).to_be_visible()