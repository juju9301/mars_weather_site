from .pages.add_comment_page import AddCommentPage
from .pages.home_page import HomePage
from .pages.login_page import LoginPage
from .pages.base_page import BasePage
from playwright.sync_api import Page, expect
import pytest
import requests
from faker import Faker
from .utils.helpers import api_create_post, api_delete_posts

fake = Faker()


@pytest.fixture
def setup(page: Page):
    # create a post
    post_id = api_create_post(image=True)

    # Create pages
    login_page = LoginPage(page)
    home_page = HomePage(page)
    add_comment_page = AddCommentPage(page)

    # Login
    login_page.navigate()
    login_page.login(login_page.test_user_username, login_page.test_user_password)

    yield post_id, home_page, add_comment_page

    # Delete all aposts
    api_delete_posts()


def test_add_comment(page: Page, setup):
    post_id, home_page, add_comment_page = setup
    first = home_page.get_nth(home_page.add_comment_button, 0)
    first.click()
    expect(page).to_have_url(add_comment_page.get_comment_page_url(post_id))
    expect(add_comment_page.no_comments_yet).to_be_visible()
    expect(add_comment_page.comment_form).to_be_visible()
    comment_text = fake.text()
    add_comment_page.comment_form_content.fill(comment_text)
    add_comment_page.comment_form_submit.click()
    expect(page).to_have_url(home_page.url)
    expect(home_page.comment).to_be_visible()
    expect(home_page.comment).to_have_count(1)
    expect(home_page.comment_author_date).to_be_visible()
    expect(home_page.comment_content).to_have_text(comment_text)


