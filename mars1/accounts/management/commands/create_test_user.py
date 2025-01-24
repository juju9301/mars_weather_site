# filepath: /c:/Users/Ivan/Documents/py_projects/mars_weather_site/mars1/accounts/management/commands/create_test_user.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from dotenv import load_dotenv
import os

load_dotenv()

success_user_login, success_user_password = os.getenv('SUCCESS_TEST_USER_LOGIN')

class Command(BaseCommand):
    help = 'Create a test user'

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username=success_user_login).exists():
            User.objects.create_user(
                username=success_user_login,
                password=success_user_password,
                email='testuser@example.com'
            )
            self.stdout.write(self.style.SUCCESS('Successfully created test user'))
        else:
            self.stdout.write(self.style.WARNING('Test user already exists'))