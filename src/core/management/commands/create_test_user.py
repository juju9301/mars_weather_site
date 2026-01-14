# filepath: /c:/Users/Ivan/Documents/py_projects/mars_weather_site/mars_weather_app/core/management/commands/create_test_user.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from dotenv import load_dotenv
import os

load_dotenv()

test_user_username, test_user_password = os.getenv('TEST_USER_USERNAME'), os.getenv('TEST_USER_PASSWORD')

class Command(BaseCommand):
    help = 'Create a test user'

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username=test_user_username).exists():
            User.objects.create_user(
                username=test_user_username,
                password=test_user_password,
                email='testuser@example.com'
            )
            self.stdout.write(self.style.SUCCESS('Successfully created test user'))
        else:
            self.stdout.write(self.style.WARNING('Test user already exists'))