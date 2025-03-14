from ..pages.weather_plot_page import WeatherPlotPage
from playwright.sync_api import Page, expect, sync_playwright
import pytest
from pathlib import Path
from ..utils.helpers import assert_text_in_image

@pytest.fixture
def setup(page: Page):
    plot_page = WeatherPlotPage(page)
    plot_page.navigate()
    expect(page).to_have_url(plot_page.url)

    yield plot_page

def test_plot_is_generated(page: Page, setup):
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

@pytest.mark.skip(reason='Image analysis is very expensive and works best with GPU. Left for demo purpose')
def test_generate_plot_with_image_analysis(page: Page, setup):
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

    # Make a screenshot of the plot and plot's title to target title
    screenshot_path = Path('tests/e2e/plotscr.png')
    page.screenshot(path=screenshot_path)
    target_text = f'Min Temp Trend from Sol {sol_from} to Sol {sol_to}'
    assert_text_in_image(img_path=str(screenshot_path), target_text=target_text)


        




