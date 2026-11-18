from playwright.sync_api import Page
from .base_page import BasePage


class HomePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = self.base_url

        self.hero_header = page.get_by_test_id('hero-header')
        self.rover_selector = page.get_by_test_id('rover-selector')
        self.rover_photo = page.get_by_test_id('rover-photo')
        self.rover_photo_info = page.get_by_test_id('rover-photo-info')
        self.rover_image_status = page.get_by_test_id('rover-image-status')

        self.recent_sol_title = page.get_by_test_id('recent-sol-title')

    def navigate(self):
        self.page.goto(self.base_url)

    def get_nth(self, locator, n):
        return locator.nth(n)

