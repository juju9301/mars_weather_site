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
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(f"{BASE_URL}list")
    sol_row = page.locator("tr").filter(has=page.locator('a[href="/4842"]'))

    expect(page.locator("table")).to_be_visible()
    expect(page.locator("thead th").first).to_have_text("Sol")
    expect(sol_row.locator('th[scope="row"]')).to_have_text("Sol 4842")
    expect(sol_row).to_contain_text("-67 °C")
    expect(sol_row).to_contain_text("849 Pa")
    sol_row.hover()
    expect(sol_row.locator('th[scope="row"]')).to_have_css(
        "background-color", "rgb(243, 244, 246)"
    )


def test_weather_list_keeps_compact_cards_on_mobile(page: Page):
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(f"{BASE_URL}list")
    sol_card = page.locator('a[href="/4842"]').filter(has=page.locator("dl"))

    expect(page.locator("table")).to_be_hidden()
    expect(sol_card).to_be_visible()
    expect(sol_card).to_contain_text("-67 °C")
    expect(sol_card.locator("dl")).to_have_class(re.compile(r"\btext-sm\b"))
