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

@pytest.mark.parametrize('sol_from,sol_to,temp_type', [
    ('10', '9', 'Min Temp'),
    ('10', '10', 'Max Temp')
])
def test_error_if_sol_to_lt_sol_from(page: Page, setup, sol_from, sol_to, temp_type):
    plot_page = setup
    plot_page.fill_plot_from_and_submit(sol_from, sol_to, temp_type)
    expect(plot_page.invalid_sol_range_error_message).to_be_visible()

@pytest.mark.skip(reason='Overwriting query params causes a Django server error. Left for demo purpose')
def test_no_data_available(page: Page, setup):
    plot_page = setup
    sol_from, sol_to, temp_type = '1', '9', 'min_temp'
    
    # Overwright query parameters of the GET plot request
    def change_url(route, request):
        url = request.url
        new_url = url.replace('sol_from=1', 'sol_from=2').replace('sol_to=9', 'sol_to=8')
        route.continue_(url=new_url)

    page.route('**/plot*', change_url)

    # Check that error message is visible
    plot_page.fill_plot_from_and_submit(sol_from, sol_to, temp_type)
    no_data_message = plot_page.get_no_data_error_message('2', '8')
    expect(no_data_message).to_be_visible()
    
@pytest.mark.ocr
def test_generate_plot_with_image_analysis(page: Page, setup):
    # Image analysis is expensive and works best with GPU; run with `pytest -m ocr` when needed.
    plot_page = setup
    sol_from, sol_to, temp_type = '10', '1000', 'min_temp'
    plot_page.fill_plot_from_and_submit(sol_from, sol_to, temp_type)
    plot_url = plot_page.get_plot_url(sol_from, sol_to, temp_type)
    expect(page).to_have_url(plot_url)
    plot_img = plot_page.get_plot_img()
    expect(plot_img).to_be_visible()
    plot_img.scroll_into_view_if_needed()

    # Make a screenshot of the plot and plot's title to target title
    screenshot_path = Path('tests/screenshots/plotscr.png')
    page.screenshot(path=screenshot_path)
    target_text = f'Min Temp Trend from Sol {sol_from} to Sol {sol_to}'
    assert_text_in_image(img_path=str(screenshot_path), target_text=target_text)




