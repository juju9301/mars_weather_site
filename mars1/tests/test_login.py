from playwright.sync_api import Page, expect
from .utils.constants import BASE_URL
from dotenv import load_dotenv
import os

from .pages.login_page import LoginPage


load_dotenv()

success_user_login, success_user_password = os.getenv('SUCCESS_TEST_USER_LOGIN'), os.getenv('SUCCESS_TEST_USER_PASS')

def test_error_message_if_password_not_provided(page: Page):
    login_page = LoginPage(page)
    page.goto(BASE_URL + 'accounts/login')
    login_page.login('ivan', '')
    expect(login_page.empty_password_error).to_be_visible()
    expect(login_page.empty_password_error).to_have_text('This field is required.')

def test_error_message_if_username_not_provided(page: Page):
    page.goto(BASE_URL + 'accounts/login')
    page.get_by_label('Password').fill('randomstring')
    page.get_by_role('button', name='Login', exact=True).click()
    # error_message = page.get_by_text('This field is required.')
    password_error_message = page.get_by_test_id('password-error')
    expect(password_error_message).to_be_hidden()
    login_error_message = page.get_by_test_id('username-error')
    expect(login_error_message).to_have_text('This field is required.')
    expect(login_error_message).to_be_visible()

def test_error_message_if_username_and_password_not_provided(page: Page):
    page.goto(BASE_URL + 'accounts/login')
    page.get_by_role('button', name='Login', exact=True).click()
    username_error_message = page.get_by_test_id('username-error')
    expect(username_error_message).to_have_text('This field is required.')
    expect(username_error_message).to_be_visible()
    password_error_message = page.get_by_test_id('password-error')
    expect(password_error_message).to_have_text('This field is required.')
    expect(password_error_message).to_be_visible()
    expect(page.get_by_text('This field is required.')).to_have_count(2)

def test_error_message_if_incorrect_password(page: Page):
    page.goto(BASE_URL + 'accounts/login')
    page.get_by_label('Username').fill('ivan')
    page.get_by_label('Password').fill('randomstring')
    page.get_by_role('button', name='Login', exact=True).click()
    error_message = page.locator('ul.errorlist')
    expect(page).to_have_url(BASE_URL + 'accounts/login/')
    expect(error_message).to_be_visible()
    expect(error_message).to_have_text('Please enter a correct username and password. Note that both fields may be case-sensitive.')

def test_successful_login(page: Page):
    page.goto(BASE_URL + 'accounts/login')
    page.get_by_label('Username').fill(success_user_login)
    page.get_by_label('Password').fill(success_user_password)
    page.get_by_role('button', name='Login').click()
    expect(page).to_have_url(BASE_URL)
    hello_string = page.get_by_text(f'Hello, {success_user_login}')
    expect(hello_string).to_be_visible()
    nav_login_button = page.get_by_text('Login')
    expect(nav_login_button).not_to_be_visible()

