from playwright.sync_api import Page, expect
from .utils.constants import BASE_URL
from dotenv import load_dotenv
import os
import pytest

from .pages.login_page import LoginPage


load_dotenv()

success_user_login, success_user_password = os.getenv('SUCCESS_TEST_USER_LOGIN'), os.getenv('SUCCESS_TEST_USER_PASS')

@pytest.fixture
def login_page(page: Page):
    login_page = LoginPage(page)
    login_page.navigate()
    return login_page

def test_error_message_if_password_not_provided(login_page: LoginPage):
    login_page.login('ivan', '')
    expect(login_page.empty_password_error).to_be_visible()
    expect(login_page.empty_password_error).to_have_text('This field is required.')

def test_error_message_if_username_not_provided(login_page: LoginPage):
    login_page.password_input.fill('randomstring')
    login_page.login_button.click()
    # error_message = page.get_by_text('This field is required.')
    expect(login_page.empty_password_error).to_be_hidden()
    expect(login_page.empty_username_error).to_have_text('This field is required.')
    expect(login_page.empty_username_error).to_be_visible()

def test_error_message_if_username_and_password_not_provided(page: Page):
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login_button.click()
    expect(login_page.empty_username_error).to_have_text('This field is required.')
    expect(login_page.empty_username_error).to_be_visible()
    expect(login_page.empty_password_error).to_have_text('This field is required.')
    expect(login_page.empty_password_error).to_be_visible()
    expect(page.get_by_text('This field is required.')).to_have_count(2)

def test_error_message_if_incorrect_password(page: Page, login_page: LoginPage):
    login_page.login(username=success_user_login, password='randomString123')
    expect(page).to_have_url(BASE_URL + 'accounts/login/')
    expect(login_page.incorrect_credentials_error).to_be_visible()
    expect(login_page.incorrect_credentials_error).to_have_text('Please enter a correct username and password. Note that both fields may be case-sensitive.')

def test_successful_login(page: Page, login_page: LoginPage):
    login_page.login(username=success_user_login, password=success_user_password)
    expect(page).to_have_url(BASE_URL)
    expect(login_page.nav_greeting).to_be_visible()
    expect(login_page.nav_greeting).to_have_text(f'Hello, {success_user_login}')
    expect(login_page.nav_logout_button).to_be_visible()
    expect(login_page.nav_login_button).not_to_be_visible()

