#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_button
----------------------------------

Tests for `html.button` module.
"""

from __future__ import absolute_import
from html import button
from selenium.webdriver.common.by import By
from . import BaseHtmlTest
import pytest
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


class TestButton(BaseHtmlTest):

    """
    Anchor link test suite
    """

    def setup_method(self, method):
        """
        Setup step:
            - create a place to store files to delete.
        """
        super(TestButton, self).setup_method(method)
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
            super(TestButton, self).teardown_method(method)

    @pytest.mark.parametrize(
        ('attr', 'is_displayed'), [
            ('', True),
            ('style="display: none;"', False),
            ('style="display: block;"', True),
            ('type=submit', True)
        ])
    def test_display(self, browser, attr, is_displayed):
        """
        Test that the object is displayed depending on the DOM.
        """

        testbutton = button.Button(browser, By.TAG_NAME, 'button')
        file_name = 'button_display_test.html'
        self.test_files.append(file_name)

        button_dom = '<button {attr} >Button</button>'.format(attr=attr)
        with open(file_name, 'w') as ofile:
            ofile.write(HTMLTEMPLATE.format(content=button_dom))

        browser.open(
            "file://{}".format(os.path.abspath(file_name)))
        if is_displayed:
            testbutton.wait_to_be_displayed()
        else:
            testbutton.wait_to_be_present()
            assert not testbutton.is_displayed()
