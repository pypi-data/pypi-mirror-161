"""
This module gives generic utilities for all classes in this package
"""

import os
import uuid

import allure

from bqpackage.general.constants import JSON_FILE
from bqpackage.selenium_base import selenium_actions
from bqpackage.selenium_base import selenium_config
import json


@allure.step
def get_folder_files(path):
    temp_list = next(os.walk(path))
    return temp_list


@allure.step
def save_json_object(path, json_string):
    try:
        if JSON_FILE not in path:
            path = path + ".json"

        json_string = str(json_string)
        json_file = open(path, "w")
        json_file.write(json_string)
        json_file.close()
    except Exception:
        print(path + " was failed")


@allure.step
def save_data_from_url(self, url, path):
    selenium_config.get_url(self, url)
    body = selenium_actions.get_body(self)
    json_string = json.dumps(json.loads(body))
    json_file = open(path, "w")
    json_file.write(json_string)
    json_file.close()
    return body


@allure.step
def save_page_source(self, url, path):
    try:
        selenium_config.get_url(self, url)
        body = selenium_actions.get_page_source(self)
        out = open(path, 'w')
        out.write(body)
        out.close()
    except Exception:
        return


@allure.step
def get_json_file_object(path):
    try:
        file_object = open(path, "r")
        json_content = file_object.read()
        temp_list = json.loads(json_content)
        return temp_list
    except Exception:
        print("JSONDecodeError")
        return


@allure.step
def get_value_by_index(json_object, key, location):
    try:
        return json_object[location][key]
    except TypeError:
        print("json object not found")
        return


@allure.step
def get_value_by_key(json_object, key):
    try:
        return json_object[key]
    except TypeError:
        print("json object not found")
        return


@allure.step
def generate_uuid():
    return str(uuid.uuid4())


# with default value
@allure.step
def split_text(txt, separate=":"):
    try:
        text_split = txt.split(separate)
        return text_split
    except Exception:
        return


@allure.step
def create_folder(path):
    try:
        os.mkdir(path)

    except OSError:
        print("Creation of the directory %s failed" % path)
    else:
        print("Successfully created the directory %s " % path)


@allure.step
def str_to_bytes(s):
    if s is None:
        return None

    return s.encode('utf-8')


@allure.step
def bytes_to_str(s):
    if s is None:
        return None

    return s.decode('utf-8')
