from playwright.sync_api import Page
from .base_page import BasePage


class WeatherPlotPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.path = 'plot'
        self.url = self.base_url + self.path

        self.sol_from_input = page.locator('input#id_sol_from')
        self.sol_to_input = page.locator('input#id_sol_to')
        self.metric_selector = page.locator('select#id_metric')
        self.generate_plot_button = page.get_by_role('button', name='Generate Plot')
        self.invalid_sol_range_error_message = page.get_by_text(
            'Sol to must be greater than Sol from.'
        )

    def navigate(self):
        self.page.goto(self.url)

    def fill_plot_from_and_submit(self, sol_from, sol_to, metric):
        self.sol_from_input.fill(str(sol_from))
        self.sol_to_input.fill(str(sol_to))
        self.metric_selector.select_option(metric)
        self.generate_plot_button.click()

    def get_plot_img(self):
        return self.page.get_by_alt_text('Weather Plot')

    def get_img_src(self):
        plot_img = self.get_plot_img()
        plot_img.get_attribute('src')

    def get_plot_url(self, sol_from, sol_to, metric):
        return f'{self.url}?sol_from={sol_from}&sol_to={sol_to}&metric={metric}'
    
    def get_no_data_error_message(self, sol_from, sol_to):
        return self.page.get_by_text(f'No weather data available for Sol range {sol_from} to {sol_to}.')