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
        self.invalid_sol_range_error_message = page.get_by_text('Sol range is invalid. Please make sure sol_to is greater than sol_from')

    def navigate(self):
        self.page.goto(self.url)

    def fill_plot_from_and_submit(self, sol_from, sol_to, temp_type):
        self.sol_from_selector.select_option(sol_from)
        self.sol_to_selector.select_option(sol_to)
        self.temp_type_selector.select_option(temp_type)
        self.generate_plot_button.click()

    def get_plot_img(self):
        return self.page.get_by_alt_text('Weather Plot')

    def get_img_src(self):
        plot_img = self.get_plot_img()
        plot_img.get_attribute('src')

    def get_plot_url(self, sol_from, sol_to, temp_type):
        return f'{self.url}?sol_from={sol_from}&sol_to={sol_to}&temp_type={temp_type}'
    
    def get_no_data_error_message(self, sol_from, sol_to):
        return self.page.get_by_text(f'No weather data available for Sol range {sol_from} to {sol_to}.')