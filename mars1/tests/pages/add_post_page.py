from playwright.sync_api import Page
from .base_page import BasePage


class AddPostPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.path = 'add_post/'
        self.url = self.base_url + self.path
        self.content_field = page.get_by_role('textbox', name='content')
        self.choose_image_input = page.locator('[input#id_image]')
        self.submit_button = page.get_by_role('button', name='Submit')
