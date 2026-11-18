import re
from urllib.parse import parse_qs, urlparse
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect


def test_add_post_retries_empty_sol_and_unloadable_image(page: Page):
    template_path = Path(__file__).parent.parent / 'core' / 'templates' / 'core' / 'add_post.html'
    template = template_path.read_text(encoding='utf-8')
    scripts = re.findall(r'<script>(.*?)</script>', template, re.DOTALL)
    assert len(scripts) == 1

    rover_requests = []

    def rover_response(route):
        rover_requests.append(route.request.url)
        if len(rover_requests) == 1:
            route.fulfill(
                json={'photos': []},
                headers={'access-control-allow-origin': '*'},
            )
        else:
            image_name = 'unavailable.svg' if len(rover_requests) == 2 else 'rover.svg'
            route.fulfill(
                json={
                    'photos': [{
                        'img_src': f'https://images.example/{image_name}',
                        'sol': 3200,
                    }]
                },
                headers={'access-control-allow-origin': '*'},
            )

    def image_response(route):
        if route.request.url.endswith('unavailable.svg'):
            route.fulfill(status=404, content_type='image/svg+xml', body='')
        else:
            route.fulfill(
                content_type='image/svg+xml',
                body='<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32"></svg>',
            )

    page.route('https://rovers.nebulum.one/**', rover_response)
    page.route('https://images.example/**', image_response)
    page.set_content(
        """
        <form>
            <textarea id="id_content"></textarea>
            <input id="random_mars_image_url" name="random_mars_image_url">
            <input type="file">
            <span id="mars-image-url"></span>
        </form>
        <select id="rover-selector">
            <option value="curiosity">Curiosity</option>
            <option value="perseverance">Perseverance</option>
        </select>
        <button id="get-random-mars-picture" type="button">Get Random Mars Picture</button>
        <p id="rover-photo-status" role="status" aria-live="polite"></p>
        <div id="random-mars-picture-container"></div>
        <button id="add-to-post" type="button" class="hidden">Add to Post</button>
        <script>""" + scripts[0] + """</script>
        """,
        wait_until='domcontentloaded',
    )

    page.get_by_role('button', name='Get Random Mars Picture').click()
    photo_info = page.get_by_test_id('mars-pic-info')
    expect(photo_info).to_have_text('Mars pic from sol 3200 by curiosity rover', timeout=10000)
    assert len(rover_requests) == 3

    requested_sol = int(parse_qs(urlparse(rover_requests[0]).query)['sol'][0])
    assert 3000 <= requested_sol <= 5500

    page.get_by_role('button', name='Add to Post').click()
    expect(page.locator('#id_content')).to_have_value(
        'Mars pic from sol 3200 by curiosity rover'
    )
    expect(page.locator('#random_mars_image_url')).to_have_value(
        'https://images.example/rover.svg'
    )
