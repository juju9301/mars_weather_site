from playwright.sync_api import Page, expect
from .base_page import BasePage
from faker import Faker

fake = Faker()


class AddPostPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.path = 'add_post/'
        self.url = self.base_url + self.path

        # Post form locators
        self.content_field = page.get_by_role('textbox', name='content')
        self.choose_image_input = page.locator('input[type="file"]')
        self.submit_button = page.get_by_role('button', name='Submit')

        # Random Mars image section locators
        self.get_mars_picture_button = page.get_by_role('button', name='Get Random Mars Picture')
        self.mars_picture = page.get_by_alt_text('Random Mars Picture')
        self.mars_picture_info = page.get_by_test_id('mars-pic-info')
        self.add_to_post_button = page.get_by_role('button', name='Add to Post')
        self.mars_image_url = page.locator('span#mars-image-url')

        self.rover_selector = page.locator('#rover-selector')
        self.rover_options = ['curiosity', 'opportunity', 'spirit']

    def navigate(self):
        self.page.goto(self.url)

    def create_post(self, content: str = fake.text(), file_path: str = None, submit: bool = True):
        self.content_field.fill(content)
        if file_path:
            with self.page.expect_file_chooser() as fc_info:
                self.choose_image_input.click()
                file_chooser = fc_info.value 
                file_chooser.set_files(files=file_path)
        if submit:
            self.submit_button.click()

        # yield file_path

    def fetch_mars_image(self, add_to_post: bool = True):
        max_attempts = 10
        current_attempt = 0
        
        while current_attempt < max_attempts:
            # Set up dialog handler for each attempt
            dialog_appeared = False
            
            def handle_dialog(dialog):
                nonlocal dialog_appeared
                dialog_appeared = True
                dialog.accept()
                
            self.page.on('dialog', handle_dialog)
            
            try:
                self.rover_selector.select_option('spirit')
                self.get_mars_picture_button.click()
                
                # Wait a bit to see if dialog appears
                self.page.wait_for_timeout(1000)
                
                # If dialog appeared, click the button again
                if dialog_appeared:
                    self.page.wait_for_timeout(500)  # Give time for dialog to close
                    self.get_mars_picture_button.click()
                    
                # Wait for the image to appear
                self.mars_picture.wait_for(state='visible')
                
                if add_to_post:
                    self.add_to_post_button.click()
                return True
                
            except TimeoutError:
                current_attempt += 1
                if current_attempt == max_attempts:
                    raise Exception('Failed to fetch Mars image after multiple attempts')
                continue
            finally:
                # Remove the dialog listener
                self.page.remove_listener('dialog', handle_dialog)