from playwright.sync_api import Page, expect
from .utils.constants import BASE_URL

def test_error_message_if_password_not_provided(page: Page):
    page.goto(BASE_URL + '/accounts/login')
    page.get_by_label('Username').fill('ivan')
    page.get_by_role('button', name='Login', exact=True).click()
    # error_message = page.get_by_text('This field is required.')
    error_message = page.get_by_test_id('password-error')
    expect(error_message).to_be_visible()
    expect(error_message).to_have_text('This field is required.')

def test_error_message_if_username_not_provided(page: Page):
    page.goto(BASE_URL + '/accounts/login')
    page.get_by_label('Password').fill('randomstring')
    page.get_by_role('button', name='Login', exact=True).click()
    # error_message = page.get_by_text('This field is required.')
    password_error_message = page.get_by_test_id('password-error')
    expect(password_error_message).to_be_hidden()
    login_error_message = page.get_by_test_id('username-error')
    expect(login_error_message).to_have_text('This field is required.')
    expect(login_error_message).to_be_visible()