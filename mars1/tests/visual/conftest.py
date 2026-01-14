# Configuration for visual tests
import os
import pytest
from playwright.sync_api import Page
from dotenv import load_dotenv
from applitools.playwright import Eyes, VisualGridRunner, Target, BatchInfo, \
    Configuration, BrowserType, DeviceName, ScreenOrientation, ChromeEmulationInfo, \
        IosDeviceInfo, IosDeviceName, RectangleSize

def pytest_addoption(parser):
    parser.addoption('--visual', action='store_true', default=False, help='run visual tests')

def pytest_collection_modifyitems(config, items):
    run_visual = config.getoption('--visual') and bool(os.getenv('APPLITOOLS_API_KEY'))
    
    if not run_visual:
        skip = pytest.mark.skip(reason='visual tests are disabled; set the APPLITOOLS_API_KEY env var and use --visual')
        for item in items:
            if 'visual' in item.keywords:
                item.add_marker(skip)

USE_ULTRAFAST_GRID = os.getenv('USE_ULTRAFAST_GRID')


@pytest.fixture(scope='session')
def batch_info():
    runner_name = 'Ultrafast Grid' if USE_ULTRAFAST_GRID else 'Classic runner'
    return BatchInfo(f'Example: playwright python with {runner_name}')

@pytest.fixture(scope='session')
def configuration(batch_info: BatchInfo):
    config = Configuration()
    config.set_batch(batch_info)
    config.set_api_key(os.getenv('APPLITOOLS_API_KEY'))

    if USE_ULTRAFAST_GRID:
        config.add_browser(800, 600, BrowserType.CHROME)
        config.add_browser(1920, 1080, BrowserType.FIREFOX)
        config.add_browser(1024, 768, BrowserType.SAFARI)

        config.add_browsers(
            [
                IosDeviceInfo(IosDeviceName.iPhone_11, ScreenOrientation.PORTRAIT),
                ChromeEmulationInfo(DeviceName.Nexus_10, ScreenOrientation.LANDSCAPE)
            ]
        )

    return config

@pytest.fixture(scope='function')
def eyes(
    runner,
    configuration: Configuration,
    page: Page,
    request: pytest.FixtureRequest):
    
    eyes = Eyes(runner)
    eyes.set_configuration(configuration)

    eyes.open(
        driver=page,
        app_name='Mars weather app',
        test_name=request.node.name,
        viewport_size=RectangleSize(1200, 600))
    
    yield eyes
    eyes.close_async()



