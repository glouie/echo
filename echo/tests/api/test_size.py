#!/usr/bin/python
# vim: set fileencoding=utf-8 :

"""
test_size.py
------------

Test the Size class.
"""

from __future__ import absolute_import
import pytest
from html.support import size

xfail = pytest.mark.xfail


class MockWebElement():

    """
    Mock a WebElement object.
    """

    def __init__(self, height, width):
        """
        Init

        :type height: int
        :param height: height value of the element.

        :type width: int
        :param width: width value of the element.
        """
        self._height = height
        self._width = width

    @property
    def size(self):
        """
        Mock the size property of the webelement's size property
        Get the size in to format of a dictionary.

        :rtype: dict
        :return: dict(height, width)
        """
        return {'width': self._width, 'height': self._height}


class MockElement():

    """
    Mock a BaseHtmlElement object.
    """

    def __init__(self, height, width):
        """
        Init

        :type height: int
        :param height: height value of the element.

        :type width: int
        :param width: width value of the element.
        """

        self._height = height
        self._width = width
        self.browser = None

    @property
    def _webelement(self):
        """
        Mock the _webelement property to return a MockWebElement.
        """
        return MockWebElement(self._height, self._width)


def gen_size(height, width):
    """
    Create a size object with the height and width.

    :rtype: html.support.size.Size
    :return: a Size object with the mock element of a given height and width
    """
    return size.Size(MockElement(height=height, width=width)._webelement.size)


class TestSize(object):

    """
    Test the size object.
    """

    @pytest.mark.parametrize(
        ('height', 'width', 'exp_result'),
        [
            (10, 20, {'height': 10, 'width': 20}),
            (10.1, 20.9, {'height': 10.1, 'width': 20.9}),
            (0, 0, {'height': 0, 'width': 0}),
            (-10, -20, {'height': -10, 'width': -20}),
            ('a', 'b', {'height': 'a', 'width': 'b'}),
            (10, 20.0, {'height': 10.0, 'width': 20}),
        ],
        ids=[
            'positive',
            'float',
            'zero',
            'negative',
            'string',
            'equal float to int',
        ]
    )
    def test_value(self, height, width, exp_result):
        """
        Test that the value property returns the size of the element.
        """
        size = gen_size(height, width)
        msg = "The value did not return what was expected."
        assert size.value == exp_result, msg

    @pytest.mark.parametrize(
        ('size1', 'size2', 'exp_result'),
        [
            ((0, 0), (0, 0), False),
            ((0, 0), (-1, -3), False),
            ((0, 0), (-1, 0), False),
            ((0, 0), (0, -3), False),

            ((2, 2), (1, 1), False),
            ((2, 2), (0, 0), False),
            ((2, 2), (-1, -1), False),

            ((1, 2), (1, 2), False),
            ((2, 1), (1, 2), False),

            ((0, 3), (3, 3), False),
            ((3, 0), (3, 3), False),
            ((3, 3), (0, 3), False),
            ((3, 3), (3, 0), False),

            ((-2, -2), (1, -1), True),
            ((-2, -2), (-1, 1), True),

            ((0, 0), (1, 2), True),
            ((3, 4), (4, 5), True),

            ((-2, -1), (0, 0), True),
            ((-2, -3), (2, 3), True),
        ],
    )
    def test_lt(self, size1, size2, exp_result):
        """
        Test the size's '<' operator.
        """

        size1 = gen_size(*size1)
        size2 = gen_size(*size2)
        msg = "Is {s1} < {s2}?".format(s1=size1, s2=size2)
        assert (size1 < size2) == exp_result, msg

    @pytest.mark.parametrize(
        ('size1', 'size2', 'exp_result'),
        [
            ((0, 0), (0, 0), True),
            ((0, 0), (-1, -3), False),
            ((0, 0), (-1, 0), False),
            ((0, 0), (0, -3), False),

            ((2, 2), (1, 1), False),
            ((2, 2), (0, 0), False),
            ((2, 2), (-1, -1), False),

            ((1, 2), (1, 2), True),
            ((2, 1), (1, 2), False),

            ((0, 3), (3, 3), True),
            ((3, 0), (3, 3), True),
            ((3, 3), (0, 3), False),
            ((3, 3), (3, 0), False),
            ((3, 3), (3, 3), True),

            ((-2, -2), (1, -1), True),
            ((-2, -2), (-1, 1), True),

            ((0, 0), (1, 2), True),
            ((3, 4), (4, 5), True),

            ((-2, -1), (0, 0), True),
            ((-2, -3), (2, 3), True),
        ],
    )
    def test_le(self, size1, size2, exp_result):
        """
        Test the size's '<=' operator.
        """

        size1 = gen_size(*size1)
        size2 = gen_size(*size2)
        msg = "Is {s1} <= {s2}?".format(s1=size1, s2=size2)
        assert (size1 <= size2) == exp_result, msg

    @pytest.mark.parametrize(
        ('size1', 'size2', 'exp_result'),
        [
            ((0, 0), (0, 0), False),
            ((0, 0), (-1, -3), True),
            ((0, 0), (-1, 0), False),
            ((0, 0), (0, -3), False),

            ((2, 2), (1, 1), True),
            ((2, 2), (0, 0), True),
            ((2, 2), (-1, -1), True),

            ((1, 2), (1, 2), False),
            ((2, 1), (1, 2), False),

            ((0, 3), (3, 3), False),
            ((3, 0), (3, 3), False),
            ((3, 3), (0, 3), False),
            ((3, 3), (3, 0), False),

            ((-2, -2), (1, -1), False),
            ((-2, -2), (-1, 1), False),

            ((0, 0), (1, 2), False),
            ((3, 4), (4, 5), False),

            ((-2, -1), (0, 0), False),
            ((-2, -3), (2, 3), False),
        ],
    )
    def test_gt(self, size1, size2, exp_result):
        """
        Test the size's '>' operator.
        """

        size1 = gen_size(*size1)
        size2 = gen_size(*size2)
        msg = "Is {s1} > {s2}?".format(s1=size1, s2=size2)
        assert (size1 > size2) == exp_result, msg

    @pytest.mark.parametrize(
        ('size1', 'size2', 'exp_result'),
        [
            ((0, 0), (0, 0), True),
            ((0, 0), (-1, -3), True),
            ((0, 0), (-1, 0), True),
            ((0, 0), (0, -3), True),

            ((2, 2), (1, 1), True),
            ((2, 2), (0, 0), True),
            ((2, 2), (-1, -1), True),

            ((1, 2), (1, 2), True),
            ((2, 1), (1, 2), False),

            ((0, 3), (3, 3), False),
            ((3, 0), (3, 3), False),
            ((3, 3), (0, 3), True),
            ((3, 3), (3, 0), True),
            ((3, 3), (3, 3), True),

            ((-2, -2), (1, -1), False),
            ((-2, -2), (-1, 1), False),

            ((0, 0), (1, 2), False),
            ((3, 4), (4, 5), False),

            ((-2, -1), (0, 0), False),
            ((-2, -3), (2, 3), False),
        ],
    )
    def test_ge(self, size1, size2, exp_result):
        """
        Test the size's '>=' operator.
        """

        size1 = gen_size(*size1)
        size2 = gen_size(*size2)
        msg = "Is {s1} >= {s2}?".format(s1=size1, s2=size2)
        assert (size1 >= size2) == exp_result, msg

    @pytest.mark.parametrize(
        ('size1', 'size2', 'exp_result'),
        [
            ((0, 3), (3, 3), False),
            ((3, 0), (3, 3), False),
            ((3, 3), (0, 3), False),
            ((3, 3), (3, 0), False),
            ((-3, 3), (3, -3), False),
            ((3, 3), (-3, -3), False),
            ((3, 3), (3, 3), True),
            ((0, 0), (0, 0), True),
            ((3, 3), (3.0, 3.0), True),
            ((-3, -3), (-3, -3), True),
            ((3, 3), (3, 3), True),
        ],
    )
    def test_eq(self, size1, size2, exp_result):
        """
        Test the size's '==' operator.
        """

        size1 = gen_size(*size1)
        size2 = gen_size(*size2)
        msg = "Is {s1} == {s2}?".format(s1=size1, s2=size2)
        assert (size1 == size2) == exp_result, msg

    @pytest.mark.parametrize(
        ('size1', 'size2', 'exp_result'),
        [
            ((0, 3), (3, 3), True),
            ((3, 0), (3, 3), True),
            ((3, 3), (0, 3), True),
            ((3, 3), (3, 0), True),
            ((-3, 3), (3, -3), True),
            ((3, 3), (-3, -3), True),
            ((3, 3), (3, 3), False),
            ((0, 0), (0, 0), False),
            ((3, 3), (3.0, 3.0), False),
            ((-3, -3), (-3, -3), False),
            ((3, 3), (3, 3), False),
        ],
    )
    def test_ne(self, size1, size2, exp_result):
        """
        Test the size's '!=' operator.
        """

        size1 = gen_size(*size1)
        size2 = gen_size(*size2)
        msg = "Is {s1} != {s2}?".format(s1=size1, s2=size2)
        assert (size1 != size2) == exp_result, msg

    @pytest.mark.parametrize(
        ('dimension', 'key'),
        [
            ({'height': 10, 'width': 20}, 'height'),
            ({'height': 10, 'width': 20}, 'width'),

            xfail(reason="Invalid key: foo")(
                ({'height': 10, 'width': 20}, 'foo')),

            xfail(reason="Invalid key: None")(
                ({'height': 10, 'width': 20}, None)),
        ]
    )
    def test_getitem(self, dimension, key):
        """
        Test the __getitem__ of size.
        """

        size = gen_size(dimension['height'], dimension['width'])
        msg = "__getitem__ did not retrieve the right value."
        assert size[key] == dimension[key], msg
