#!/usr/bin/python
# vim: set fileencoding=utf-8 :

"""
test_element_equality.py
------------

Test the equals logic in the Element class
"""

from __future__ import absolute_import

from html import Element

import pytest
from selenium.webdriver.remote import webelement


class MockBrowser(object):

    """
    Mock a Browser object.
    """

    def __init__(self):
        self.timeout = 60
        self.poll_frequency = 0.5


class MockWebElement(webelement.WebElement):

    """
    Mock a WebElement object.
    """

    def get_attribute(self, name):
        """
        Override the get_attribute method for testing.
        """
        return True


class TestBaseHtmlElementEquality(object):

    """
    Test the equality logic in the Element class.
    """

    @pytest.mark.parametrize(
        ('element1', 'element2', 'expected'),
        [
            (Element._init_with_webelement(
                MockBrowser(), MockWebElement(None, '123456')),
             MockWebElement(None, '123456'),
             True),

            (MockWebElement(None, '123456'),
             Element._init_with_webelement(
                MockBrowser(), MockWebElement(None, '123456')),
             True),

            (Element._init_with_webelement(
                MockBrowser(), MockWebElement(None, '123456')),
             MockWebElement(None, '654321'),
             False),

            (MockWebElement(None, '654321'),
             Element._init_with_webelement(
                MockBrowser(), MockWebElement(None, '123456')),
             False),

            (Element._init_with_webelement(
                MockBrowser(), MockWebElement(None, '123456')),
             Element._init_with_webelement(
                MockBrowser(), MockWebElement(None, '123456')),
             True),

            # not really needed since we don't control webelements
            # but just added it for completeness
            (MockWebElement(None, '123456'),
             MockWebElement(None, '123456'),
             True),

            (Element._init_with_webelement(
                MockBrowser(), MockWebElement(None, '654321')),
             Element._init_with_webelement(
                MockBrowser(), MockWebElement(None, '123456')),
             False),

            # not really needed since we don't control webelements
            # but just added it for completeness
            (MockWebElement(None, '123456'),
             MockWebElement(None, '654321'),
             False),

            (Element._init_with_webelement(
                MockBrowser(), MockWebElement(None, '654321')),
             None,
             False),

            # not really needed since we don't control webelements
            # but just added it for completeness
            (MockWebElement(None, '123456'),
             None,
             False),

            (None,
             Element._init_with_webelement(
                 MockBrowser(), MockWebElement(None, '123456')),
             False),

            # not really needed since we don't control webelements
            # but just added it for completeness
            (None,
             MockWebElement(None, '654321'),
             False),
        ]
    )
    def test_equal(self, element1, element2, expected):
        """
        Test '==' between webelement and basehtmlelement
        """
        assert (element1 == element2) == expected, (
            "Expected the element1 and element2 to be {}equal.".format(
                '' if expected else 'not '))
