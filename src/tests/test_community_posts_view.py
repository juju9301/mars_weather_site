import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from core.models import Post


@pytest.mark.django_db
def test_posts_are_not_rendered_on_homepage(client):
    author = User.objects.create_user(username='feed-author')
    Post.objects.create(author=author, content='Feed-only post')

    response = client.get(reverse('core:index'))

    assert response.status_code == 200
    assert b'Feed-only post' not in response.content


@pytest.mark.django_db
def test_community_posts_view_renders_paginated_posts(client):
    author = User.objects.create_user(username='feed-author')
    contents = [f'Community post {number}' for number in range(6)]
    for content in contents:
        Post.objects.create(author=author, content=content)

    first_page = client.get(reverse('core:community_posts'))
    second_page = client.get(reverse('core:community_posts'), {'page': 2})

    assert first_page.status_code == 200
    assert len(first_page.context['posts']) == 5
    assert second_page.status_code == 200
    assert len(second_page.context['posts']) == 1
    rendered_posts = first_page.content + second_page.content
    for content in contents:
        assert content.encode() in rendered_posts


@pytest.mark.django_db
def test_post_creation_redirects_to_community_feed(client):
    author = User.objects.create_user(username='post-author')
    client.force_login(author)

    response = client.post(
        reverse('core:add_post'),
        {
            'content': 'A new community post',
            'font_color': '#000000',
            'background_color': '#ffffff',
        },
    )

    assert response.status_code == 302
    assert response['Location'] == reverse('core:community_posts')


@pytest.mark.django_db
def test_comment_creation_redirects_to_community_feed(client):
    author = User.objects.create_user(username='comment-author')
    post = Post.objects.create(author=author, content='A post to comment on')
    client.force_login(author)

    response = client.post(
        reverse('core:add_comment', args=[post.pk]),
        {'content': 'A community comment'},
    )

    assert response.status_code == 302
    assert response['Location'] == reverse('core:community_posts')
