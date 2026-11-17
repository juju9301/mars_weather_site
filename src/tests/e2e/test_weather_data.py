import re

from playwright.sync_api import Page, expect

from ..utils.constants import BASE_URL


def test_weather_detail_displays_measurement_units(page: Page):
    page.goto(f"{BASE_URL}4842")

    expect(page.get_by_text("-67 °C", exact=True)).to_be_visible()
    expect(page.get_by_text("849 Pa", exact=True)).to_be_visible()
    expect(page.get_by_text("247°", exact=True)).to_be_visible()
    expect(page.get_by_text("05:41 LTST", exact=True)).to_be_visible()


def test_weather_list_shows_compact_measurements(page: Page):
    page.goto(f"{BASE_URL}list")
    sol_card = page.locator('a[href="/4842"]')

    expect(sol_card).to_contain_text("-67 °C")
    expect(sol_card).to_contain_text("849 Pa")
    expect(sol_card.locator("dl")).to_have_class(re.compile(r"\btext-sm\b"))
