from playwright.sync_api import Page
from dotenv import load_dotenv

from pages.register_page import RegisterPage


load_dotenv()

def test_successful_register(register_page: RegisterPage):
    pass

def test_register_fail_if_password_too_short(register_page: RegisterPage):
    pass

def test_regster_fail_if_password_numeric(register_page: RegisterPage):
    pass

def test_register_fail_if_password_too_common(register_page: RegisterPage):
    pass

def test_register_fail_if_username_exists(register_page: RegisterPage):
    pass