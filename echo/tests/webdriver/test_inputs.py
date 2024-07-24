#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_input
----------------------------------

Tests for `html.inputs` module.
"""

from __future__ import absolute_import
from html import inputs
from selenium.webdriver.common.by import By
from . import BaseHtmlTest
import os


HTMLTEMPLATE = (
    """
<html>
    <head>
        <style>
        </style>
        <h2>This is a testing page for html-webdriver.</h2>
    </head>

    <body>
        <br/>
        {content}
        <br/>
    </body>
<html>
""")


class TestInputs(BaseHtmlTest):

    """
    Anchor link test suite
    """

    def setup_method(self, method):
        """
        Setup step:
            - create a place to store files to delete.
        """
        super(TestInputs, self).setup_method(method)
        self.test_files = []

    def teardown_method(self, method):
        """
        Teardown step:
            - remove the html files created.

        """
        try:
            for tfile in self.test_files:
                if os.path.exists(tfile):
                    os.remove(tfile)
        finally:
            super(TestInputs, self).teardown_method(method)

    def test_text_value(self, browser):
        """
        Test getting the value of an input
        """

        test_value = u'<3'
        new_value = u'uwu'
        test_input = inputs.Text(browser, By.TAG_NAME, 'input')
        file_name = 'input_test.html'
        self.test_files.append(file_name)

        input_dom = '<input type="text" value="{}"></input>'.format(test_value)
        with open(file_name, 'w') as ofile:
            ofile.write(HTMLTEMPLATE.format(content=input_dom))

        browser.open(
            "file://{}".format(os.path.abspath(file_name)))
        assert test_input.value == test_value

        test_input.value = new_value
        assert test_input.value == new_value

    def test_text_low_performance(self, browser):
        """
        Test getting the value of an input
        """

        test_value = u'<3'
        new_value = u'uwu'
        test_input = inputs.Text(browser, By.TAG_NAME, 'input')
        file_name = 'input_test.html'
        self.test_files.append(file_name)

        input_dom = '<input type="text" value="{}"></input>'.format(test_value)
        with open(file_name, 'w') as ofile:
            ofile.write(HTMLTEMPLATE.format(content=input_dom))

        browser.open(
            "file://{}".format(os.path.abspath(file_name)))

        test_input.set_value_with_wait(new_value)
        assert test_input.value == new_value
