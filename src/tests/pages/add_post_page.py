from playwright.sync_api import Page, expect
from .base_page import BasePage


class AddPostPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.path = 'add_post/'
        self.url = self.base_url + self.path

        # Post form locators
        self.content_field = page.get_by_role('textbox', name='content')
        self.choose_image_input = page.locator('input[type="file"]')
        self.submit_button = page.get_by_role('button', name='Submit')
        self.bg_color_input = page.locator('#id_background_color')
        self.font_color_input = page.locator('#id_font_color')

        self.form_error = page.get_by_text('You must provide either content or an image.')

        # Random Mars image section locators
        self.get_mars_picture_button = page.get_by_role('button', name='Get Random Mars Picture')
        self.mars_picture = page.get_by_alt_text('Random Mars Picture')
        self.mars_picture_info = page.get_by_test_id('mars-pic-info')
        self.add_to_post_button = page.get_by_role('button', name='Add to Post')
        self.mars_image_url = page.locator('span#mars-image-url')

        self.rover_selector = page.locator('#rover-selector')
        self.rover_options = ['curiosity', 'perseverance']

    def navigate(self):
        self.page.goto(self.url)

    def create_post(self, content: str, file_path: str = None, submit: bool = True):
        self.content_field.fill(content)
        if file_path:
            with self.page.expect_file_chooser() as fc_info:
                self.choose_image_input.click()
                file_chooser = fc_info.value 
                file_chooser.set_files(files=file_path)
        if submit:
            self.submit_button.click()

        # yield file_path

    def fetch_mars_image(self):
        # Fetching Mars rover image can result in an error or invalid image. 
        # Here we attempt to fetch it 5 times in order to decrease test flakiness.
        max_attempts = 5
        current_attempt = 1

        self.page.on('dialog', lambda dialog: dialog.accept())

        for attempt in range(1, max_attempts + 1):
            try:
                self.get_mars_picture_button.click()
                expect(self.mars_picture).to_be_visible()
                # Found image
                break
            except AssertionError:
                if attempt == max_attempts:
                    raise TimeoutError(f'Failed to fetch mars image after {max_attempts} attempts')