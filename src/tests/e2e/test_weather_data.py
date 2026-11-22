import re

from playwright.sync_api import Page, expect

from ..utils.constants import BASE_URL


def test_weather_detail_displays_rems_metrics_and_quality_summary(page: Page):
    page.goto(f"{BASE_URL}3997")

    expect(page.get_by_text("-76 °C", exact=True)).to_be_visible()
    expect(page.get_by_text("-49.04 °C", exact=True)).to_be_visible()
    expect(page.get_by_text("-44.07 °C", exact=True)).to_be_visible()
    expect(page.get_by_text("-116.11 °C", exact=True)).to_be_visible()
    expect(page.get_by_text("693 Pa", exact=True)).to_be_visible()
    expect(page.get_by_text("5.0834 W/m²", exact=True)).to_be_visible()
    expect(page.get_by_text("10.7000 W/m²", exact=True)).to_be_visible()
    expect(page.get_by_text("05:38 LTST", exact=True)).to_be_visible()
    expect(page.get_by_test_id("rems-quality-summary")).to_contain_text(
        "Sol data summary"
    )
    expect(page.get_by_text("Solar longitude", exact=False)).to_have_count(0)
    expect(page.get_by_text("Pressure category", exact=False)).to_have_count(0)
    expect(page.get_by_text("UV irradiance index", exact=False)).to_have_count(0)


def test_weather_list_shows_compact_measurements(page: Page):
    page.set_viewport_size({"width": 1280, "height": 800})
    page.goto(f"{BASE_URL}list")
    sol_row = page.locator("tr").filter(has=page.locator('a[href="/4842"]'))
    table_panel = page.get_by_test_id("weather-table-panel")

    expect(page.locator("table")).to_be_visible()
    expect(table_panel).to_be_visible()
    expect(table_panel).to_have_css("border-radius", "0px")
    expect(table_panel).to_have_css("border-width", "1px")
    expect(table_panel).to_have_css("background-color", "rgb(255, 255, 255)")
    expect(page.locator("thead th").first).to_have_text("Sol")
    expect(sol_row.locator('th[scope="row"]')).to_have_text("Sol 4842")
    expect(sol_row).to_contain_text("-67 °C")
    expect(sol_row).to_contain_text("849 Pa")
    expect(page.locator("thead")).to_contain_text("Mean air")
    expect(page.locator("thead")).to_contain_text("Daylight UV mean")
    expect(page.get_by_text("Solar longitude", exact=False)).to_have_count(0)
    expect(page.get_by_text("Pressure category", exact=False)).to_have_count(0)
    expect(page.get_by_text("UV irradiance index", exact=False)).to_have_count(0)
    sol_row.hover()
    expect(sol_row.locator('th[scope="row"]')).to_have_css(
        "background-color", "rgb(243, 244, 246)"
    )


def test_weather_list_keeps_compact_cards_on_mobile(page: Page):
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(f"{BASE_URL}list")
    sol_card = page.locator('a[href="/4842"]').filter(has=page.locator("dl"))
    cards_panel = page.get_by_test_id("weather-cards-panel")

    expect(page.locator("table")).to_be_hidden()
    expect(cards_panel).to_be_visible()
    expect(cards_panel).to_have_css("border-radius", "0px")
    expect(cards_panel).to_have_css("background-color", "rgb(255, 255, 255)")
    expect(sol_card).to_be_visible()
    expect(sol_card).to_contain_text("-67 °C")
    expect(sol_card.locator("dl")).to_have_class(re.compile(r"\btext-sm\b"))
