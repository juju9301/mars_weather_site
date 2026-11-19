from playwright.sync_api import Page

from .base_page import BasePage


class CommunityPostsPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = f'{self.base_url}community-posts/'
        self.heading = page.get_by_role('heading', name='Blog')
        self.add_post_button = page.get_by_test_id('add-post')
        self.post_creation_notice = page.get_by_test_id('admin-only-posts')
        self.no_posts = page.get_by_test_id('no-blog-posts')

        self.post = page.get_by_test_id('post')
        self.post_content = page.get_by_test_id('post-content')
        self.post_image = page.get_by_test_id('post-image')
        self.post_author = page.get_by_test_id('post-author')

        self.add_comment_button = page.get_by_role('link', name='Add Comment')
        self.login_to_add_comment = page.get_by_test_id('login-to-add-comment')
        self.comment = page.get_by_test_id('comment')
        self.comment_author_date = page.get_by_test_id('comment-author-date')
        self.comment_content = page.get_by_test_id('comment-content')

        self.pag_first = page.get_by_role('link', name='First')
        self.pag_next = page.get_by_role('link', name='Next')
        self.pag_last = page.get_by_role('link', name='Last')
        self.pag_previous = page.get_by_role('link', name='Previous')

    def navigate(self):
        self.page.goto(self.url)
