from ..pages.weather_plot_page import WeatherPlotPage
from playwright.sync_api import Page, expect, sync_playwright
import pytest
import easyocr
from pathlib import Path

@pytest.fixture
def setup(page: Page):
    plot_page = WeatherPlotPage(page)
    plot_page.navigate()
    expect(page).to_have_url(plot_page.url)

    yield plot_page

def test_generate_plot(page: Page, setup):
    plot_page = setup
    sol_from, sol_to, temp_type = '10', '1000', 'min_temp'
    plot_page.sol_from_selector.select_option('10')
    plot_page.sol_to_selector.select_option('1000')
    plot_page.temp_type_selector.select_option('Min Temp')
    plot_page.generate_plot_button.click()
    plot_url = plot_page.get_plot_url(sol_from, sol_to, temp_type)
    expect(page).to_have_url(plot_url)
    plot_img = plot_page.get_plot_img()
    expect(plot_img).to_be_visible()
    plot_img.scroll_into_view_if_needed()

    screenshot_path = Path('tests/e2e/plotscr.png')
    page.screenshot(path=screenshot_path)
    text = f'Min Temp Trend from Sol {sol_from} to Sol {sol_to}'

    def compare(text1, text2):
        return True if text1.lower() == text2.lower() else False

    result_list = []
    reader = easyocr.Reader(['en'])
    info = reader.readtext(str(screenshot_path))
    for el in info:
        text2 = el[1]
        result_list.append(compare(text, text2))
    assert any(result_list)

        




