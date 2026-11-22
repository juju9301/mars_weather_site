from datetime import date

import pytest
from django.urls import reverse

from weather.models import Weather


@pytest.mark.django_db
def test_weather_pages_show_new_metrics_and_hide_legacy_fields(client):
    Weather.objects.create(
        terrestrial_date=date(2023, 11, 4),
        sol=3997,
        min_temp=-76,
        max_temp=-10,
        mean_temp=-49.04,
        min_gts_temp=-83,
        mean_gts_temp=-44.07,
        raw_min_gts_temp=-116.11,
        max_gts_temp=2,
        pressure=693,
        sunrise="05:38",
        sunset="17:50",
        uv_abc_daylight_mean=5.0834,
        uv_abc_daylight_peak=10.7,
        rems_quality_summary={
            "confidence_policy": "All non-missing values are included.",
            "products": {"rmd_samples": 10, "adr_samples": 10},
            "metrics": {
                "air_temperature": {
                    "valid_samples": 10,
                    "total_samples": 10,
                    "confidence_flag_counts": {"111": 10},
                },
                "ground_temperature": {
                    "valid_samples": 9,
                    "total_samples": 10,
                    "burst_count": 2,
                    "coldest_burst_valid_samples": 3,
                    "coldest_burst_mean_celsius": -83.3,
                    "confidence_flag_counts": {"0111": 9, "XXXX": 1},
                },
                "pressure": {
                    "valid_samples": 10,
                    "total_samples": 10,
                    "confidence_flag_counts": {"11": 10},
                },
                "uv_abc_daylight": {
                    "valid_samples": 5,
                    "total_samples": 10,
                    "daylight_samples": 6,
                    "confidence_flag_counts": {"01110": 5},
                },
            },
            "product_staging": {
                "RMD": {"routed_in_rows": 2, "duplicate_rows_removed": 0},
                "ADR": {"routed_in_rows": 2, "duplicate_rows_removed": 0},
            },
        },
    )

    pages = (
        client.get(reverse("weather:weather_list")),
        client.get(reverse("weather:weather_detail", args=(3997,))),
        client.get(reverse("core:index")),
    )
    expected_values = (
        "-49.04 °C",
        "-44.07 °C",
        "-116.11 °C",
        "5.0834 W/m²",
        "10.7000 W/m²",
    )
    hidden_labels = (
        "Solar longitude",
        "Pressure category",
        "UV irradiance index",
    )

    for response in pages:
        assert response.status_code == 200
        content = response.content.decode()
        for value in expected_values:
            assert value in content
        for label in hidden_labels:
            assert label not in content

    detail_content = pages[1].content.decode()
    assert "Sol data summary" in detail_content
    assert "9 / 10 valid samples" in detail_content
    assert "0111: 9" in detail_content
    assert "2 acquisition bursts" in detail_content
    assert "RMD rows routed in: 2" in detail_content
