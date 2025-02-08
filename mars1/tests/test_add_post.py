from playwright.sync_api import Page, expect
import pytest
from faker import Faker
from .pages.add_post_page import AddPostPage
from .pages.login_page import LoginPage
from .pages.home_page import HomePage
from .utils.helpers import check_timestamp, api_delete_posts
# from core.models import Post

fake = Faker()

@pytest.fixture
def setup(page: Page):

    # Initialize 3 pages required for test
    login_page = LoginPage(page)
    home_page = HomePage(page)
    add_post_page = AddPostPage(page)

    # Navigate to home page
    page.goto(home_page.base_url)
    expect(home_page.post).to_have_count(0)
    home_page.nav_login_button.click()
    expect(page).to_have_url(login_page.url)

    # Login
    login_page.login(login_page.test_user_username, login_page.test_user_password)
    expect(page).to_have_url(home_page.url)

    # Navigate to add post page
    home_page.add_post_button.click()
    expect(page).to_have_url(add_post_page.url)

    yield home_page, add_post_page 
    
    #Delete all posts
    api_delete_posts()

def test_login_and_add_post(page: Page, setup):
    home_page, add_post_page = setup

    expect(page).to_have_url(add_post_page.url)
    content = fake.text()
    add_post_page.create_post(content=content)
    expect(page).to_have_url(home_page.url)
    expect(home_page.post).to_have_count(1)
    expect(home_page.post_content).to_have_text(content)

def test_post_with_custom_picture(page: Page, setup):
    home_page, add_post_page = setup

    text = fake.text()
    add_post_page.create_post(text, add_post_page.test_file_jpg)
    expect(page).to_have_url(home_page.url)
    expect(home_page.post).to_have_count(1)
    expect(home_page.post_content).to_have_text(text)
    expect(home_page.post_image).to_be_visible()


def test_post_with_fetched_image(page: Page, setup):
    home_page, add_post_page = setup
    
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
    expect(home_page.post_author).to_contain_text(f'Posted by {home_page.test_user_username}')
    check_timestamp(home_page.post_author.text_content())

def test_mars_image_overrides_custome_image(page: Page, setup):
    home_page, add_post_page = setup

    add_post_page.create_post('', file_path=add_post_page.test_file_jpg, submit=False)
    filename = add_post_page.test_file_jpg.name
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

    # Submit post and verify that mars picture and content was posted
    add_post_page.submit_button.click()
    expect(home_page.post).to_have_count(1)
    expect(home_page.post_content).to_have_text(mars_info)
    expect(home_page.post_image).to_be_visible()

def test_mars_info_gets_appended(page: Page, setup):
    home_page, add_post_page = setup

    # Fill content text
    text = fake.text()
    add_post_page.create_post(text, submit=False)

    # Get random mars pic add add it to post
    # For later - need to handle case if image can't be fetched or fetched image can't be displayed
    add_post_page.get_mars_picture_button.click()
    add_post_page.add_to_post_button.click()
    mars_info = add_post_page.mars_picture_info.text_content()
    expect(add_post_page.content_field).to_have_value(text + mars_info)
    add_post_page.submit_button.click()
    expect(home_page.post).to_have_count(1)
    expect(home_page.post_content).to_have_text(text + mars_info)

def test_after_page_refresh_form_content_not_preserved(page: Page, setup):
    home_page, add_post_page = setup

    # Fill form content, select image
    content = fake.text()
    image = add_post_page.test_file_png
    add_post_page.create_post(content=content, file_path=image, submit=False)

    # Reload page and check that form is empty
    page.reload()
    expect(add_post_page.content_field).to_be_empty()
    expect(add_post_page.choose_image_input).not_to_have_value(fr'C:\fakepath\{image.name}')

def test_after_page_refresh_with_custome_image_new_data_is_submitted(page: Page, setup):
    home_page, add_post_page = setup

    # Fill the form with custom image 
    content = fake.text()
    image = add_post_page.test_file_jpg
    add_post_page.create_post(content=content, file_path=image, submit=False)

    # Reload the page and fill form again with custom image, submit
    new_content = fake.text()
    new_image = add_post_page.test_file_png
    add_post_page.create_post(content=new_content, file_path=new_image)

    # Check that the post posted contains new data
    expect(home_page.post_content).to_have_text(new_content)
    image_src = home_page.post_image.get_attribute('src')
    assert new_image.stem in image_src

def test_after_page_refresh_mars_image_replaced_with_custom(page: Page, setup):
    home_page, add_post_page = setup

    # Fill the form with mars image
    add_post_page.get_mars_picture_button.click()
    add_post_page.add_to_post_button.click()
    expect(add_post_page.mars_picture).to_be_visible()
    expect(add_post_page.mars_image_url).to_be_visible()

    # Refresh the page and fill with custom data, submit
    page.reload()
    content = fake.text()
    image = add_post_page.test_file_jpg
    add_post_page.create_post(content=content, file_path=image)

    # Check that post created with latest data
    expect(home_page.post_content).to_have_text(content)
    image_src = home_page.post_image.get_attribute('src')
    assert image.stem in image_src

@pytest.mark.xfail(reason='known issue with image url preservation')
def test_mars_image_data_is_preserved_after_going_back_to_homepage(page: Page, setup):
    home_page, add_post_page = setup

    # Get Mars image and add to post
    add_post_page.get_mars_picture_button.click()
    add_post_page.add_to_post_button.click()
    info = add_post_page.mars_picture_info.text_content()
    expect(add_post_page.content_field).to_have_value(info)
    expect(add_post_page.mars_image_url).to_be_visible()

    # Go back and forth and checkif data is preserved
    page.go_back()
    page.go_forward()
    expect(add_post_page.content_field).to_have_value(info)
    expect(add_post_page.mars_image_url).to_be_visible() #This line causes test to fail, element is hidden

    # Submit post
    add_post_page.submit_button.click()
    expect(home_page.post_content).to_have_text(info)
    expect(home_page.post_image).to_be_visible()

def test_custom_image_data_is_preserved_after_going_back_to_homepage(page: Page, setup):
    home_page, add_post_page = setup

    # Fill post form
    content = fake.text()
    image = add_post_page.test_file_jpg
    add_post_page.create_post(content=content, file_path=image, submit=False)

    # Check that after going back and forth the form data is preserved
    page.go_back()
    page.go_forward()
    expect(add_post_page.content_field).to_have_value(content)
    expect(add_post_page.choose_image_input).to_have_value((fr'C:\fakepath\{image.name}'))

    # Submit post and check the post result
    add_post_page.submit_button.click()
    expect(home_page.post_content).to_have_text(content)
    expect(home_page.post_image).to_be_visible()









