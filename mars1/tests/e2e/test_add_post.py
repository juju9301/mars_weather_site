from playwright.sync_api import Page, expect
import pytest
from faker import Faker
from ..pages.add_post_page import AddPostPage
from ..pages.login_page import LoginPage
from ..pages.home_page import HomePage
from ..utils.helpers import check_timestamp, api_delete_posts


fake = Faker()

@pytest.fixture
def setup(page: Page):

    # Initialize 3 pages required for test
    login_page = LoginPage(page)
    home_page = HomePage(page)
    add_post_page = AddPostPage(page)

    # Navigate to home page
    page.goto(home_page.base_url)

    # A temporary solution with post deletion for local testing
    try:
        expect(home_page.post).to_have_count(0)
    except AssertionError:
        api_delete_posts()

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

def test_add_post_without_image(page: Page, setup):
    home_page, add_post_page = setup
    content = fake.text()
    add_post_page.create_post(content=content)
    expect(page).to_have_url(home_page.url)
    expect(home_page.post).to_have_count(1)
    expect(home_page.post_content).to_have_text(content)
    expect(home_page.post_author).to_contain_text(f'Posted by {home_page.test_user_username}')
    check_timestamp(home_page.post_author.text_content())

def test_post_with_custom_image(page: Page, setup):
    home_page, add_post_page = setup
    content = fake.text()
    add_post_page.create_post(content, add_post_page.test_file_jpg)
    expect(page).to_have_url(home_page.url)
    expect(home_page.post).to_have_count(1)
    expect(home_page.post_content).to_have_text(content)
    expect(home_page.post_image).to_be_visible()


def test_post_with_fetched_image(page: Page, setup):
    home_page, add_post_page = setup

    # Fetch random Mars image and check presence of all related elements
    add_post_page.fetch_mars_image()
    expect(add_post_page.mars_picture).to_be_visible()
    expect(add_post_page.mars_picture_info).to_be_visible()
    mars_info = add_post_page.mars_picture_info.text_content()
    mars_pic_url = add_post_page.mars_picture.get_attribute('src')

    # Add Mars image to post and check all relevant changes
    add_post_page.add_to_post_button.click()
    expect(add_post_page.content_field).to_have_value(mars_info)
    expect(add_post_page.choose_image_input).to_be_hidden()
    expect(add_post_page.mars_image_url).to_have_text(mars_pic_url)

    # Submit post and verify correct post creation on home page
    add_post_page.submit_button.click()
    expect(home_page.post).to_have_count(1)
    expect(home_page.post_content).to_have_text(mars_info)
    expect(home_page.post_image).to_be_visible()
    expect(home_page.post_author).to_contain_text(f'Posted by {home_page.test_user_username}')
    check_timestamp(home_page.post_author.text_content())

def test_add_post_without_text(page: Page, setup):
    home_page, add_post_page = setup
    add_post_page.create_post('', file_path=add_post_page.test_file_jpg)
    expect(home_page.post).to_be_visible()

def test_post_require_content_or_image(page: Page, setup):
    home_page, add_post_page = setup

    # Verify failed post submission if image and content are absent
    add_post_page.create_post('')
    expect(page).to_have_url(add_post_page.url)
    expect(add_post_page.form_error).to_be_visible()

    # Verify absence of new posts on home page
    home_page.navigate()
    expect(home_page.post).not_to_be_visible()

def test_mars_image_overrides_custome_image(page: Page, setup):
    home_page, add_post_page = setup

    add_post_page.create_post('', file_path=add_post_page.test_file_jpg, submit=False)
    filename = add_post_page.test_file_jpg.name
    expect(add_post_page.choose_image_input).to_have_value(fr'C:\fakepath\{filename}')

    # Get mars image
    add_post_page.fetch_mars_image()
    expect(add_post_page.mars_picture).to_be_visible()

    # Add mars image to post and verify that image is overriden and content added
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
    content = fake.text()
    add_post_page.create_post(content, submit=False)

    # Get random mars pic add add it to post
    # For later - need to handle case if image can't be fetched or fetched image can't be displayed
    add_post_page.fetch_mars_image()
    add_post_page.add_to_post_button.click()
    mars_info = add_post_page.mars_picture_info.text_content()
    expect(add_post_page.content_field).to_have_value(content + mars_info)
    add_post_page.submit_button.click()
    expect(home_page.post).to_have_count(1)
    expect(home_page.post_content).to_have_text(content + mars_info)

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
    add_post_page.fetch_mars_image()
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
    add_post_page.fetch_mars_image()
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

def test_submit_resulted_in_500(page: Page, setup):
    home_page, add_post_page = setup
    page.route('**/add_post/', lambda route: route.fulfill(
    status=500, content_type='text/html', body='''
<!doctype html>
<html lang="en">
<head>
  <title>500 Internal Server Error</title>
</head>
<body>
  <h1>Internal Server Error</h1>
</body>
''' if route.request.method == 'POST' else route.continue_()
    ))

    # Fill post content and submit
    content = fake.text()
    add_post_page.content_field.fill(content)
    add_post_page.submit_button.click()
    expect(page).to_have_url(add_post_page.url)
    expect(add_post_page.content_field).not_to_be_visible()
    expect(page.get_by_text('Internal Server Error')).to_be_visible()

def test_post_colors(page: Page, setup):
    home_page, add_post_page = setup
    content = fake.text()
    bg_color = '#000000'
    font_color = '#ffff00'

    # Set the color values to both inputs and submit
    add_post_page.bg_color_input.evaluate(f'element => element.value = "{bg_color}"')
    add_post_page.font_color_input.evaluate(f'element => element.value = "{font_color}"')

    # Submit form and assert
    add_post_page.create_post(content=content)
    expect(home_page.post).to_have_attribute('style', f'background-color: {bg_color};')
    expect(home_page.post_content).to_have_attribute('style', f'color: {font_color};')




