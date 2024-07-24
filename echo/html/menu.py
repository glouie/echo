#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# pylint: disable=too-many-arguments
# pylint: disable=dangerous-default-value
# pylint: disable=locally-disabled

"""
Menu module
"""


from __future__ import absolute_import
from html import Element


class MenuItem(Element):

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
        super(MenuItem, self).__init__(
            browser, by, value, parent_instance, attributes, sub_elements)


MenuItem.generate_attributes_properties(
    ['checked', 'command', 'default', 'disabled', 'icon',
     'label', 'radiogroup', 'type'])


class Menu(Element):

    """
    This is a class to simulate HTML menu list object interactions.

    Tag: <menu>

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
        super(Menu, self).__init__(
            browser, by, value, parent_instance, attributes, sub_elements)

    @property
    def items(self):
        """
        Get the list of list items.

        :rtype: MenuItem[]
        :return: the list of MenuItem objects
        """
        elems = self.find_elements_by_tag_name('menuitem')
        return MenuItem.init_with_element(elems)

    @property
    def labels(self):
        """
        Get the labels of all the list items.

        :rtype: string[]
        :return: the list of the MenuItem's labels
        """
        return [item.label for item in self.items]

    @property
    def values(self):
        """
        Get the values of all the list items.

        :rtype: string[]
        :return: the list of the MenuItem's value
        """
        return [item.value for item in self.items]


Menu.generate_attributes_properties(['label', 'type'])
