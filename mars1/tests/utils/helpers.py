import requests
from .constants import * 
from faker import Faker
import os
import re
import json
import easyocr


fake = Faker()

def get_test_user_id():
    resp = requests.get(url=API_GET_USERS_URL)
    return resp.json()[0]['id']

def api_create_post(image=False, many=False):
    """Create a test post with optional image and return its ID"""
    data = {
        'author': get_test_user_id(),
        'content': fake.text()
    }

    if image:
        # Open the image file and prepare it for upload
        with open(TEST_FILES['jpg'], 'rb') as f:
            files = {'image': (os.path.basename(TEST_FILES['jpg']), f, 'image/jpeg')}
            resp = requests.post(url=API_POST_CREATE_URL, data=data, files=files)
    else:
        resp = requests.post(url=API_POST_CREATE_URL, data=data)

    if resp.status_code != 201:
        raise Exception(f"Failed to create post: {resp.text}")
        
    return resp.json()["id"]

def api_delete_posts():
    resp = requests.delete(url=API_POST_DELETE_URL)
    assert resp.status_code == 204

def check_timestamp(text):
        # Accept both full month names (January) and 3-letter abbreviations (Jan.)
        # Match is case-insensitive to support 'Jan.' or 'jan.' etc.
        timestamp_regex = r'on [A-Za-z]{3,9}\.? \d{1,2}, \d{4}, \d{1,2}:\d{2} [ap]\.m\.'
        assert re.search(timestamp_regex, text, re.IGNORECASE)

def get_weather_from_fixture(index):
     with open(WEATHER_FIXTURE_PATH, 'r') as file:  
        data = json.load(file)
        if isinstance(index, int):
            return data[index]
        if isinstance(index, list):
            return [data[i] for i in index]
     
def get_latest_weather_from_fixture():
    with open(WEATHER_FIXTURE_PATH, 'r') as file:
        data = json.load(file)
        latest = data[0]
        for entry in data:
            if int(entry['fields']['sol']) > int(latest['fields']['sol']):
                latest = entry
    return latest

def get_weather_fixture_len():
    with open(WEATHER_FIXTURE_PATH, 'r') as file:
        data = json.load(file)
        return len(data)
    
def compare_texts(text1, text2):
    return True if text1.lower() == text2.lower() else False

def assert_text_in_image(target_text: str, img_path: str):   
    # Returns True if any of the text snippets found in an image matches the target string 
    result_list = []
    reader = easyocr.Reader(['en'])
    info = reader.readtext(str(img_path))
    for element in info:
        text_to_check = element[1]
        result_list.append(compare_texts(target_text, text_to_check))
    assert any(result_list)
