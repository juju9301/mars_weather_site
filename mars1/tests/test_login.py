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

def test_error_message_if_username_and_password_not_provided(page: Page):
    page.goto(BASE_URL + '/accounts/login')
    page.get_by_role('button', name='Login', exact=True).click()
    username_error_message = page.get_by_test_id('username-error')
    expect(username_error_message).to_have_text('This field is required.')
    expect(username_error_message).to_be_visible()
    password_error_message = page.get_by_test_id('password-error')
    expect(password_error_message).to_have_text('This field is required.')
    expect(password_error_message).to_be_visible()
    expect(page.get_by_text('This field is required.')).to_have_count(2)

def test_error_message_if_incorrect_password(page: Page):
    page.goto(BASE_URL + '/accounts/login')
    page.get_by_label('Username').fill('ivan')
    page.get_by_label('Password').fill('randomstring')
    page.get_by_role('button', name='Login', exact=True).click()
    error_message = page.locator('ul.errorlist')
    expect(page).to_have_url(BASE_URL + '/accounts/login/')
    expect(error_message).to_be_visible()
    expect(error_message).to_have_text('Please enter a correct username and password. Note that both fields may be case-sensitive.')