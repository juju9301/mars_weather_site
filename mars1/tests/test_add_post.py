from playwright.sync_api import Page, expect, sync_playwright
import playwright
import pytest
from faker import Faker
from .pages.add_post_page import AddPostPage
from .pages.login_page import LoginPage
from .pages.home_page import HomePage
import requests
# from core.models import Post

fake = Faker()

def make_api_request(method, endpoint, playwright: sync_playwright):
    context = playwright.request.new_context()
    if method == 'GET':
        resp = context.get(endpoint)
    elif method == 'POST':
        form_data = {'author': 1, 'content': 'api request content'}
        resp = context.post(endpoint, form_data)
    return resp

@pytest.fixture
def all_pages(page: Page):
    login_page = LoginPage(page)
    home_page = HomePage(page)
    add_post_page = AddPostPage(page)
    return login_page, home_page, add_post_page 
    # await Post.objects.all().delete()

def test_login_and_add_post(page: Page, all_pages):
    login_page, home_page, add_post_page = all_pages
    page.goto(home_page.base_url)
    expect(home_page.post).to_have_count(0)
    home_page.nav_login_button.click()
    expect(page).to_have_url(login_page.url)
    login_page.login(login_page.success_user_login, login_page.success_user_password)
    expect(page).to_have_url(home_page.url)
    home_page.add_post_button.click()
    expect(page).to_have_url(add_post_page.url)
    content = fake.text()
    add_post_page.content_field.fill(content)
    add_post_page.submit_button.click()
    expect(page).to_have_url(home_page.url)
    expect(home_page.post).to_have_count(1)
    # expect(home_page.post).to_have_text('this is a demo text')
    url = home_page.base_url + 'api/posts/delete'
    resp = requests.delete(url=url)
    # resp = make_api_request('POST', url, sync_playwright)
    assert resp.status_code == 204




