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
    plot_page.fill_plot_from_and_submit(sol_from, sol_to, temp_type)
    plot_url = plot_page.get_plot_url(sol_from, sol_to, temp_type)
    expect(page).to_have_url(plot_url)
    plot_img = plot_page.get_plot_img()
    expect(plot_img).to_be_visible()
    page.wait_for_timeout(5000)

@pytest.mark.parametrize('sol_from,sol_to,temp_type', [
    ('10', '9', 'Min Temp'),
    ('10', '10', 'Max Temp')
])
def test_error_if_sol_to_lt_sol_from(page: Page, setup, sol_from, sol_to, temp_type):
    plot_page = setup
    plot_page.fill_plot_from_and_submit(sol_from, sol_to, temp_type)
    expect(plot_page.invalid_sol_range_error_message).to_be_visible()

@pytest.mark.skip(reason='Image analysis is very expensive and works best with GPU. Left for demo purpose')
def test_generate_plot_with_image_analysis(page: Page, setup):
    plot_page = setup
    sol_from, sol_to, temp_type = '10', '1000', 'min_temp'
    plot_page.fill_plot_from_and_submit(sol_from, sol_to, temp_type)
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


        




