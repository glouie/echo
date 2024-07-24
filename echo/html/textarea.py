#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# pylint: disable=too-many-arguments
# pylint: disable=dangerous-default-value
# pylint: disable=locally-disabled

"""
Textarea module
"""

from __future__ import absolute_import
import platform

from selenium.webdriver.common.keys import Keys
from polling import TimeoutException

from html import Element
from html import wait_for_display


class Textarea(Element):

    """
    This is a class to simulate HTML textarea object interactions.

    Tag: <textarea>

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

        :type attributes: string[]
        :param attributes: list of attribute to create property
                           methods for

        :type sub_elements: SubElement[]
        :param sub_elements: list of SubElement objects to attach
                             to this class
        """
        super(Textarea, self).__init__(
            browser, by, value, parent_instance, attributes, sub_elements)

    def clear(self):
        """
        Clears the input and sends the necessary backspaces for windows
        """

        # Send backspaces if we're on windows because IEDriver v3.0.0 and
        # msedgedriver v87 don't clear properly. Don't continue with the super
        # call because selenium will also send the enter key for some reason.
        if platform.system() == 'Windows' and self.value:
            self.send_keys(Keys.BACKSPACE * len(self.value))

        # super objects can't take advantage of the method_missing's
        # __get_attr__ to search for clear, so we force the first layer.
        try:
            super(Textarea, self).clear()
        except AttributeError:
            # AttributeError: 'super' object has no attribute 'clear'
            self.method_missing('clear')()

    @property
    def value(self):
        """
        Gets the value in the value attribute of the textarea object

        :rtype: string
        :return: the value attribute
        """

        return self.get_attribute("value")

    @value.setter
    @wait_for_display
    def value(self, value):
        """
        Sets the value of the textarea object.

        :type value: string
        :param value: the value to set
        """
        # If the value is a string consisting of alphanumeric characters and
        # has a length of more than one, and the SLOW_WEBDRIVER_ENV variable is
        # true, then use the set_value_with_wait() method as the value setter.
        if (self.is_slow_run_enabled() and
                isinstance(value, str) and value.isalnum() and
                len(str(value)) > 1):
            self.set_value_with_wait(value)

        else:
            self.clear()
            self.send_keys(value)

    @wait_for_display
    def set_value_with_wait(
            self, value, key_timeout=3, key_check_frequency=1,
            character_timeout=12):
        """
        Sets the value of the input object and waits between each key. It'll
        try again if a key times out.

        :type value: str
        :param value: the value to set

        :type key_timeout: int
        :param key_timeout: time to spend on each keypress

        :type key_check_frequency: int
        :param key_check_frequency: how often to check the key has been set

        :type character_timeout: int
        :param character_timeout: time to spend on each character. including
            multiple attempts on a keypress
        """

        def check_clear():
            """
            Clears the input and returns wether the clear is empty.

            :return: whether the clear is empty
            :rtype: bool
            """
            self.clear()
            return not self.value

        try:
            self.wait_for_condition(
                check_clear,
                timeout=key_timeout, frequency=key_check_frequency,
                error_message="Failed to wait for clear."
            )
        except TimeoutException:
            self.send_keys(Keys.BACKSPACE * len(self.value))
            self.wait_for_condition(
                lambda: not self.value,
                timeout=key_timeout, frequency=key_check_frequency,
                error_message="Failed to wait for backspaces."
            )

        for idx, key in enumerate(value):
            def send_key_and_wait():
                """
                Sends a key, waits a little, and retries a few times.

                :return: whether a new character has been appended
                :rtype: bool
                """
                self.send_keys(key)
                return self.wait_for_condition(
                    lambda: self.value == value[:idx + 1],
                    timeout=key_timeout, frequency=key_check_frequency,
                )

            self.wait_for_condition(
                send_key_and_wait,
                timeout=character_timeout, frequency=key_timeout,
                ignore_exceptions=TimeoutException,
                error_message=(
                    "Failed to send key, even after retrying a few times")
            )

    @wait_for_display
    def append(self, value):
        """
        Appends to the end of the value that's already in the
        textarea object

        :type value: string
        :param value: the value to append
        """

        self.send_keys(value)


Textarea.generate_attributes_properties(['type', 'name'])
