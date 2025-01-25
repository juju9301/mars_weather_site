from playwright.sync_api import Page

class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.nav_login_button = page.locator('[href="/accounts/login/"]')
        self.nav_register_button = page.locator('[href="/accounts/register/"]')
        self.nav_logout_button = page.get_by_role('button', name="Logout")
        self.nav_greeting = page.get_by_test_id('nav-greeting')
        self.nav_plot_link = page.get_by_role('link', name="Generate Weather Plot")
        self.nav_weather_list = page.get_by_role('link', name="Weather List")
