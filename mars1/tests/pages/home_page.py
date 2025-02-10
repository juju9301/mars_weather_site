from playwright.sync_api import Page
from .base_page import BasePage


class HomePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = self.base_url

        self.add_post_button = page.locator('a[href="/add_post/"]', has_text='Add Post')
        self.add_comment_button = page.get_by_role('link', name='Add Comment')
        self.login_to_add_post = page.get_by_text('Please login to add a post.')
        self.login_to_add_comment = page.get_by_text('Please login to add a comment.')
        self.hero_header = page.get_by_test_id('hero-header')

        # Post locators
        self.post = page.get_by_test_id('post')
        self.post_content = page.get_by_test_id('post-content')
        self.post_image = page.get_by_test_id('post-image')
        self.post_author = page.get_by_test_id('post-author')

        # Comment locators
        self.comment = page.get_by_test_id('comment')
        self.comment_author_date = page.get_by_test_id('comment-author-date')
        self.comment_content = page.get_by_test_id('comment-content')

        # Post pagination locators
        self.pag_first = page.get_by_role('link', name='First')
        self.pag_next = page.get_by_role('link', name='Next')
        self.pag_last = page.get_by_role('link', name='Last')
        self.pag_previous = page.get_by_role('link', name='Previous')

        # NASA's picture of the day 
        self.apod_section = page.locator('#apod')
        self.apod_title = page.get_by_text('NASA\'s Space Picture of the Day')
        self.apod_content = page.locator('#apod-content')
        self.apod_text_title = page.get_by_test_id('apod-text-title')
        self.apod_text = page.get_by_test_id('apod-text')
        self.apod_media = page.get_by_test_id('apod-media')

        # Most recent sol weather section locators
        self.recent_sol_title = page.get_by_text('Most Recent Sol Weather')

    def navigate(self):
        self.page.goto(self.base_url)

    def get_nth(self, locator, n):
        return locator.nth(n)

