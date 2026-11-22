# filepath: /c:/Users/Ivan/Documents/py_projects/mars_weather_site/mars_weather_app/core/management/commands/create_test_user.py
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from dotenv import load_dotenv
import os

load_dotenv()

class Command(BaseCommand):
    help = 'Create a test user'

    def handle(self, *args, **kwargs):
        test_user_username = os.getenv('TEST_USER_USERNAME')
        test_user_password = os.getenv('TEST_USER_PASSWORD')
        if not test_user_username or not test_user_password:
            raise CommandError(
                'Set TEST_USER_USERNAME and TEST_USER_PASSWORD in the environment '
                'before creating the test user.'
            )

        if not User.objects.filter(username=test_user_username).exists():
            User.objects.create_user(
                username=test_user_username,
                password=test_user_password,
                email='testuser@example.com'
            )
            self.stdout.write(self.style.SUCCESS('Successfully created test user'))
        else:
            self.stdout.write(self.style.WARNING('Test user already exists'))