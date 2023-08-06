import requests

from bqpackage.selenium_base.selenium_config import SeleniumConfig


def test_selenium_instance():
    sc = SeleniumConfig(remote="http://sgrid-web.az.seebo.com/wd/hub")
    sc.tear_down()
    session_id = sc.driver.session_id
    try:
        requests.delete(f'https://sgrid-web.az.seebo.com/session/{session_id}')
    except:
        pass


# test_selenium_instance()
