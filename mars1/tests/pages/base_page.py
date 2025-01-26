from playwright.sync_api import Page
from dotenv import load_dotenv
import os
from ..utils.constants import BASE_URL

load_dotenv()


class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.base_url = BASE_URL
        self.nav_login_button = page.locator('[href="/accounts/login/"]')
        self.nav_register_button = page.locator('[href="/accounts/register/"]')
        self.nav_logout_button = page.get_by_role('button', name="Logout")
        self.nav_greeting = page.get_by_test_id('nav-greeting')
        self.nav_plot_link = page.get_by_role('link', name="Generate Weather Plot")
        self.nav_weather_list = page.get_by_role('link', name="Weather List")

        self.success_user_login = os.getenv('SUCCESS_TEST_USER_LOGIN') 
        self.success_user_password = os.getenv('SUCCESS_TEST_USER_PASS')
