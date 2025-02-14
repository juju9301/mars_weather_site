from pathlib import Path

BASE_URL = 'http://localhost:8000/'
TEST_FILES = {'jpg': Path('media/test_images/test_image1.jpg'), 
              'png': Path('media/test_images/test_image2.png')}
WEATHER_FIXTURE_PATH = Path(r'weather/fixtures/weather_fixture.json')
API_GET_USERS_URL = BASE_URL + 'api/users'
API_POST_CREATE_URL = BASE_URL + 'api/posts/'
API_POST_DELETE_URL = BASE_URL + 'api/posts/delete'