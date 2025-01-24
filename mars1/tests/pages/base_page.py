from playwright.sync_api import Page

class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.nav_loing_button = None
        self.nav_logout_button = None
        self.nav_greeting = None