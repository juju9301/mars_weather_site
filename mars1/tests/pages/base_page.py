from playwright.sync_api import Page
from dotenv import load_dotenv
import os
from ..utils.constants import BASE_URL, TEST_FILES
import requests

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

        self.test_user_username = os.getenv('TEST_USER_USERNAME') 
        self.test_user_password = os.getenv('TEST_USER_PASSWORD')

        self.api_posts = self.base_url + 'api/posts'
        self.api_posts_delete = self.base_url + 'api/posts/delete'
        self.api_comments = self.base_url + 'api/comments'
        self.api_comments_delete = self.base_url + 'api/comments/delete'
        self.api_users = self.base_url + 'api/users'
