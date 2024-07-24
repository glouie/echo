#!/usr/bin/python
# vim: set fileencoding=utf-8 :


"""
BasePage module
"""

from __future__ import absolute_import
import logging
from html import wrapper

LOGGER = logging.getLogger(__name__)
TIMEOUT = 30  # 30 seconds


class BasePage(object):

    """
    BasePage model

    Extension of this object is where it should tie all the
    components together.
    """

    def __init__(self, browser, url):
        """
        BasePage init

        :type browser: selenium.webdriver.remote.webelement.WebDriver
        :param browser: WebDriver object like instance

        :type url: string
        :param url: the base url for this page

        """

        if isinstance(browser, wrapper.Wrapper):
            self.browser = browser
        else:
            self.browser = wrapper.Wrapper(browser)

        self.url = url
        self.timeout = TIMEOUT  # simple handle to be used later if needed.

    def open(self, param_string=None):
        """
        Open method to open the page.

        Uses the Wrapper.open() method, and not the WebDriver.get()

        :type param_string: string
        :param param_string: the param string to attach to the end of the url

        :rtype: string
        :return: the url that was requested to open.
        """

        if param_string is None:
            url = self.url
        else:
            if "?" in self.url:
                url = "{url}&{param}".format(
                    url=self.url, param=param_string)
            else:
                url = "{url}?{param}".format(
                    url=self.url, param=param_string)

        self.browser.open(url)
        return url

    def simulate_print_start(self):
        '''
        Simulates the user initiating a browser print operation.
        We can't actually run the print handler code because it opens the
        browser's native print dialog.
        '''

        script = '''
            var body_el = document.getElementsByTagName('body')[0];
            body_el.classList.add('print');
            body_el.style['width'] = "800px";

            var print_start_evt = new Event("PrintStart");
            document.dispatchEvent(print_start_evt);
        '''

        self.browser.execute_script(script)

    def simulate_print_end(self):
        '''
        Simulates the user cancelling the browser print operation.
        '''

        script = '''
            var body_el = document.getElementsByTagName('body')[0];
            body_el.classList.remove('print');
            body_el.style['width'] = "";

            var print_start_evt = new Event("PrintEnd");
            document.dispatchEvent(print_start_evt);
        '''

        self.browser.execute_script(script)
