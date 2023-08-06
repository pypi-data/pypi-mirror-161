import allure

from bqpackage.selenium_base.selenium_actions import SeleniumActions
from bqpackage.selenium_base.selenium_config import SeleniumConfig
from bqpackage.shared import run_parallel as parallel


# Test 1 - check the default parameters
@allure.feature('Fixtures')
def test_1():
    selenium = SeleniumConfig()
    selenium.init_driver()
    selenium.tear_down()


# # Test 2 - check the headless option
@allure.feature('Fixtures')
def test_2():
    selenium = SeleniumConfig()
    selenium.init_driver(headless=True)
    selenium.tear_down()


# # test 3 - check the url option
@allure.feature('Fixtures')
def test_3():
    selenium = SeleniumConfig()
    selenium.init_driver()
    selenium.get_url('"https://www.google.com/"')
    selenium.tear_down()


# test 4 check the proxy server
@allure.feature('Fixtures')
def test_4():
    selenium = SeleniumConfig()
    selenium.init_driver(proxy=True)
    selenium.get_url('"https://www.google.com/"')
    selenium.tear_down()


# test 5 - check the parallel function
@allure.feature('Fixtures')
def test_5():
    # TODO
    pass