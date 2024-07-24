#!/usr/bin/python
# vim: set fileencoding=utf-8 :

"""
test_element_instantiations.py.py
------------

Test the instantiation of the html objects.
"""

from __future__ import absolute_import

import html
import inspect
import pkgutil
from html import Element

import pytest
from selenium.webdriver.common.by import By

HTMLWD_MODULES = [
    loader.find_module(module_name).load_module(module_name)
    for loader, module_name, is_pkg in pkgutil.walk_packages(
        html.__path__)
]


HTMLWD_BASEHTMLELEMENT_CLASSES = set([
    getattr(mod, mcls) for mod in HTMLWD_MODULES
    for mcls in mod.__dict__
    if (not mcls.startswith('_') and
        inspect.isclass(getattr(mod, mcls)) and
        issubclass(getattr(mod, mcls), Element))])


HTMLWD_PARAMS = [
    ("{}.{}".format(mcls.__module__, mcls.__name__), mcls)
    for mcls in HTMLWD_BASEHTMLELEMENT_CLASSES]
HTMLWD_PARAMS.sort()


class MockBrowser():

    """
    Mock a Browser object.
    """

    def __init__(self):
        """
        Init: barebone requirement.
        """

        self.timeout = 60
        self.poll_frequency = 0.5


class TestHtmlwebdriverElementInstantiations(object):

    """
    Test the instantiation of the html objects.
    """

    @pytest.mark.parametrize(
        "htmlwd_class",
        [htmlwd_cls for _, htmlwd_cls in HTMLWD_PARAMS],
        ids=[name for name, _ in HTMLWD_PARAMS]
    )
    def test_basic_instantiations(self, htmlwd_class):
        """
        Test the basic instantiation of all the htmlwd_class
        """

        htmlwd_class(MockBrowser(), By.TAG_NAME, 'body')
