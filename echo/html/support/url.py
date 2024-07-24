#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# pylint: disable=no-member

"""
Url
===
    Object to facilitate url related operation

"""

from __future__ import absolute_import
import six
import polling
from selenium.webdriver.support import wait
from html import TIMEOUT


class Url(object):

    """
    Url object to facilitate url related operations.
    """

    def __init__(self, driver, url=None):
        """
        Url Init

        :type browser: selenium.webdriver.remote.webelement.WebDriver
        :param browser: WebDriver object like instance

        :type url: string
        :param url: the current url string.
        """

        self.driver = driver
        self._url = url

    def __str__(self):
        """
        String representation of the class is the url string.

        :rtype: string
        :return: the current state of the url string
        """
        return self._url

    def update(self):
        """
        Updates the url state with the latest value of the browser url.

        :rtype: Url
        :return: returns itself after updating to allow chaining.
        """
        self._url = self.driver.current_url
        return self

    @property
    def value(self):
        """
        Get the value of the url string.

        :rtype: string
        :return: the current state of the url string
        """
        return self._url

    def has_text(self, text):
        """
        Check to see if the given text is in the url string.

        :type text: string
        :param text: the text to check in the url string.
        """
        return bool(text in self._url)

    def wait_to_contain(
            self, text, timeout=TIMEOUT, frequency=wait.POLL_FREQUENCY,
            refresh=False):
        """
        Wait for the url to contain a specified text.

        :type text: string
        :param text: the text to wait to appear in the url.

        :type timeout: int
        :param timeout: number for seconds to wait before giving up

        :type frequency: int
        :param frequency: number for seconds to wait before
                          polling again

        :type refresh: boolean
        :param refresh: True to fresh page for every poll
        """

        def wait_condition():
            """
            Wait condition to satisfy this specific wait method

            :rtype: bool
            :return: True if url contains the given text
                     and False if not
            """
            if refresh:
                self.driver.refresh()
            self._url = self.driver.current_url
            return self.has_text(text)

        return polling.poll_for_condition(
            wait_condition, timeout=timeout, frequency=frequency)

    @property
    def scheme(self):
        """
        Urlparse the url to get the scheme

        :rtype: string
        :return: the scheme attribute of the url
        """
        return six.moves.urllib.parse.urlsplit(self._url).scheme

    @property
    def netloc(self):
        """
        Urlparse the url to get the netloc

        :rtype: string
        :return: the netloc attribute of the url
        """
        return six.moves.urllib.parse.urlsplit(self._url).netloc

    @property
    def path(self):
        """
        Urlparse the url to get the path

        :rtype: string
        :return: the path attribute of the url
        """
        return six.moves.urllib.parse.urlsplit(self._url).path

    @property
    def query(self):
        """
        Urlparse the url to get the query

        :rtype: string
        :return: the query attribute of the url
        """
        return six.moves.urllib.parse.urlsplit(self._url).query

    @property
    def fragment(self):
        """
        Urlparse the url to get the fragment

        :rtype: string
        :return: the fragment attribute of the url
        """
        return six.moves.urllib.parse.urlsplit(self._url).fragment

    @property
    def username(self):
        """
        Urlparse the url to get the username

        :rtype: string
        :return: the username attribute of the url
        """
        return six.moves.urllib.parse.urlsplit(self._url).username

    @property
    def password(self):
        """
        Urlparse the url to get the password

        :rtype: string
        :return: the password attribute of the url
        """
        return six.moves.urllib.parse.urlsplit(self._url).password

    @property
    def port(self):
        """
        Urlparse the url to get the port

        :rtype: string
        :return: the port attribute of the url
        """
        return six.moves.urllib.parse.urlsplit(self._url).port

    def get_url_params_as_dict(self):
        '''
        Returns the current URL query string parameters as a dict
        @rtype: dict
        @return: dict with all query string parameters
        '''
        parsed_url = six.moves.urllib.parse.urlparse(
            self.driver.current_url.encode('utf-8'))
        # IE url is different than other browsers: SPL-102027
        qs_dict = six.moves.urllib.parse.parse_qs(parsed_url.query)
        if (self.driver.name.strip() == 'internet explorer' and
                '?' in parsed_url.fragment):
            fs_dict = six.moves.urllib.parse.parse_qs(
                parsed_url.fragment.split('?')[1])
        else:
            fs_dict = six.moves.urllib.parse.parse_qs(parsed_url.fragment)
        # The parsed dict will have each key mapped to a list of values -
        # since technically a key can appear multiple times - for convenience
        # convert any 1-item lists into just the value.
        for key, item in six.iteritems(qs_dict):
            if isinstance(item, list) and len(item) == 1:
                qs_dict[key] = item[0]
        for key, item in six.iteritems(fs_dict):
            if isinstance(item, list) and len(item) == 1:
                qs_dict[key] = item[0]
        return qs_dict
