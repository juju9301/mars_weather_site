from django.test import TestCase
from django.urls import reverse

from .models import Weather


class WeatherPlotViewTests(TestCase):
    def setUp(self):
        for sol, offset in ((10, 0), (12, 2), (15, 5)):
            Weather.objects.create(
                terrestrial_date=f"2020-01-{offset + 1:02d}",
                sol=sol,
                ls=100 + offset,
                min_temp=-70 + offset,
                max_temp=-20 + offset,
                min_gts_temp=-110 + offset,
                max_gts_temp=5 + offset,
                pressure=800 + offset,
                sunrise=f"05:{30 + offset:02d}",
                sunset=f"17:{20 + offset:02d}",
            )

    def test_plot_form_shows_bounds_without_listing_every_sol(self):
        response = self.client.get(reverse("weather:generate_weather_plot"))

        self.assertContains(response, "Available sol range: 10–15.")
        self.assertContains(response, 'type="number" name="sol_from"')
        self.assertContains(response, 'type="number" name="sol_to"')
        self.assertNotContains(response, '<option value="10">')
        self.assertContains(
            response,
            '<option value="min_gts_temp">Coldest burst mean</option>',
        )

    def test_rejects_reversed_out_of_range_and_missing_endpoint_sols(self):
        url = reverse("weather:generate_weather_plot")
        cases = (
            ({"sol_from": 12, "sol_to": 10, "metric": "ls"}, "Sol to must be greater than Sol from."),
            ({"sol_from": 9, "sol_to": 15, "metric": "ls"}, "Enter a sol between 10 and 15."),
            ({"sol_from": 11, "sol_to": 15, "metric": "ls"}, "Sol 11 is not present in the weather database."),
        )

        for query, error in cases:
            with self.subTest(query=query):
                self.assertContains(self.client.get(url, query), error)

    def test_generates_plots_for_all_supported_metrics(self):
        url = reverse("weather:generate_weather_plot")
        metrics = (
            "ls",
            "max_temp",
            "min_temp",
            "max_gts_temp",
            "min_gts_temp",
            "pressure",
            "sunrise",
            "sunset",
        )

        for metric in metrics:
            with self.subTest(metric=metric):
                response = self.client.get(
                    url,
                    {"sol_from": 10, "sol_to": 15, "metric": metric},
                )
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context["plot_image"].startswith("data:image/png;base64,"))
                if metric == "min_gts_temp":
                    self.assertEqual(
                        response.context["metric_label"],
                        "Coldest burst mean",
                    )

    def test_reports_when_selected_metric_has_no_data(self):
        Weather.objects.filter(sol__in=(12, 15)).update(ls=None)

        response = self.client.get(
            reverse("weather:generate_weather_plot"),
            {"sol_from": 12, "sol_to": 15, "metric": "ls"},
        )

        self.assertContains(response, "No solar longitude data is available between Sol 12 and Sol 15.")
        self.assertNotIn("plot_image", response.context)

    def test_handles_an_empty_weather_database(self):
        Weather.objects.all().delete()

        response = self.client.get(reverse("weather:generate_weather_plot"))

        self.assertContains(response, "No weather observations are currently available.")
