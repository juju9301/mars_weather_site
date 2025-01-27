from playwright.sync_api import Page
from .base_page import BasePage


class HomePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.add_post_button = page.get_by_role('button', name='Add Post')
        self.add_comment_button = page.get_by_role('button', name='Add Comment')
        self.login_to_add_post = page.get_by_text('Please login to add a post.')
        self.login_to_add_comment = page.get_by_text('Please login to add a comment.')

        # post pagination locators
        self.pag_first = page.get_by_role('link', name='First')
        self.pag_next = page.get_by_role('link', name='Next')
        self.pag_last = page.get_by_role('link', name='Last')
        self.pag_previous = page.get_by_role('link', name='Previous')

    def navigate(self):
        self.page.goto(self.base_url)

