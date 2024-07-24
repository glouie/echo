#!/usr/bin/python
# vim: set fileencoding=utf-8 :

"""
Meta
====
    $Id$  # nopep8
    $DateTime$
    $Author$
    $Change$
"""

from __future__ import absolute_import
import logging
from html.webdriver_wrapper import WebdriverWrapper
from pytest_splunk_config import get_pytest_config

logger = logging.getLogger(__name__)

global DRIVER_INSTANCES
DRIVER_INSTANCES = []


def init_browser():
    """
    Initialize browser

    :return: browser instance
    """
    logger.debug("Setting up browser instance with html's WebDriverWrapper.")
    try:
        pytest_config = get_pytest_config()
        webdriver = pytest_config.get_browser(pytest_config)
        logger.debug("We got back: {s}".format(s=webdriver))
        browser = WebdriverWrapper(webdriver)
        logger.info("Browser session ID: '{id}'"
                    "".format(id=browser.session_id))

        pytest_config.webdriver = browser

        global DRIVER_INSTANCES
        DRIVER_INSTANCES.append(browser)
    except Exception as err:
        logger.error("Error occurred setting WebDriverWrapper."
                     "{e}".format(e=err))
        raise

    return browser


def destroy_all_browsers():
    """
    Destroy all browser instances

    :return: void
    """
    global DRIVER_INSTANCES
    try:
        logger.info(
            "There are {i} instances of webdriver, "
            "tearing them down.".format(i=len(DRIVER_INSTANCES)))
        for driver in DRIVER_INSTANCES:
            if driver is not None:
                try:
                    logger.info("Quitting browser...")
                    driver.quit()
                except Exception as err:
                    logger.error(
                        "Error happened while quitting browser: {err}".format(
                            err=err))
    finally:
        get_pytest_config().webdriver = None
        DRIVER_INSTANCES = []
