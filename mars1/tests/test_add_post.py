from playwright.sync_api import Page, expect, sync_playwright
import playwright
import pytest
from faker import Faker
from .pages.add_post_page import AddPostPage
from .pages.login_page import LoginPage
from .pages.home_page import HomePage
import requests
import re
# from core.models import Post

fake = Faker()

@pytest.fixture
def all_pages(page: Page):
    # initialize 3 pages required for test
    login_page = LoginPage(page)
    home_page = HomePage(page)
    add_post_page = AddPostPage(page)
    yield login_page, home_page, add_post_page 
    
    # delete all posts after each test 
    url = home_page.base_url + 'api/posts/delete'
    resp = requests.delete(url=url)
    assert resp.status_code == 204

def check_timestamp(text):
        timestamp_regex = r'on \w{3}\. \d{1,2}, \d{4}, \d{1,2}:\d{2} [ap]\.m\.'
        assert re.search(timestamp_regex, text)

# @pytest.mark.e2e
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
    add_post_page.add_post(content=content)
    expect(page).to_have_url(home_page.url)
    expect(home_page.post).to_have_count(1)
    expect(home_page.post_content).to_have_text(content)

def test_post_with_custom_picture(page: Page, all_pages):
    login_page, home_page, add_post_page = all_pages
    login_page.navigate()
    login_page.login(login_page.success_user_login, login_page.success_user_password)
    home_page.add_post_button.click()
    text = fake.text()
    add_post_page.create_post(text, add_post_page.test_file_jpg)
    expect(page).to_have_url(home_page.url)
    expect(home_page.post).to_have_count(1)
    expect(home_page.post_content).to_have_text(text)
    expect(home_page.post_image).to_be_visible()


def test_post_with_fetched_image(page: Page, all_pages):
    login_page, home_page, add_post_page = all_pages
    login_page.navigate()
    login_page.login(login_page.success_user_login, login_page.success_user_password)
    home_page.add_post_button.click()
    add_post_page.get_mars_picture_button.click()
    expect(add_post_page.mars_picture).to_be_visible()
    expect(add_post_page.mars_picture_info).to_be_visible()
    mars_info = add_post_page.mars_picture_info.text_content()
    mars_pic_url = add_post_page.mars_picture.get_attribute('src')
    add_post_page.add_to_post_button.click()
    expect(add_post_page.content_field).to_have_value(mars_info)
    expect(add_post_page.choose_image_input).to_be_hidden()
    expect(add_post_page.mars_image_url).to_have_text(mars_pic_url)
    add_post_page.submit_button.click()
    expect(home_page.post).to_have_count(1)
    expect(home_page.post_content).to_have_text(mars_info)
    expect(home_page.post_image).to_be_visible()
    expect(home_page.post_author).to_contain_text(f'Posted by {home_page.success_user_login}')
    check_timestamp(home_page.post_author.text_content())

def test_mars_image_overrides_custome_image(page: Page, all_pages):
    login_page, home_page, add_post_page = all_pages
    login_page.navigate()
    login_page.login(login_page.success_user_login, login_page.success_user_password)
    add_post_page.navigate()
    add_post_page.create_post('', file_path=add_post_page.test_file_jpg, submit=False)
    filename = add_post_page.test_file_jpg.split('\\')[-1]
    expect(add_post_page.choose_image_input).to_have_value(fr'C:\fakepath\{filename}')
    # get mars image
    add_post_page.get_mars_picture_button.click()
    expect(add_post_page.mars_picture).to_be_visible()
    # add mars image to post and verify that image is overriden and content added
    mars_info = add_post_page.mars_picture_info.text_content()
    mars_pic_url = add_post_page.mars_picture.get_attribute('src')
    add_post_page.add_to_post_button.click()
    expect(add_post_page.mars_image_url).to_be_visible()
    expect(add_post_page.content_field).to_have_value(mars_info)
    expect(add_post_page.choose_image_input).to_be_hidden()
    expect(add_post_page.mars_image_url).to_have_text(mars_pic_url)
    # submit post and verify that mars picture and content was posted
    add_post_page.submit_button.click()
    expect(home_page.post).to_have_count(1)
    expect(home_page.post_content).to_have_text(mars_info)
    expect(home_page.post_image).to_be_visible()







