from ..pages.add_comment_page import AddCommentPage
from ..pages.home_page import HomePage
from ..pages.login_page import LoginPage
from ..pages.base_page import BasePage
from playwright.sync_api import Page, expect
import pytest
from faker import Faker
from ..utils.helpers import api_create_post, api_delete_posts

fake = Faker()


@pytest.fixture
def setup(page: Page):
    # Create a post
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

    # Find first ['Add comment'] button and click
    expect(home_page.add_comment_button).to_have_count(1)
    first = home_page.get_nth(home_page.add_comment_button, 0)
    first.click()

    # Check that the comment form is displayed
    expect(page).to_have_url(add_comment_page.get_comment_page_url(post_id))
    expect(add_comment_page.no_comments_yet).to_be_visible()
    expect(add_comment_page.comment_form).to_be_visible()

    # Fill the comment form and submit
    comment_text = fake.text()
    add_comment_page.comment_form_content.fill(comment_text)
    add_comment_page.comment_form_submit.click()
    
    # Check that comment has been posted and displayed under the post
    expect(page).to_have_url(home_page.url)
    expect(home_page.comment).to_be_visible()
    expect(home_page.comment).to_have_count(1)
    expect(home_page.comment_author_date).to_be_visible()
    expect(home_page.comment_content).to_have_text(comment_text)

def test_comment_message_is_preserved_after_going_back_to_home_page(page: Page, setup):
    post_id, home_page, add_comment_page = setup

    # Go to add comment page and fill comment form
    home_page.add_comment_button.click()
    content = fake.text()
    add_comment_page.comment_form_content.fill(content)

    # Go back to homepage and forward to the comment form
    page.go_back()
    page.go_forward()
    expect(add_comment_page.comment_form_content).to_have_value(content)

