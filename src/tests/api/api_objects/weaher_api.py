from playwright.sync_api import APIRequestContext, APIResponse
from ...utils.constants import BASE_URL, WEATHER_FIXTURE_PATH

class WeatherAPI:
    def __init__(self, api_context: APIRequestContext):
        self.api_context = api_context
        self.api_url = BASE_URL + 'api/get_weather_data'
        self.weather_fixture_path = WEATHER_FIXTURE_PATH

    def get_weather_data(self, data: dict = None) -> APIResponse:
        return self.api_context.get(self.api_url, data=data)
    
    
