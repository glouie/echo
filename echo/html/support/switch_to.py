#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# pylint: disable=protected-access
# pylint: disable=no-member

"""
SwitchTo class
===========
* SwitchTo class to provide the switch_to APIs.
"""


from __future__ import absolute_import
from selenium.webdriver.remote import switch_to
from html import Element


class SwitchTo(switch_to.SwitchTo):

    """
    Helper class to provide the switch_to APIs
    """

    def __init__(self, browser):
        """
        Init

        :type browser: WebDriverWrapper
        :param browser: the specified web driver

        """
        switch_to.SwitchTo.__init__(self, browser.driver)
        self._browser = browser

    @property
    def active_element(self):
        """
        Returns the element with focus, or BODY if nothing has focus.

        :rtype: Element
        :return the element with focus, or BODY if nothing has focus
        """
        return Element._init_with_webelement(
            self._browser, switch_to.SwitchTo.active_element.fget(self))
