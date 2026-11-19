import requests
from .constants import *
from faker import Faker
import os
import re
import json
# import easyocr


fake = Faker()


def _admin_api_session():
    username = os.getenv('TEST_ADMIN_USERNAME') or os.getenv('TEST_USER_USERNAME')
    password = os.getenv('TEST_ADMIN_PASSWORD') or os.getenv('TEST_USER_PASSWORD')
    if not username or not password:
        raise RuntimeError('Set TEST_ADMIN_USERNAME and TEST_ADMIN_PASSWORD for API test setup.')

    session = requests.Session()
    login_url = BASE_URL + 'login/'
    response = session.get(login_url)
    response.raise_for_status()
    csrf_token = session.cookies.get('csrftoken')
    if not csrf_token:
        raise RuntimeError('Could not obtain a CSRF token while logging in the test admin.')

    response = session.post(
        login_url,
        data={
            'username': username,
            'password': password,
            'csrfmiddlewaretoken': csrf_token,
        },
        headers={'Referer': login_url},
    )
    response.raise_for_status()
    if response.url.rstrip('/').endswith('/login'):
        raise RuntimeError('Test admin login failed; check the configured admin credentials.')
    return session


def _csrf_headers(session):
    token = session.cookies.get('csrftoken')
    if not token:
        raise RuntimeError('Could not obtain a CSRF token for the authenticated API request.')
    return {'Referer': BASE_URL, 'X-CSRFToken': token}


def api_create_post(image=False, many=False):
    """Create a test post with optional image and return its ID"""
    session = _admin_api_session()
    data = {"content": fake.text()}

    if image:
        # Open the image file and prepare it for upload
        with open(TEST_FILES["jpg"], "rb") as f:
            files = {"image": (os.path.basename(TEST_FILES["jpg"]), f, "image/jpeg")}
            resp = session.post(
                API_POST_CREATE_URL,
                data=data,
                files=files,
                headers=_csrf_headers(session),
            )
    else:
        resp = session.post(
            API_POST_CREATE_URL,
            data=data,
            headers=_csrf_headers(session),
        )
    session.close()

    if resp.status_code != 201:
        raise RuntimeError(
            f"Failed to create test post ({resp.status_code}); "
            "verify TEST_ADMIN_USERNAME belongs to a staff user. "
            f"Response: {resp.text}"
        )

    return resp.json()["id"]


def api_delete_posts():
    session = _admin_api_session()
    resp = session.delete(
        API_POST_DELETE_URL,
        headers=_csrf_headers(session),
    )
    session.close()
    if resp.status_code != 204:
        raise RuntimeError(
            f"Failed to delete test posts ({resp.status_code}): {resp.text}"
        )


def check_timestamp(text):
    # Accept both full month names (January) and 3-letter abbreviations (Jan.)
    # Match is case-insensitive to support 'Jan.' or 'jan.' etc.
    timestamp_regex = r"on [A-Za-z]{3,9}\.? \d{1,2}, \d{4}, \d{1,2}:\d{2} [ap]\.m\."
    assert re.search(timestamp_regex, text, re.IGNORECASE)


def get_weather_from_fixture(index):
    with open(WEATHER_FIXTURE_PATH, "r") as file:
        data = json.load(file)
        if isinstance(index, int):
            return data[index]
        if isinstance(index, list):
            return [data[i] for i in index]


def get_latest_weather_from_fixture():
    with open(WEATHER_FIXTURE_PATH, "r") as file:
        data = json.load(file)
        latest = data[0]
        for entry in data:
            if int(entry["fields"]["sol"]) > int(latest["fields"]["sol"]):
                latest = entry
    return latest


def get_weather_fixture_len():
    fixture_paths = [WEATHER_FIXTURE_PATH]
    fixture_paths.extend(WEATHER_FIXTURE_PATH.parent.glob("weather_sol_*.json"))
    return sum(
        len(json.loads(path.read_text(encoding="utf-8")))
        for path in fixture_paths
    )


def compare_texts(text1, text2):
    return True if text1.lower() == text2.lower() else False


"""A helper which uses easyocr to recognize the text in an image. 
"""

# _reader = None


# def assert_text_in_image(target_text: str, img_path: str):
#     # Heavy operation: initialize easyocr reader once and reuse to speed up tests
#     global _reader
#     if _reader is None:
#         _reader = easyocr.Reader(["en"])

#     # Returns True if any of the text snippets found in an image matches the target string
#     result_list = []
#     info = _reader.readtext(str(img_path))
#     for element in info:
#         text_to_check = element[1]
#         result_list.append(compare_texts(target_text, text_to_check))
#     assert any(result_list), f"'{target_text}' not found in image {img_path}"
