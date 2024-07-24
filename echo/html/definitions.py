#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# pylint: disable=too-many-arguments
# pylint: disable=dangerous-default-value
# pylint: disable=locally-disabled

"""
Definitionslist module
"""

from __future__ import absolute_import
from collections import namedtuple
from html import Element


DefinitionsListItems = namedtuple(
    'DefinitionsListItems', ['term', 'description'])


class List(Element):

    """
    This is a class to simulate HTML definitions list object
    interactions.

    Tag: <dl>

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
                   the WebElement

        :type value: str
        :param value: the value of the selector

        :type parent_instance: object
        :param parent_instance: a reference to the parent object.
                                for this to be useful, parent needs a
                                get_element() method that returns its
                                WebElement from its parent's instance

        :type attributes: str []
        :param attributes: list of attribute to create property
                           methods for

        :type sub_elements: SubElement []
        :param sub_elements: list of SubElement objects to attach
                             to this class
        """

        attributes = [] + list(attributes)

        super(List, self).__init__(
            browser, by, value, parent_instance, attributes, sub_elements)

    @property
    def terms(self):
        """
        Get the definition terms.

        :rtype: Term[]
        :return: a list of Term objects
        """

        elems = self.find_elements_by_tag_name('dt')
        return Term.init_with_elements(elems)

    @property
    def descriptions(self):
        """
        Get the definition descriptions.

        :rtype: Description[]
        :return: a list of Description objects.
        """

        elems = self.find_elements_by_tag_name('dd')
        return Description.init_with_elements(elems)

    @property
    def items(self):
        """
        Get the definitions list items in a list.

        :rtype: DefinitionsListItems[]
        :return: list of DefinitionsListItems objects

        Note: if you have unbalanced terms and descriptions,
              you will get the minimal set
        """

        dts = self.terms
        dds = self.descriptions
        return [DefinitionsListItems(dt, dd) for dt, dd, in zip(dts, dds)]

    def get_description_for_term(self, term):
        """
        Get the value (dd) for the given term (dt)

        :type term: string
        :param term: the term to look up for the description

        :rtype: string
        :return: the description for the given term
        """

        for item in self.items:
            if item.term.text == term:
                return item.description.text
        raise AssertionError(
            "Definition term not found: '{t}'.".format(t=term))


class Term(Element):

    """
    This is a class to simulate HTML definitions term object
    interactions.

    Tag: <dt>

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

        :type value: str
        :param value: the value of the selector

        :type parent_instance: object
        :param parent_instance: a reference to the parent object.
                                for this to be useful, parent needs a
                                get_element() method that returns its
                                webelement from its parent's instance

        :type attributes: str[]
        :param attributes: list of attribute to create property
                           methods for

        :type sub_elements: SubElement []
        :param sub_elements: list of SubElement objects to attach
                             to this class
        """

        attributes = [] + list(attributes)

        super(Term, self).__init__(
            browser, by, value, parent_instance, attributes, sub_elements)


class Description(Element):

    """
    This is a class to simulate HTML definitions description object
    interactions.

    Tag: <dd>

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

        :type value: str
        :param value: the value of the selector

        :type parent_instance: object
        :param parent_instance: a reference to the parent object.
                                for this to be useful, parent needs a
                                get_element() method that returns its
                                webelement from its parent's instance

        :type attributes: string[]
        :param attributes: list of attribute to create property
                           methods for

        :type sub_elements: SubElement []
        :param sub_elements: list of SubElement objects to attach
                             to this class
        """

        attributes = [] + list(attributes)

        super(Description, self).__init__(
            browser, by, value, parent_instance, attributes, sub_elements)
