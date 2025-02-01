from playwright.sync_api import Page
from .base_page import BasePage


class HomePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = self.base_url
        self.add_post_button = page.locator('a[href="/add_post/"]', has_text='Add Post')
        self.add_comment_button = page.get_by_role('button', name='Add Comment')
        self.login_to_add_post = page.get_by_text('Please login to add a post.')
        self.login_to_add_comment = page.get_by_text('Please login to add a comment.')
        self.hero_header = page.get_by_test_id('hero-header')

        # post locators
        self.post = page.get_by_test_id('post')
        self.post_content = page.get_by_test_id('post-content')
        self.post_image = page.get_by_test_id('post-image')
        self.post_author = page.get_by_test_id('post-author')

        # post pagination locators
        self.pag_first = page.get_by_role('link', name='First')
        self.pag_next = page.get_by_role('link', name='Next')
        self.pag_last = page.get_by_role('link', name='Last')
        self.pag_previous = page.get_by_role('link', name='Previous')

    def navigate(self):
        self.page.goto(self.base_url)

    def get_nth(self, locator, n):
        return locator.nth(n)

