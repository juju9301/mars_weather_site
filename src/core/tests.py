import os
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .forms import PostForm
from .models import Comment, Post
from weather.models import Weather


class ApiAuthorAssignmentTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username="post-api-admin",
            password="test-password",
            is_staff=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.staff_user)

    def test_post_api_assigns_authenticated_author(self):
        response = self.client.post(
            reverse("core:post_list_create"),
            {"content": "API-created post"},
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["author"], self.staff_user.pk)
        self.assertEqual(Post.objects.get().author, self.staff_user)

    def test_comment_api_assigns_authenticated_author(self):
        post = Post.objects.create(author=self.staff_user, content="Existing post")

        response = self.client.post(
            reverse("core:comment_list_create"),
            {"post": post.pk, "content": "API-created comment"},
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["author"], self.staff_user.pk)
        self.assertEqual(Comment.objects.get().author, self.staff_user)


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

    def test_creates_user_and_staff_admin_with_configured_credentials(self):
        credentials = {
            "TEST_USER_USERNAME": "test-user",
            "TEST_USER_PASSWORD": "user-password",
            "TEST_ADMIN_USERNAME": "test-admin",
            "TEST_ADMIN_PASSWORD": "admin-password",
        }
        with patch.dict(os.environ, credentials):
            call_command("create_test_user", verbosity=0)

        user = User.objects.get(username="test-user")
        admin = User.objects.get(username="test-admin")
        self.assertTrue(user.check_password("user-password"))
        self.assertFalse(user.is_staff)
        self.assertTrue(admin.check_password("admin-password"))
        self.assertTrue(admin.is_staff)

    def test_resets_password_for_existing_test_user(self):
        user = User.objects.create_user(
            username="test-user",
            password="old-password",
        )
        with patch.dict(os.environ, {
            "TEST_USER_USERNAME": "test-user",
            "TEST_USER_PASSWORD": "new-password",
            "TEST_ADMIN_USERNAME": "",
            "TEST_ADMIN_PASSWORD": "",
        }):
            call_command("create_test_user", verbosity=0)

        user.refresh_from_db()
        self.assertTrue(user.check_password("new-password"))
        self.assertTrue(user.is_staff)


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
