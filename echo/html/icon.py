#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# pylint: disable=too-many-arguments
# pylint: disable=dangerous-default-value
# pylint: disable=locally-disabled

"""
Icon module
"""


from __future__ import absolute_import
from html import Element


class Icon(Element):

    """
    This is a class to simulate HTML icon object interactions.

    Tag: <i, icon>

    Requires a webdriver or webdriver like instance passed into it.
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

        super(Icon, self).__init__(
            browser, by, value, parent_instance, attributes, sub_elements)
