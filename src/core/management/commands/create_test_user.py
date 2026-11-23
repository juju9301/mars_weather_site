# filepath: /c:/Users/Ivan/Documents/py_projects/mars_weather_site/mars_weather_app/core/management/commands/create_test_user.py
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from dotenv import load_dotenv
import os

load_dotenv()

class Command(BaseCommand):
    help = 'Create or update the configured test user and test admin'

    def handle(self, *args, **kwargs):
        test_user_username = os.getenv('TEST_USER_USERNAME')
        test_user_password = os.getenv('TEST_USER_PASSWORD')
        if not test_user_username or not test_user_password:
            raise CommandError(
                'Set TEST_USER_USERNAME and TEST_USER_PASSWORD in the environment '
                'before creating the test user.'
            )

        test_admin_username = os.getenv('TEST_ADMIN_USERNAME')
        test_admin_password = os.getenv('TEST_ADMIN_PASSWORD')
        if bool(test_admin_username) != bool(test_admin_password):
            raise CommandError(
                'Set both TEST_ADMIN_USERNAME and TEST_ADMIN_PASSWORD, or neither.'
            )

        if not test_admin_username:
            test_admin_username = test_user_username
            test_admin_password = test_user_password
        elif (
            test_admin_username == test_user_username
            and test_admin_password != test_user_password
        ):
            raise CommandError(
                'TEST_USER and TEST_ADMIN cannot use the same username with '
                'different passwords.'
            )

        test_user_is_admin = test_admin_username == test_user_username
        self._create_or_update_user(
            test_user_username,
            test_user_password,
            'testuser@example.com',
            is_staff=test_user_is_admin,
        )
        self.stdout.write(self.style.SUCCESS('Test user is ready'))

        if not test_user_is_admin:
            self._create_or_update_user(
                test_admin_username,
                test_admin_password,
                'testadmin@example.com',
                is_staff=True,
            )
            self.stdout.write(self.style.SUCCESS('Test admin is ready'))

    @staticmethod
    def _create_or_update_user(username, password, email, *, is_staff):
        user = User.objects.filter(username=username).first()
        if user is None:
            User.objects.create_user(
                username=username,
                password=password,
                email=email,
                is_staff=is_staff,
            )
            return

        user.email = email
        user.is_staff = is_staff
        user.set_password(password)
        user.save(update_fields=['email', 'is_staff', 'password'])