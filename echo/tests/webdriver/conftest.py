#!/usr/bin/python
# vim: set fileencoding=utf-8 :

from __future__ import absolute_import
from html.webdriver_wrapper import WebdriverWrapper
from pytest_base_uitest.util import browsermanager
import pytest
import logging


LOGGER = logging.getLogger(__name__)


@pytest.fixture()
def browser(request):
    """
    Wraps Selenium with the WebdriverWrapper and any project settings

    :type request: SubRequest
    :param request:

    :type driver: WebDriver
    :param driver: A Selenium WebDriver object
    :return: WebDriverWrapper object
    """
    LOGGER.info("Start browser...")

    if len(browsermanager.DRIVER_INSTANCES) == 0:
        browsermanager.destroy_all_browsers()

    driver = browsermanager.init_browser()
    wrapped_webdriver = WebdriverWrapper(driver)

    def fin():
        LOGGER.info("End of browser...")

        browsermanager.destroy_all_browsers()

    request.addfinalizer(fin)
    return wrapped_webdriver
