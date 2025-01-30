from playwright.sync_api import Page
from dotenv import load_dotenv
import os
from ..utils.constants import BASE_URL, TEST_FILES

load_dotenv()


class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.base_url = BASE_URL
        self.test_file_jpg = TEST_FILES['jpg']
        self.test_file_png = TEST_FILES['png']
        # navbar locators
        self.nav_login_button = page.get_by_test_id('nav-login')
        self.nav_register_button = page.locator('[href="/register/"]')
        self.nav_logout_button = page.get_by_role('button', name="Logout")
        self.nav_greeting = page.get_by_test_id('nav-greeting')
        self.nav_plot_link = page.get_by_role('link', name="Generate Weather Plot")
        self.nav_weather_list = page.get_by_role('link', name="Weather List")

        self.success_user_login = os.getenv('SUCCESS_TEST_USER_LOGIN') 
        self.success_user_password = os.getenv('SUCCESS_TEST_USER_PASS')
