from datetime import date

import pytest
from django.urls import reverse

from weather.models import Weather


@pytest.mark.django_db
def test_weather_list_paginates_50_sols(client):
    for sol in range(1, 52):
        Weather.objects.create(
            sol=sol,
            terrestrial_date=date(2020, 1, 1),
            sunrise='06:00',
            sunset='18:00',
        )

    first_page = client.get(reverse('weather:weather_list'))
    second_page = client.get(reverse('weather:weather_list'), {'page': 2})

    assert first_page.status_code == 200
    assert first_page.context['page_obj'].paginator.per_page == 50
    assert len(first_page.context['page_obj']) == 50
    assert second_page.status_code == 200
    assert len(second_page.context['page_obj']) == 1
