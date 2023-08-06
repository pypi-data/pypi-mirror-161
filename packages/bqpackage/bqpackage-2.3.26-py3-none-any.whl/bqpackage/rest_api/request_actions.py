"""
This module gives the option to create HTTP requests for GET, POST, PUT, DELETE, and PATCH methods
"""
import allure

from bqpackage.rest_api import utilities
import requests as req
import json

DEFAULT_HEADERS = {'content-type': 'application/json', "accept": "*/*"}
DEFAULT_PARAMS = ['?']


@allure.step
def get_request(url, params=None, headers=None):
    """
    send get request, and return the response
    """
    utilities.url_validator(url)

    if not headers:
        headers = DEFAULT_HEADERS

    try:
        if params is None:
            response = req.get(url, headers=headers)
        else:
            response = req.get(url, headers=headers, params=params)

    except Exception as ex:
        get_exception(url, ex)
    return response


@allure.step
def put_request(url, body, params=None, headers=None):
    """
    send put request, and return the response
    """
    utilities.url_validator(url)
    if not headers:
        headers = DEFAULT_HEADERS

    try:

        if params is None:
            response = req.put(url=url, data=json.dumps(body), headers=headers)
        else:
            response = req.put(url=url, data=json.dumps(body), headers=headers, params=params)

    except Exception as ex:
        get_exception(url, ex)
        return response


@allure.step
def post_request(url, body, params=None, headers=None):
    """
    send post request, and return the response
    """
    utilities.url_validator(url)
    if not headers:
        headers = DEFAULT_HEADERS

    try:
        if params is None:
            response = req.post(url=url, data=json.dumps(body), headers=headers)
        else:
            response = req.post(url=url, data=json.dumps(body), headers=headers, params=params)

    except Exception as ex:
        get_exception(url, ex)
        return response


@allure.step
def patch_request(url, body, params=None, headers=None):
    """
    send patch request, and return the response
    """
    utilities.url_validator(url)
    if not headers:
        headers = DEFAULT_HEADERS

    try:

        if params is None:
            response = req.patch(url=url, data=json.dumps(body), headers=headers)
        else:
            response = req.patch(url=url, data=json.dumps(body), headers=headers, params=params)

    except Exception as ex:
        get_exception(url, ex)
        return response


@allure.step
def delete_request(url, body, params=None, headers=None):
    """
    send delete request, and return the response
    """
    utilities.url_validator(url)
    if not headers:
        headers = DEFAULT_HEADERS

    try:
        if params is None:
            response = req.delete(url=url, data=json.dumps(body), headers=headers)
        else:
            response = req.delete(url=url, data=json.dumps(body), headers=headers, params=params)

    except Exception as ex:
        get_exception(url, ex)

        return response


@allure.step
def get_exception(url, ex):
    print(str(req.exceptions.RequestException(
        "failed on getting response from " + url + "\n error message description: %s" % str(ex))))
