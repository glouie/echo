#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# pylint: disable=too-many-arguments
# pylint: disable=dangerous-default-value
# pylint: disable=locally-disabled

"""
Lists module
"""


from __future__ import absolute_import
from html import Element
from html import wait_for_display


class ListItem(Element):

    """
    This is a class to simulate HTML list item object interactions.

    Tag: <li>

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

        :type value: string
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

        attributes = ['value'] + list(attributes)

        super(ListItem, self).__init__(
            browser, by, value, parent_instance, attributes, sub_elements)

    @property
    def label(self):
        """
        Get the text value of the list item

        :rtype: string
        :return: the text value of the list item
        """

        return self.text


class OrderedList(Element):

    """
    This is a class to simulate HTML ordered list object interactions.

    Tag: <ol>

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

        :type value: string
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

        attributes = [] + list(attributes)

        super(OrderedList, self).__init__(
            browser, by, value, parent_instance, attributes, sub_elements)

    @property
    @wait_for_display
    def items(self):
        """
        Get the list of list items.

        :rtype: ListItem[]
        :return: the list of ListItem objects
        """
        elems = self.find_elements_by_tag_name('li')
        return ListItem.init_with_elements(elems)

    @property
    @wait_for_display
    def labels(self):
        """
        Get the labels of all the list items.

        :rtype: string[]
        :return: the list of the ListItem's labels
        """
        return [item.label for item in self.items]

    @property
    @wait_for_display
    def values(self):
        """
        Get the values of all the list items.

        :rtype: string[]
        :return: the list of the ListItem's value
        """
        return [item.attr_value for item in self.items]


class UnorderedList(Element):

    """
    This is a class to simulate HTML unordered list object interactions.

    Tag: <ul>

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

        :type value: string
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

        attributes = [] + list(attributes)

        super(UnorderedList, self).__init__(
            browser, by, value, parent_instance, attributes, sub_elements)

    @property
    @wait_for_display
    def items(self):
        """
        Get the list of list items.

        :rtype: ListItem[]
        :return: the list of ListItem objects
        """
        elems = self.find_elements_by_tag_name('li')
        return ListItem.init_with_elements(elems)

    @property
    @wait_for_display
    def labels(self):
        """
        Get the labels of all the list items.

        :rtype: string[]
        :return: the list of the ListItem's labels
        """
        return [item.label for item in self.items]

    @property
    @wait_for_display
    def values(self):
        """
        Get the values of all the list items.

        :rtype: string[]
        :return: the list of the ListItem's value
        """
        return [item.attr_value for item in self.items]
