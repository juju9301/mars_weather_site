from .base_page import BasePage
from playwright.sync_api import Page


class AddCommentPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # self.url = self.get_comment_page_path
        # Relevant post locators
        self.post = page.get_by_test_id('post')
        self.post_author = page.get_by_test_id('post-author')
        self.post_content = page.get_by_test_id('post-content')
        self.post_image = page.get_by_test_id('post-image')
        self.post_date = page.get_by_test_id('post-date')

        # Existing comment locators
        self.comment = page.get_by_test_id('comment')
        self.comment_author = page.get_by_test_id('comment-author')
        self.comment_content = page.get_by_test_id('comment-content')
        self.comment_date = page.get_by_test_id('comment-date')
        self.no_comments_yet = page.get_by_text('No comments yet.')
        
        # New comment form locators
        self.comment_form = page.get_by_test_id('comment-form')
        self.comment_form_content = page.get_by_test_id('comment-form-content')
        self.comment_form_submit = page.get_by_role('button', name='Submit')

    def get_comment_page_path(self, post_id):
        return f'add_comment/{post_id}/'
    
    def get_comment_page_url(self, post_id):
        return self.base_url + f'add_comment/{post_id}/'




