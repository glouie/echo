#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# pylint: disable=too-many-arguments
# pylint: disable=dangerous-default-value
# pylint: disable=locally-disabled

"""
Table module
"""

from __future__ import absolute_import
from selenium.webdriver.common.by import By
from html import Element
from bs4 import BeautifulSoup


class TableFormatError(Exception):

    """
    Table format exception class.
    """

    pass


class Table(Element):

    """
    This is a class to simulate HTML table object interactions.

    Tag: <table>

    Requires a WebDriver or WebDriver like instance passed into it.
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

        attributes = ['border', 'sortable'] + list(attributes)

        super(Table, self).__init__(
            browser, by, value, parent_instance, attributes, sub_elements)

        self.body = Body(
            self.browser, By.TAG_NAME, 'tbody', parent_instance=self)
        self.caption = Caption(
            self.browser, By.TAG_NAME, 'caption', parent_instance=self)
        self.colgroup = Colgroup(
            self.browser, By.TAG_NAME, 'colgroup', parent_instance=self)
        self.foot = Foot(
            self.browser, By.TAG_NAME, 'tfoot', parent_instance=self)
        self.head = Head(
            self.browser, By.TAG_NAME, 'thead', parent_instance=self)

    @property
    def rows(self):
        """
        Get all the table rows

        :rtype: Row[]
        :return: a list of all the table rows.
        """

        elems = self.find_elements_by_tag_name('tr')
        return Row.init_with_elements(elems)

    def has_header_row(self):
        """
        Check to see if there are table header tags in the first row.

        :rtype: boolean
        :return: True if there are th tags in the first row
                 and False if not.
        """

        # faster to just get the first row than to get all rows.
        first_row = self.find_element_by_tag_name('tr')
        elems = first_row.find_elements_by_tag_name('th')
        return bool(list(elems))

    @property
    def header_row(self):
        """
        Get the header row

        :rtype: Header
        :return: the header row if it exists and None of not.
        """

        # faster to just get the first row than to get all rows.
        first_row = self.find_element_by_tag_name('tr')
        elems = first_row.find_elements_by_tag_name('th')
        if elems:
            return Row.init_with_element(first_row)

    @property
    def text_matrix(self):
        """
        Get a two dimensional array of strings, representing the table.

        :rtype: str [][]
        :return: two dimensional array of all the cell text values.
        """
        rows_text = []
        if self.has_header_row():
            rows_text.append(self.header_row.headers_text)
        table_data = self.get_attribute('outerHTML')
        soup = BeautifulSoup(table_data, "html.parser")
        matrix = [[td.text.strip() for td in tr.select('td')]
                  for tr in soup.select('tbody > tr')]
        rows_text.extend(matrix)
        return rows_text

    def get_cell_text_for_header_label(self, label):
        """
        Get a two dimensional array of strings, representing the
        cells in the column of the given header label.

        :type label: string
        :param label: the label to find the matching columns.

        :rtype: str [][]
        :return: returns a list of all the rows, and all the data in
                 each row that in a column matching the label.
        """
        if not self.has_header_row():
            raise TableFormatError("Table has no header row.")
        rows = self.rows
        header_row = rows.pop(0)

        if len(header_row.headers) != len(rows[0].data):
            raise TableFormatError(
                "The number of cells in the header row does not match "
                "the number of cells in a non header row.")

        indices = header_row.get_indices_of_label(label)
        return [[row.data[index].text for index in indices] for row in rows]


class Body(Element):

    """
    This is a class to simulate HTML table body object interactions.

    Tag: <tbody>

    Requires a WebDriver or WebDriver like instance passed into it.
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

        super(Body, self).__init__(
            browser, by, value, parent_instance, attributes, sub_elements)

    @property
    def rows(self):
        """
        Get all the table rows

        :rtype: Row[]
        :return: a list of all the table rows.
        """

        elems = self.find_elements_by_tag_name('tr')
        return Row.init_with_elements(elems)


class Caption(Element):

    """
    This is a class to simulate HTML table caption object interactions.

    Tag: <caption>

    Requires a WebDriver or WebDriver like instance passed into it.
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

        super(Caption, self).__init__(
            browser, by, value, parent_instance, attributes, sub_elements)


class Col(Element):

    """
    This is a class to simulate HTML table col object interactions.

    Tag: <col>

    Requires a WebDriver or WebDriver like instance passed into it.
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

        attributes = ['span']

        super(Col, self).__init__(
            browser, by, value, parent_instance, attributes, sub_elements)


class Colgroup(Element):

    """
    This is a class to simulate HTML table colgroup object
    interactions.

    Tag: <colgroup>

    Requires a WebDriver or WebDriver like instance passed into it.
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

        attributes = ['span'] + list(attributes)

        super(Colgroup, self).__init__(
            browser, by, value, parent_instance, attributes, sub_elements)

    def cols(self):
        """
        Get the list of Col objects.

        :rtype: Col[]
        :return: the list of Col objects.
        """
        elems = self.find_elements_by_tag_name('col')
        return Col.init_with_elements(elems)


class Data(Element):

    """
    This is a class to simulate HTML table data object interactions.

    Tag: <td>

    Requires a WebDriver or WebDriver like instance passed into it.
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

        attributes = ['colspan', 'headers'] + list(attributes)

        super(Data, self).__init__(
            browser, by, value, parent_instance, attributes, sub_elements)


class Foot(Element):

    """
    This is a class to simulate HTML table foot object interactions.

    Tag: <tfoot>

    Requires a WebDriver or WebDriver like instance passed into it.
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

        super(Foot, self).__init__(
            browser, by, value, parent_instance, attributes, sub_elements)

    @property
    def rows(self):
        """
        Get all the table rows

        :rtype: Row []
        :return: a list of all the table rows.
        """

        elems = self.find_elements_by_tag_name('tr')
        return Row.init_with_elements(elems)


class Head(Element):

    """
    This is a class to simulate HTML table head object interactions.

    Tag: <thead>

    Requires a WebDriver or WebDriver like instance passed into it.
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

        super(Head, self).__init__(
            browser, by, value, parent_instance, attributes, sub_elements)

    @property
    def rows(self):
        """
        Get all the table rows

        :rtype: Row []
        :return: a list of all the table rows.
        """

        elems = self.find_elements_by_tag_name('tr')
        return Row.init_with_elements(elems)


class Header(Element):

    """
    This is a class to simulate HTML table header object interactions.

    Tag: <th>

    Requires a WebDriver or WebDriver like instance passed into it.
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

        attributes = [
            'abbr', 'colspan', 'headers', 'rowspan', 'scope', 'sorted'
        ] + list(attributes)

        super(Header, self).__init__(
            browser, by, value, parent_instance, attributes, sub_elements)


class Row(Element):

    """
    This is a class to simulate HTML table object interactions.

    Tag: <tr>

    Requires a WebDriver or WebDriver like instance passed into it.
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

        super(Row, self).__init__(
            browser, by, value, parent_instance, attributes, sub_elements)

    @property
    def data(self):
        """
        Get the table data objects inside the table row.

        :rtype: Data []
        :return: list of Data objects
        """
        elems = self.find_elements_by_tag_name('td')
        return Data.init_with_elements(elems)

    @property
    def headers(self):
        """
        Get the table headers objects inside the table row.

        :rtype: Header []
        :return: list of Data objects
        """
        elems = self.find_elements_by_tag_name('th')
        return Header.init_with_elements(elems)

    @property
    def data_text(self):
        """
        Get the list of data text values.

        :rtype: str []
        :return: list of the data text values.
        """
        # we are going to bypass checking for cells to be displayed
        # because tables are big and generally can span off screen
        # so this is faster and more reliable.
        return [data.element.text for data in self.data]

    @property
    def headers_text(self):
        """
        Get the list of headers text values.

        :rtype: str []
        :return: list of the header text values.
        """
        # we are going to bypass checking for cells to be displayed
        # because tables are big and generally can span off screen
        # so this is faster and more reliable.
        return [header.element.text for header in self.headers]

    def get_indices_of_label(self, label):
        """
        Get the list of indices that the label occurs in the table.

        :rtype: int []
        :return: list of indices of the headers text list that
                 contains value that matches the label
        """

        headers = self.headers_text
        return [idx for idx, val in enumerate(headers) if val == label]
