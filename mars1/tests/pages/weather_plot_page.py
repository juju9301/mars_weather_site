from playwright.sync_api import Page
from .base_page import BasePage


class WeatherPlotPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.path = 'plot'
        self.url = self.base_url + self.path

        self.sol_from_selector = page.locator('select#sol_from')
        self.sol_to_selector = page.locator('select#sol_to')
        self.temp_type_selector = page.locator('select#temp_type')
        self.generate_plot_button = page.get_by_role('button', name='Generate Plot')

    def navigate(self):
        self.page.goto(self.url)

    def get_plot_img(self):
        return self.page.get_by_alt_text('Weather Plot')

    def get_img_src(self):
        plot_img = self.get_plot_img()
        plot_img.get_attribute('src')

    def get_plot_url(self, sol_from, sol_to, temp_type):
        return f'{self.url}?sol_from={sol_from}&sol_to={sol_to}&temp_type={temp_type}'