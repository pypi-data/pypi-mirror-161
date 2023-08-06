"""
This module wrapping basic selenium actions
"""
import re

import allure
from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Chrome


@allure.step
class SeleniumActions:

    @allure.step('Selenium actions initialization')
    def __init__(self, driver, max_tries=2, max_pages=50):
        self._list_of_elements = []
        self._web_element_type = "webelement"
        self._temp_element = None
        self._wait_seconds = 0
        self.driver: Chrome = driver
        self.global_timeout = 60
        self.max_tries = max_tries
        self.max_pages = max_pages

    @allure.step
    def pagination(self, container: str, next_btn: str, disabled: str):
        """
        Loop pages until reaches the end

        :arg container : Container
        :arg next_btn : Next button element
        :arg disabled : next button disabled
        :returns True->successfully paginated, False->error
        """
        for i in self.pagination_iterator(container=container, next_btn=next_btn, disabled=disabled):
            pass
        return True

    @allure.step
    def pagination_iterator(self, container: str, next_btn: str, disabled: str):
        """
        Loop pages, yield every page for future consume

        :arg container : Container
        :arg next_btn : Next button element
        :arg disabled : next button disabled
        :returns page text->when there's text, False->error
        """
        i = 0
        container_text = self.get_text(element=container, strip=True)
        try:
            next_attrs = self.element_exist(element=f'{container}{next_btn}').get_attribute('class')
            while next_attrs and disabled not in next_attrs:
                yield container_text
                self.click(element=f'{container}{next_btn}')
                i += 1
                container_text = self.get_text(element=container, strip=True)
                next_attrs = self.element_exist(element=f'{container}{next_btn}').get_attribute('class')
                if not i < self.max_pages:
                    raise RuntimeError(f'looping pages reached maximum {i}/{self.max_pages}')
        except AttributeError:
            pass

        # exhausted
        yield container_text

    @allure.step
    def text_in_pagination(self, container: str, next_btn: str, disabled: str, text: str):
        """
        Loop pages until reaches the end/criteria met (text in page)

        :arg container : Container
        :arg next_btn : Next button element
        :arg disabled : next button disabled
        :arg text : Text to look for
        :returns Text->Text found on current page, False->error
        """
        text = re.sub(r"\s+", "", text)
        for container_text in self.pagination_iterator(container=container, next_btn=next_btn, disabled=disabled):
            if text in container_text:
                return text

        return False

    @allure.step
    def wait_for_text(self, location=None, text=None):
        """
        wait for a text to be presented inside/without element (currently searching by xpath!)
        driver max waiting time is 30 sec.
        :arg location : element to search inside
        :arg text : text to look for
        :returns True->Text found on current element/non element, False->error
        """
        if location:
            WebDriverWait(self.driver, self.global_timeout).until(
                EC.text_to_be_present_in_element((By.XPATH, location), text))
        else:
            WebDriverWait(self.driver, self.global_timeout).until(EC.text_to_be_present_in_element
                                                                  (locator=(By.XPATH, "//body"), text_=text))
        return True

    @allure.step
    def where_is_element(self, element: str):
        """
        ping you when element have been found (only XPATH)
        :param element: XPATH
        :return: True if element have been found, Raise timeout if time passed
        """
        WebDriverWait(self.driver, self.global_timeout).until(EC.presence_of_element_located((By.XPATH, element)))
        return True

    @allure.step
    def element_is_gone(self, element: str):
        """
        ping you when element is gone (only XPATH)
        :param element: XPATH
        :return: True if element have is gone, Raise timeout if time passed
        """
        WebDriverWait(self.driver, self.global_timeout).until(EC.invisibility_of_element_located((By.XPATH, element)))
        return True

    @allure.step
    def get_element(self, element: str):
        """
        find element
        :param element: XPATH
        :return: Single element
        """
        self.where_is_element(element=element)
        return self.driver.find_element(By.XPATH, value=element)

    @allure.step
    def element_exist(self, element: str):
        """
        check if element exist
        :param element: XPATH
        :return: True->Exist, Else->False
        """
        try:
            return self.driver.find_element(By.XPATH, value=element)
        except:
            return False

    @allure.step
    def get_elements(self, element: str):
        """
        Get all the elements
        :param element: XPATH
        :return: List of elements
        """
        self.where_is_element(element=element)
        return self.driver.find_elements(By.XPATH, element)

    @allure.step
    def click(self, element: str, proof=None, max_tries=None, maximum=None, reset=None):
        """
        click on element
        :arg element : element to be clicked (XPATH)
        :arg proof : optional function that returns True when some requirement satisfied, for ex. where_is_element
        :arg max_tries : optional arg, how many tries do you want before throwing exception ?
        :arg maximum : optional arg, maximum waiting time before throwing exception
        :arg reset : optional arg, something to do after each try
        :returns True->Clicked False->error
        """
        element_to = self.get_element(element)
        if proof:
            tries = max_tries if max_tries else self.max_tries
            self.repeat(command=lambda: element_to.click(), proof=proof, max_tries=tries, maximum=maximum,
                        reset=reset)
            return True
        else:
            element_to.click()
            return True

    @allure.step
    def repeat(self, command, proof, max_tries=None, maximum=None, reset=None):
        """
        loop trying to fulfil a command (function), until a requirement satisfied (proof)
        :arg command : what to do ?
        :arg proof : optional function that returns True when some requirement satisfied
        :arg max_tries : optional arg, how many tries do you want before throwing exception ?
        :arg maximum : optional arg, maximum waiting time before throwing exception
        :arg reset : optional arg, something to do after each try
        :returns True->Satisfied and proof exist False->error
        """
        if not max_tries or max_tries > self.max_tries:
            max_tries = self.max_tries

        temp_global = self.global_timeout
        if maximum:
            self.global_timeout = maximum

        tries = 0
        satisfied = False
        while not satisfied:
            try:
                command()
            except Exception as e:
                pass

            tries += 1

            if tries > max_tries:
                break
            sleep(1)

            try:
                satisfied = proof()
            except Exception as e:
                pass

            if not satisfied and reset:
                reset()

        self.global_timeout = temp_global
        if not satisfied:
            raise RuntimeError(f"requirement not satisfied !")

        allure.attach(str(tries), 'Tries', allure.attachment_type.TEXT)
        return True

    @allure.step
    def hover(self, element, proof=None, max_tries=None, maximum=None, reset=None):
        """
        hover element
        :arg element : element to be hovered (XPATH)
        :arg proof : optional function that returns True when some requirement satisfied, for ex. where_is_element
        :arg max_tries : optional arg, how many tries do you want before throwing exception ?
        :arg maximum : optional arg, maximum waiting time before throwing exception
        :arg reset : optional arg, something to do after each try
        :return:
        """
        element_to = self.get_element(element)
        if proof:
            tries = max_tries if max_tries else self.max_tries
            self.repeat(command=lambda: ActionChains(self.driver).move_to_element(element_to).perform(),
                        proof=proof, max_tries=tries, maximum=maximum, reset=reset)
            return True
        else:
            ActionChains(self.driver).move_to_element(element_to).perform()
            return True

    @allure.step
    def send_keys(self, element=None, text=None, proof=None, max_tries=None, maximum=None, reset=None):
        """
        send keys to element/screen
        :arg element : optional, element to be send keys to (XPATH)
        :arg text : text to send
        :arg proof : optional function that returns True when some requirement satisfied, for ex. where_is_element
        :arg max_tries : optional arg, how many tries do you want before throwing exception ?
        :arg maximum : optional arg, maximum waiting time before throwing exception
        :arg reset : optional arg, something to do after each try
        :return:
        """
        text = str(text)
        if not element:
            if proof:
                tries = max_tries if max_tries else self.max_tries
                self.repeat(command=lambda: ActionChains(self.driver).send_keys(text).perform(),
                            proof=proof, max_tries=tries, maximum=maximum, reset=reset)
                return True
            else:
                ActionChains(self.driver).send_keys(text).perform()
                return True
        else:
            element_to = self.get_element(element)
            if proof:
                self.repeat(command=lambda: element_to.send_keys(text).perform(),
                            proof=proof, max_tries=max_tries, maximum=maximum, reset=reset)
                return True
            else:
                element_to.send_keys(text)
                return True

    @allure.step
    def get_text(self, element, strip=False):
        """
        get text from page (WebDriverWait)
        :param element: XPATH
        :param strip: optional
        :return:
        """
        element = self.get_element(element)
        allure.attach(element.text, 'Text', allure.attachment_type.TEXT)
        if strip:
            return re.sub(r"\s+", "", element.text)
        return element.text

    @allure.step
    def get_page_source(self):
        source = self.driver.page_source
        allure.attach(source, 'Page source', allure.attachment_type.TEXT)
        return source
