import pytest
from playwright.sync_api import Page, expect

from ..pages.community_posts_page import CommunityPostsPage
from ..pages.home_page import HomePage


@pytest.fixture
def home_page(page: Page):
    home_page = HomePage(page)
    home_page.navigate()

    yield home_page

def test_homepage_title(page: Page, home_page: HomePage):
    expect(page).to_have_title('Mars Weather - Home')

def test_home_page_hero_header(home_page: HomePage):
    expect(home_page.hero_header).to_be_visible()
    expect(home_page.hero_header).to_have_text('Mars Weather')

def test_homepage_introduction_and_weather_document(home_page: HomePage):
    expect(home_page.page.get_by_role('heading', name='Hey there!')).to_be_visible()
    expect(home_page.page.get_by_role('link', name='GitHub repository')).to_have_attribute(
        'href', 'https://github.com/juju9301/mars_weather_site'
    )
    expect(home_page.recent_sol_title).to_be_visible()
    expect(home_page.page.get_by_test_id('recent-sol-document')).to_contain_text('°C')
    expect(home_page.page.get_by_test_id('recent-sol-document')).to_contain_text('Pa')
    expect(home_page.page.locator('#apod')).to_have_count(0)


def test_blog_nav_link_is_before_login_and_opens_blog(page: Page, home_page: HomePage):
    expect(page.get_by_role('heading', name='Blog')).to_have_count(0)
    nav_links = page.locator('.site-nav').get_by_role('link')
    expect(nav_links.nth(3)).to_have_text('Blog')
    expect(nav_links.nth(4)).to_have_text('Login')

    home_page.nav_blog.click()
    blog_page = CommunityPostsPage(page)
    expect(page).to_have_url(blog_page.url)
    expect(blog_page.heading).to_be_visible()
    expect(blog_page.post_creation_notice).to_be_visible()
    expect(blog_page.add_post_button).to_be_hidden()
    expect(blog_page.login_to_add_comment).to_have_count(
        blog_page.post.count()
    )

def test_rover_photo_loads_on_refresh_and_selection(page: Page):
    home_page = HomePage(page)
    rover_requests = []

    def rover_response(route):
        rover_requests.append(route.request.url)
        route.fulfill(json={
            'photos': [{
                'img_src': f'https://images.example/rover-{len(rover_requests)}.svg',
                'sol': 3000,
            }]
        })

    page.route('https://rovers.nebulum.one/**', rover_response)
    page.route(
        'https://images.example/**',
        lambda route: route.fulfill(
            content_type='image/svg+xml',
            body='<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32"></svg>',
        ),
    )
    home_page.navigate()
    expect(home_page.rover_photo).to_be_visible()
    expect(home_page.rover_photo).to_have_attribute('src', 'https://images.example/rover-1.svg')

    page.reload()
    expect(home_page.rover_photo).to_be_visible()
    expect(home_page.rover_photo).to_have_attribute('src', 'https://images.example/rover-2.svg')

    home_page.rover_selector.select_option('perseverance')
    expect(home_page.rover_photo).to_have_attribute('src', 'https://images.example/rover-3.svg')
    assert 'perseverance' in rover_requests[-1]