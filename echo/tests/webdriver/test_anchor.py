#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_anchor
----------------------------------

Tests for `html.anchor` module.
"""

from __future__ import absolute_import
from html import BaseHtmlElement
from html import anchor
from selenium.webdriver.common.by import By
from selenium.webdriver.support import color
from . import BaseHtmlTest
import pytest
import os


HTMLTEMPLATE = (
    """
<html>
    <head>
        <style>
            a:link {{color: #000;}}
            a:visited {{color: #f0f;}}
            a:hover {{color: #00f;}}
            a:active {{color: #0f0;}}
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


class TestAnchor(BaseHtmlTest):

    """
    Anchor link test suite
    """

    def setup_method(self, method):
        """
        Setup step:
            - create a place to store files to delete.
        """
        super(TestAnchor, self).setup_method(method)
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
            super(TestAnchor, self).teardown_method(method)

    @pytest.mark.parametrize(
        ('attr', 'is_displayed'), [
            ('', True),
            ('style="display: none;"', False),
            ('style="display: block;"', True),
            ('src="www.google.com"', True)
        ])
    def test_display(self, browser, attr, is_displayed):
        """
        Test that the object is displayed depending on the DOM.
        """

        link = anchor.Anchor(browser, By.TAG_NAME, 'a')
        file_name = 'anchor_display_test.html'
        self.test_files.append(file_name)

        link_dom = '<a {attr} >This is a link</a>'.format(attr=attr)
        with open(file_name, 'w') as ofile:
            ofile.write(HTMLTEMPLATE.format(content=link_dom))

        browser.open(
            "file://{}".format(os.path.abspath(file_name)))
        if is_displayed:
            link.wait_to_be_displayed()
        else:
            link.wait_to_be_present()
            assert not link.is_displayed()

    @pytest.mark.parametrize(
        ('state', 'exp_color'), [
            ('default', color.Color.from_string('#000')),
            ('hover', color.Color.from_string('#00f')),
            ('active', color.Color.from_string('#0f0')),

            # The following test case(s) are not possible
            # selenium can not get state color.
            # ('visited', color.Color.from_string('#f0f')),
        ])
    def test_state(self, browser, state, exp_color):
        """
        Tests that the different link state works

        Verify by having unique state color for the link.
        """

        link = anchor.Anchor(browser, By.TAG_NAME, 'a')
        header = BaseHtmlElement(browser, By.TAG_NAME, 'h2')
        file_name = 'anchor_state_test.html'
        html = '<a href="#">This is a link</a>'
        self.test_files.append(file_name)

        with open(file_name, 'w') as ofile:
            ofile.write(HTMLTEMPLATE.format(content=html))

        browser.open(
            "file://{}".format(os.path.abspath(file_name)))
        link.wait_to_be_present()

        if state == 'default':
            pass
        elif state == 'visited':
            link.click()
            browser.url.wait_to_contain('#')

            # after clicking need to lose the focus on the link
            # or otherwise it might be in the hover state.
            header.mouse.hover()
        elif state == 'hover':
            link.mouse.hover()
        elif state == 'active':
            link.mouse.click_and_hold()

        assert color.Color.from_string(link.css('color')) == exp_color
