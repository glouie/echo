#!/usr/bin/python
# vim: set fileencoding=utf-8 :

"""
Size class
===========
* Size class to handle size comparisons.
"""


class Size(object):

    """
    Helper class to provide the more functionality to size
    """

    def __init__(self, elem_size):
        """
        Init

        :type elem_size: dict
        :param elem_size: the size of the web element

        """
        self._size = elem_size

    @property
    def value(self):
        """
        Return the size dictionary

        :rtype: dict
        :return: the webelement's size.
        """
        return self._size.copy()

    def __str__(self):
        """
        Prints the string value of the size dictionary

        :rtype: string
        :return: the size dictionary as a string.
        """
        return str(self.value)

    @property
    def height(self):
        """
        Get the height attribute for the size

        :rtype: int
        :return: the size's height value
        """
        return self.value['height']

    @property
    def width(self):
        """
        Get the width attribute for the size

        :rtype: int
        :return: the size's width value
        """
        return self.value['width']

    @property
    def area(self):
        """
        Get the area of the element

        :rtype: int
        :return: the area of the element,
                 i.e.: the product of the width and height
        """
        size = self.value
        return size['width'] * size['height']

    def __eq__(self, other):
        """
        Overloading the '==' operator
        Evaluates the height and width, does not compare area.

        If two elements are the same size but oriented in different
        positions, this will return False because the heights and
        widths are different even though the area is the same.

        :type other: Size
        :param other: the other size object to compare with

        :rtype: boolean
        :return: True if BOTH the height and width is the same.
        """
        selfsize = self.value
        othersize = other.value

        return (
            selfsize['height'] == othersize['height'] and
            selfsize['width'] == othersize['width'])

    def __ne__(self, other):
        """
        Overloading the '!=' operator
        Evaluates the height and width, does not compare area.

        If two elements are the same size but oriented in different
        positions, this will return True because the heights and
        widths are different even though the area is the same.

        :type other: Size
        :param other: the other size object to compare with

        :rtype: boolean
        :return: True if the height and width are both not the same.
        """
        return not self.__eq__(other)

    def __lt__(self, other):
        """
        Overloading the '<' operator
        Evaluates the height and width, does not compare area.

        Both the element's width and height has to be less than
        each other for this to be true, if either the width or
        the height is equal, this method will return False.

        :type other: Size
        :param other: the other size object to compare with

        :rtype: boolean
        :return: True if the height and width are less.
        """
        selfsize = self.value
        othersize = other.value
        return (
            selfsize['height'] < othersize['height'] and
            selfsize['width'] < othersize['width'])

    def __le__(self, other):
        """
        Overloading the '<=' operator
        Evaluates the height and width, does not compare area.

        Both the element's width and height has to be less than or
        equal to each other for this to be true, if just either
        the width or the height is equal, this method will return True.

        :type other: Size
        :param other: the other size object to compare with

        :rtype: boolean
        :return: True if the height and width are less than equal to.
        """
        selfsize = self.value
        othersize = other.value
        return (
            selfsize['height'] <= othersize['height'] and
            selfsize['width'] <= othersize['width'])

    def __gt__(self, other):
        """
        Overloading the '>' operator
        Evaluates the height and width, does not compare area.

        Both the element's width and height has to be greater than
        each other for this to be true, if either the width or
        the height is equal, this method will return False.

        :type other: Size
        :param other: the other size object to compare with

        :rtype: boolean
        :return: True if the height and width are greater.
        """
        selfsize = self.value
        othersize = other.value
        return (
            selfsize['height'] > othersize['height'] and
            selfsize['width'] > othersize['width'])

    def __ge__(self, other):
        """
        Overloading the '>=' operator
        Evaluates the height and width, does not compare area.

        Both the element's width and height has to be greater than or
        equal to each other for this to be true, if just either
        the width or the height is equal, this method will return True.

        :type other: Size
        :param other: the other size object to compare with

        :rtype: boolean
        :return: True if the height and width are greater than equal to.
        """
        selfsize = self.value
        othersize = other.value
        return (
            selfsize['height'] >= othersize['height'] and
            selfsize['width'] >= othersize['width'])

    def __getitem__(self, key):
        """
        Allowing the access of the size's dictionary items.

        :type key: string
        :param key: the size key to access: 'height', 'width'

        :rtype: object
        :return: whatever is stored in the size's dict using key.
        """
        return self.value[key]
