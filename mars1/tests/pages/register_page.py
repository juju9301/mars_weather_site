from playwright.sync_api import Page
from .base_page import BasePage


class RegisterPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.path = 'accounts/register/'
        self.url = self.base_url + self.path
        self.page = page
        self.username_input = page.locator('#id_username')
        self.password_input = page.locator('#id_password1')
        self.password_confirm_input = page.locator('#id_password2')
        self.submit = page.get_by_role('button', name='Register')
        self.register_form = page.get_by_test_id('register-form')

        self.error_list = page.locator('ul.errorlist')
        self.error_password_short = page.get_by_text('This password is too short. It must contain at least 8 characters.')
        self.error_password_too_common = page.get_by_text('This password is too common.')
        self.error_password_numeric = page.get_by_text('This password is entirely numeric.')
        self.error_user_already_registered = page.get_by_text('A user with that username already exists.')
        self.error_passwords_dont_match = page.get_by_text(r'The two password fields didn’t match.')

    def navigate(self):
        self.page.goto(self.url)

    def register(self, username: str, password: str, confirm_password: str = None):
        self.username_input.type(username)
        self.password_input.type(password)
        self.password_confirm_input.type(confirm_password if confirm_password is not None else password)
        self.submit.click()