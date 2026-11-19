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
def test_regular_user_sees_comment_action_but_not_post_action(client):
    author = User.objects.create_user(username='feed-author')
    Post.objects.create(author=author, content='A post in the feed')
    regular_user = User.objects.create_user(username='regular-user')
    client.force_login(regular_user)

    response = client.get(reverse('core:community_posts'))

    assert response.status_code == 200
    assert b'data-testid="admin-only-posts"' in response.content
    assert b'data-testid="add-post"' not in response.content
    assert reverse('core:add_comment', args=[Post.objects.first().pk]).encode() in response.content


@pytest.mark.django_db
def test_only_staff_users_can_open_or_submit_post_form(client):
    anonymous_response = client.get(reverse('core:add_post'))
    assert anonymous_response.status_code == 302

    regular_user = User.objects.create_user(username='regular-user')
    client.force_login(regular_user)

    assert client.get(reverse('core:add_post')).status_code == 403
    response = client.post(
        reverse('core:add_post'),
        {
            'content': 'A forbidden post',
            'font_color': '#000000',
            'background_color': '#ffffff',
        },
    )
    assert response.status_code == 403
    assert Post.objects.count() == 0

    admin = User.objects.create_user(username='site-admin', is_staff=True)
    client.force_login(admin)
    assert client.get(reverse('core:add_post')).status_code == 200

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
    assert Post.objects.get().author == admin


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


@pytest.mark.django_db
def test_post_api_requires_staff_and_sets_author_from_session(client):
    author = User.objects.create_user(username='payload-author')
    regular_user = User.objects.create_user(username='regular-user')
    endpoint = reverse('core:post_list_create')
    payload = {'author': author.pk, 'content': 'API post'}

    assert client.post(endpoint, payload).status_code == 403

    client.force_login(regular_user)
    assert client.post(endpoint, payload).status_code == 403
    assert Post.objects.count() == 0

    admin = User.objects.create_user(username='site-admin', is_staff=True)
    client.force_login(admin)
    response = client.post(endpoint, payload)

    assert response.status_code == 201
    assert Post.objects.get().author == admin


@pytest.mark.django_db
def test_comment_api_requires_authentication_and_sets_author_from_session(client):
    post_author = User.objects.create_user(username='post-author')
    post = Post.objects.create(author=post_author, content='A post to comment on')
    spoofed_author = User.objects.create_user(username='payload-author')
    regular_user = User.objects.create_user(username='regular-user')
    endpoint = reverse('core:comment_list_create')
    payload = {
        'post': post.pk,
        'author': spoofed_author.pk,
        'content': 'API comment',
    }

    assert client.post(endpoint, payload).status_code == 403

    client.force_login(regular_user)
    response = client.post(endpoint, payload)

    assert response.status_code == 201
    comment = post.comments.get()
    assert comment.author == regular_user


@pytest.mark.django_db
def test_comment_api_list_remains_public(client):
    author = User.objects.create_user(username='post-author')
    post = Post.objects.create(author=author, content='Public post')

    response = client.get(reverse('core:comment_list_create'), {'post_id': post.pk})

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.django_db
def test_delete_api_endpoints_require_staff(client):
    author = User.objects.create_user(username='post-author')
    post = Post.objects.create(author=author, content='Protected post')
    regular_user = User.objects.create_user(username='regular-user')

    client.force_login(regular_user)
    post_response = client.delete(reverse('core:post_delete'))
    assert post_response.status_code == 403
    assert Post.objects.filter(pk=post.pk).exists()

    admin = User.objects.create_user(username='site-admin', is_staff=True)
    client.force_login(admin)
    post_response = client.delete(reverse('core:post_delete'))
    assert post_response.status_code == 204
    assert not Post.objects.filter(pk=post.pk).exists()
