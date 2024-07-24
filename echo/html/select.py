#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# pylint: disable=too-many-arguments
# pylint: disable=dangerous-default-value
# pylint: disable=locally-disabled

"""
Select module
"""

from __future__ import absolute_import
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotSelectableException
from selenium.common.exceptions import ElementNotVisibleException
from html import Element
from html import wait_for_display


class Select(Element):

    """
    This is a class to simulate HTML select object
    interactions

    Tag: select

    Requires a WebElement or WebElement like instance passed into it.
    """

    def __init__(self, browser, by, value, parent_instance=None,
                 attributes=[], sub_elements=[]):
        """
        Init

        :type browser: selenium.webdriver.remote.webelement.WebDriver
        :param browser: WebDriver object like instance

        :type by: selenium.webdriver.common.by.By
        :param by: by which selector method is used to locate
                   the webelement

        :type value: str
        :param value: the value of the selector

        :type parent_instance: object
        :param parent_instance: a reference to the parent object.
                                for this to be useful, parent needs a
                                get_element() method that returns its
                                webelement from its parent's instance

        :type attributes: str []
        :param attributes: list of attribute to create property
                           methods for

        :type sub_elements: SubElement []
        :param sub_elements: list of SubElement objects to attach
                             to this class
        """
        super(Select, self).__init__(
            browser, by, value, parent_instance, attributes, sub_elements)

    @wait_for_display
    def select_by_value(self, value):
        """
        Sets the select object to select a value.

        @type value: string
        @param value: the value to set
        """

        selector = '[value="{v}"]'.format(v=value.replace('"', '\\\"'))
        option = Option(self.browser, By.CSS_SELECTOR,
                        selector, parent_instance=self)
        if not option.is_enabled():
            raise ElementNotSelectableException(
                "Option is disabled and not selectable.")
        option.click()

    @property
    @wait_for_display
    def options(self):
        """
        Get all the options by inside the select element.

        :rtype: Option[]
        :return: the list of elements that represents the
                 option elements
        """

        elems = self.find_elements_by_tag_name("option")
        return Option.init_with_elements(elems)

    @property
    @wait_for_display
    def option(self):
        """
        Gets the selected option of the select object

        @rtype: Option
        @return: the selected option
        """

        return Option(
            self.browser, By.CSS_SELECTOR,
            'option[value="{}"]'.format(self.attr_value), parent_instance=self)

    def select(self, label):
        """
        Select the option by text value.

        :type option: string
        :param option: list of option text for the select
        """
        elems = self.find_elements_by_tag_name("option")
        for elem in elems:
            txt = elem.text
            if txt == label:
                if not elem.is_enabled():
                    raise ElementNotSelectableException(
                        "Option is disabled and not selectable.")
                elem.click()
                return None
        raise ElementNotVisibleException(
            "Could not find the option '{o}'.".format(o=label))


Select.generate_attributes_properties(
    ['autofocus', 'disabled', 'form', 'multiple', 'name',
     'required', 'size', 'value'])


class Option(Element):

    """

    This is a class to simulate HTML select's option object
    interactions

    Tag: option

    Requires a WebElement or WebElement like instance passed into it.

    """

    def __init__(self, browser, by, value, parent_instance=None,
                 attributes=[], sub_elements=[]):
        """
        Init

        :type browser: selenium.webdriver.remote.webelement.WebDriver
        :param browser: WebDriver object like instance

        :type by: selenium.webdriver.common.by.By
        :param by: by which selector method is used to locate
                   the webelement

        :type value: str
        :param value: the value of the selector

        :type parent_instance: object
        :param parent_instance: a reference to the parent object.
                                for this to be useful, parent needs a
                                get_element() method that returns its
                                webelement from its parent's instance

        :type attributes: str []
        :param attributes: list of attribute to create property
                           methods for

        :type sub_elements: SubElement []
        :param sub_elements: list of SubElement objects to attach
                             to this class
        """
        super(Option, self).__init__(
            browser, by, value, parent_instance, attributes, sub_elements)


Option.generate_attributes_properties(
    ['disabled', 'label', 'selected', 'value'])
