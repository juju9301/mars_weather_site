import os
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse

from .forms import PostForm
from weather.models import Weather


class CreateTestUserCommandTests(TestCase):
    def test_requires_test_user_credentials(self):
        with patch.dict(os.environ, {
            "TEST_USER_USERNAME": "",
            "TEST_USER_PASSWORD": "",
        }):
            with self.assertRaisesMessage(
                CommandError,
                "Set TEST_USER_USERNAME and TEST_USER_PASSWORD",
            ):
                call_command("create_test_user")


class PostFormTests(TestCase):
    def test_accepts_post_content_of_at_least_1000_characters(self):
        form = PostForm(data={
            "content": "x" * 1000,
            "font_color": "#000000",
            "background_color": "#ffffff",
        })

        self.assertTrue(form.is_valid(), form.errors)

    def test_post_content_textarea_is_large_and_full_width(self):
        widget_attrs = PostForm().fields["content"].widget.attrs

        self.assertEqual(widget_attrs["rows"], 12)
        self.assertEqual(widget_attrs["cols"], 60)
        self.assertEqual(widget_attrs["class"], "w-full")


class LandingPageWeatherSummaryTests(TestCase):
    def setUp(self):
        Weather.objects.create(
            terrestrial_date="2020-01-01",
            sol=10,
            min_temp=-80,
            max_temp=-20,
            min_gts_temp=-110,
            max_gts_temp=5,
            pressure=800,
            sunrise="05:30",
            sunset="17:30",
        )
        Weather.objects.create(
            terrestrial_date="2020-01-03",
            sol=12,
            min_temp=-90,
            max_temp=-10,
            min_gts_temp=-120,
            max_gts_temp=10,
            pressure=850,
            sunrise="05:29",
            sunset="17:31",
        )
        Weather.objects.create(
            terrestrial_date="2020-01-05",
            sol=14,
            min_temp=-70,
            max_temp=-30,
            min_gts_temp=-100,
            max_gts_temp=2,
            pressure=780,
            sunrise="05:28",
            sunset="17:32",
        )

    def test_shows_coverage_and_record_champions(self):
        response = self.client.get(reverse("core:index"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["coverage"], {
            "min_sol": 10,
            "max_sol": 14,
            "record_count": 3,
            "sol_span": 5,
            "missing_count": 2,
            "percentage": 60.0,
        })
        champions = {
            champion["label"]: champion
            for champion in response.context["champions"]
        }
        self.assertEqual(champions["Warmest air"]["record"].sol, 12)
        self.assertEqual(champions["Coldest air"]["record"].sol, 12)
        self.assertEqual(champions["Warmest ground"]["record"].sol, 12)
        self.assertEqual(champions["Coldest ground"]["record"].sol, 12)
        self.assertEqual(champions["Highest pressure"]["record"].sol, 12)
        self.assertEqual(champions["Lowest pressure"]["record"].sol, 14)

        self.assertContains(response, "Current Champions")
        self.assertContains(response, "Data Coverage")
        self.assertContains(response, "Missing sols in range")

    def test_handles_empty_and_null_measurements(self):
        Weather.objects.all().delete()
        empty_response = self.client.get(reverse("core:index"))
        self.assertIsNone(empty_response.context["coverage"])
        self.assertContains(empty_response, "No weather observations are currently available.")

        Weather.objects.create(
            terrestrial_date="2020-01-01",
            sol=10,
            min_temp=None,
            max_temp=None,
            min_gts_temp=None,
            max_gts_temp=None,
            pressure=None,
            sunrise="05:30",
            sunset="17:30",
        )
        response = self.client.get(reverse("core:index"))
        self.assertTrue(all(
            champion["record"] is None
            for champion in response.context["champions"]
        ))
