import requests
from .constants import * 
from faker import Faker
from PIL import Image
import os

fake = Faker()

def get_test_user_id():
    resp = requests.get(url=API_GET_USERS_URL)
    return resp.json()[0]['id']

def api_create_post(image=False):
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
    requests.delete(url=API_POST_DELETE_URL)
