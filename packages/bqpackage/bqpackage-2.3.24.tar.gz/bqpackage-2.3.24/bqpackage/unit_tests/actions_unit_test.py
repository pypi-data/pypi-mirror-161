import allure
from bqpackage.selenium_base.selenium_actions import SeleniumActions
from bqpackage.selenium_base.selenium_config import SeleniumConfig

# init selenium driver
why_seebo = "(//a[contains(text(),'Why Seebo')])[1]"
the_solution = "(//a[contains(text(),'The Solution')])[1]"
customers = "(//a[contains(text(),'Customers')])[1]"
get_a_demo = "//li[@id='menu-item-64909']/a/div/div/div/span"
name_field = "(//input)[1]"


# init driver and do test
@allure.feature('Fixtures')
def test():
    selenium = SeleniumConfig()

    DEFAULT_LINK = "https://www.seebo.com/"
    selenium.get_url(DEFAULT_LINK)

    selenium.actions.click(why_seebo)
    selenium.tear_down()

test()