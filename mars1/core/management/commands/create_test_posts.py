from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Post
import os

IMAGE_URL = 'https://assets.science.nasa.gov/dynamicimage/assets/science/psd/mars/news_items/main_images/9306_https___mars.nasa-web.jpg?w=1200&h=1200&fit=clip&crop=faces%2Cfocalpoint'

class Command(BaseCommand):
    help = 'Create test posts for a user'

    def handle(self, *args, **kwargs):
        success_user_login = os.getenv('SUCCESS_TEST_USER_LOGIN')
        user = User.objects.filter(username=success_user_login).first()

        if not user:
            self.stdout.write(self.style.ERROR('Test user does not exist'))
            return

        # Create a post without a picture
        Post.objects.get_or_create(
            # title='Test Post without Picture',
            content='This is a test post without a picture.',
            author=user
        )

        # Create a post with a picture
        Post.objects.get_or_create(
            # title='Test Post with Picture',
            content='This is a test post with a picture.',
            author=user,
            image=IMAGE_URL
        )

        self.stdout.write(self.style.SUCCESS('Successfully created test posts'))