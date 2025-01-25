from playwright.sync_api import Page
from .base_page import BasePage
from ..utils.constants import BASE_URL


class RegisterPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.path = 'accounts/register'
        self.page = page
        self.username_input = page.get_by_label('id_username')
        self.password_input = page.get_by_label('id_password1')
        self.password_confirm_input = page.get_by_label('id_password2')
        self.submit = page.get_by_role('button', name='Register')

        self.error_list = page.locator('ul.errorlist')
        self.error_password_short = page.get_by_text('This password is too short. It must contain at least 8 characters.')
        self.error_password_too_common = page.get_by_text('This password is too common.')
        self.error_password_numeric = page.get_by_text('This password is entirely numeric.')
        self.error_user_already_registered = page.get_by_text('A user with that username already exists.')

    def navigate(self):
        self.page.goto(BASE_URL + self.path)

    def register(self, username: str, password: str):
        self.username_input.type(username)
        self.password_input.type(password)
        self.password_confirm_input.type(password)
        self.submit.click()