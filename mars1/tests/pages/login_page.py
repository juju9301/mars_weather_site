from playwright.sync_api import Page
from ..utils.constants import BASE_URL

class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.username_input = page.get_by_label('Username')
        self.password_input = page.get_by_label('Password')
        self.login_button = page.get_by_role('button', name='Login', exact=True)
        self.empty_password_error = page.get_by_test_id('password-error')
        self.empty_login_error = page.get_by_test_id('username-error')

    # def navigate(self, base_url: str):
    #     self.page.goto(BASE_URL + 'accounts/login')

    def login(self, username: str, password: str):
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()
