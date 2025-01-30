from playwright.sync_api import Page
from .base_page import BasePage


class AddPostPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.path = 'add_post/'
        self.url = self.base_url + self.path
        self.content_field = page.get_by_role('textbox', name='content')
        self.choose_image_input = page.locator('input[type="file"]')
        self.submit_button = page.get_by_role('button', name='Submit')

    def navigate(self):
        self.page.goto(self.url)

    def add_post(self, content: str, file_path: str = None):
        self.content_field.fill(content)
        if file_path:
            with self.page.expect_file_chooser() as fc_info:
                self.choose_image_input.click()
                file_chooser = fc_info.value 
                file_chooser.set_files(files=file_path)
        self.submit_button.click()
