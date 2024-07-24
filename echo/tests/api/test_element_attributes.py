#!/usr/bin/python
# vim: set fileencoding=utf-8 :

"""
test_element_attributes.py
------------

Test the attribute generation in the Element class
"""

from __future__ import absolute_import

from html import Element

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.remote import webelement

ATTRS_PARAMS = [
    ('foobar', 'attr_foobar'),
    ('foo-bar', 'attr_foo_bar'),
    ('foo_bar', 'attr_foo_bar'),
    ('  foo bar  ', 'attr_foo_bar'),
    ('NewHTTPFile', 'attr_new_http_file'),
    ('New-HTTP*File', 'attr_new_http__file'),
    ('New-HTTPFile', 'attr_new_http_file'),
    ('New*HTTPFile', 'attr_new_http_file'),
    ('newFile', 'attr_new_file'),
    ('NewHTTP', 'attr_new_http'),
]


class MockWebelement(webelement.WebElement):

    """
    Mock a WebElement object.
    """

    ATTRIBUTE_VALUE = u'MockWebelement get_attribute method'

    def __init__(self):
        """
        Init: we extend from webelement.WebElement just to
        get the type but we pass in nothing of importance
        to the object class.
        """
        super(MockWebelement, self).__init__(None, '1234')

    def get_attribute(self, attribute):
        """
        Override the get_attribute method to return the
        same value for testing.
        """
        return self.ATTRIBUTE_VALUE

    def wait_for_condition(self, *args, **kwargs):
        """
        Override the wait_for_condition method since we
        are not really waiting for things to show up.
        """
        return None

    def find_element(self, *args, **kwargs):
        """
        Override find_element to return a mock element
        """
        return MockWebelement()

    # override properties
    _webelement = property(find_element)
    element = property(find_element)


class MockBrowser():  # webdriver_wrapper.WebdriverWrapper):

    """
    Mock a Browser object.
    """

    def __init__(self):
        """
        Init: barebone requirement.
        """

        self.timeout = 60
        self.poll_frequency = 0.5

    def wait_for_condition(self, *args, **kwargs):
        """
        Override the wait_for_condition method since we
        are not really waiting for things to show up.
        """
        return None

    def find_element(self, *args, **kwargs):
        """
        Override find_element to return a mock element
        """
        return MockWebelement()

    # override properties
    _webelement = property(find_element)
    element = property(find_element)


class SubBaseHtmlElement(Element):

    """
    An example shell that extends from Element
    class that helps tests sub classes.
    """

    ATTRIBUTE_VALUE = u'SubBaseHtmlElement get_attribute method'

    def __init__(
            self, browser=MockBrowser(), by=By.TAG_NAME, value="body",
            parent_instance=None, attributes=(), sub_elements=()):
        """
        Init: sets basic defaults for everything except
        for attributes.
        """

        super(SubBaseHtmlElement, self).__init__(
            browser, by, value, parent_instance,
            attributes, sub_elements)
        self._check_display = False

    def get_attribute(self, attribute):
        """
        Override the get_attribute method to return the
        same value for testing.
        """
        return self.ATTRIBUTE_VALUE

    def wait_for_condition(self, *args, **kwargs):
        """
        Override the wait_for_condition method since we
        are not really waiting for things to show up.
        """
        return None

    def find_element(self, *args, **kwargs):
        """
        Override find_element to return a mock element
        """
        return MockWebelement()

    # override properties
    _webelement = property(find_element)
    element = property(find_element)


ELEMENT_CLASS_WITH_ATTRS = [
    [eclass] + list(param)
    for eclass in (Element, SubBaseHtmlElement)
    for param in ATTRS_PARAMS
]

DIFF_ELEMENT_CLASS_PARAMs = [


    [eclass] + list(param)
    for eclass in (Element, SubBaseHtmlElement)
    for param in [('something', 'attr_something')]
]


class TestBaseHtmlElementAttributes(object):

    """
    Test the attribute generation in the
    Element class.
    """

    def setup_method(self, method):
        """
        Setup method
        """
        self.attr_list = []
        self.cls_list = []

    def teardown_method(self, method):
        """
        Teardown method
        """
        for item in self.attr_list:
            for mcls in self.cls_list:
                if hasattr(mcls, item):
                    delattr(mcls, item)

    @pytest.mark.parametrize(
        'element_class,attr,gen_attr', ELEMENT_CLASS_WITH_ATTRS,
        ids=["{}-{}".format(ecls.__name__, attr)
             for ecls, attr, _ in ELEMENT_CLASS_WITH_ATTRS]
    )
    def test_name_generation(self, element_class, attr, gen_attr):
        """
        Test that the attributes are converted to attr_* properties
        """
        self.cls_list.append(element_class)
        self.attr_list.append(gen_attr)

        base_elem = element_class(
            MockBrowser(), By.TAG_NAME, 'body', attributes=[attr])

        assert hasattr(base_elem.__class__, gen_attr), (
            "Did the attr generation create the right attribute? "
            "Make sure that it's an instance attribute instead of "
            "a class level attribute."
            "Is {} in {}.".format(attr, base_elem.__class__.__dict__))

    @pytest.mark.parametrize(
        'element_class,attr,gen_attr', ELEMENT_CLASS_WITH_ATTRS,
        ids=["{}-{}".format(ecls.__name__, attr)
             for ecls, attr, _ in ELEMENT_CLASS_WITH_ATTRS]
    )
    def test_instance_attributes(self, element_class, attr, gen_attr):
        """
        Test that the attributes are isolated from other
        objects attributes.
            i.e.: attributes generated are not class level attributes.
        """
        self.cls_list.append(element_class)
        self.cls_list.append(Element)
        self.attr_list.append(gen_attr)

        elem_with_new_attr = element_class(
            MockBrowser(), By.TAG_NAME, 'body', attributes=[attr])

        elem_with_no_attr = Element(
            MockBrowser(), By.TAG_NAME, 'body')

        assert hasattr(elem_with_new_attr.__class__, gen_attr), (
            "Seems that the expected {} attribute was not generated. "
            "__dict__ shows: {}".format(gen_attr, elem_with_new_attr.__dict__))

        if elem_with_new_attr.__class__ != elem_with_no_attr.__class__:

            assert not hasattr(elem_with_no_attr.__class__, gen_attr), (
                "Seems that the attribute declared in one element appeared "
                "inside a different element.")

    @pytest.mark.parametrize(
        'element_class,attr,gen_attr,expected_string',
        [
            (Element, 'bhe_something',
             'attr_bhe_something', MockWebelement.ATTRIBUTE_VALUE),

            (SubBaseHtmlElement, 'sbhe_something',
             'attr_sbhe_something', SubBaseHtmlElement.ATTRIBUTE_VALUE),
        ],
        ids=['Element', 'SubBaseHtmlElement']
    )
    def test_attributes_calls(
            self, element_class, attr, gen_attr, expected_string):
        """
        Making sure that attr_* calls the right get_attribute method
        """
        self.cls_list.append(element_class)
        self.attr_list.append(gen_attr)

        elem = element_class(
            MockBrowser(), By.TAG_NAME, 'body', attributes=[attr])

        assert getattr(elem, gen_attr) == expected_string, (
            "Did we call the right get_attribute method?")
