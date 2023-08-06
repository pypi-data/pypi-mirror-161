import allure

from bqpackage.rest_api import request_actions


@allure.feature('Fixtures')
def test_1():
    response = request_actions.get_request("https://github.com/")
    print(response)
