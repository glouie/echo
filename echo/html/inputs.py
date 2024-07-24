#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# pylint: disable=too-many-arguments
# pylint: disable=dangerous-default-value
# pylint: disable=too-few-public-methods
# pylint: disable=locally-disabled
# pylint: disable=super-on-old-class
# pylint: disable=fixme

"""
Input module
"""

from __future__ import absolute_import
import logging
import platform
import re
import six

from polling import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException

from html import Element
from html import wait_for_display

LOGGER = logging.getLogger(__name__)


class InputType(object):

    """
    Set of supported Input types
    """

    CHECKBOX = 'checkbox'
    DATE = 'date'
    FILE = 'file'
    HIDDEN = 'hidden'
    PASSWORD = 'password'
    RADIO = 'radio'
    RANGE = 'range'
    SUBMIT = 'submit'
    TEXT = 'text'

    @classmethod
    def get_class(cls, input_type):
        """
        Class method to get the Input class for the given type.

        :type input_type: InputType
        :param input_type: the input type to use.

        :rtype: object
        :return: the correct input class
        """

        if cls.is_valid(input_type):
            input_classes = {
                InputType.CHECKBOX: Checkbox,
                InputType.DATE: Date,
                InputType.FILE: File,
                InputType.HIDDEN: Hidden,
                InputType.PASSWORD: Password,
                InputType.RADIO: Radio,
                InputType.RANGE: Range,
                InputType.SUBMIT: Submit,
                InputType.TEXT: Text,
            }
            return input_classes[input_type]
        raise AttributeError(
            "Invalid or unsupported input type. '{}'".format(input_type))

    @classmethod
    def is_valid(cls, input_type):
        """
        Check if the type is a valid type.

        :type input_type: InputType
        :param input_type: an input type

        :rtype: bool
        :return: True if the input_type is valid and False if not
        """

        for attr in dir(cls):
            if input_type == getattr(cls, attr):
                return True
        return False


class Input(Element):

    """
    This is a class to simulate HTML input object interactions.

    Tag: <input>

    Requires a WebDriver or WebDriver like instance passed into it.
    """

    def __init__(
            self, browser, by, value,
            parent_instance=None, attributes=[], sub_elements=[],
            input_type=None):
        """
        Init

        :type browser: selenium.webdriver.remote.webdriver.WebDriver
        :param browser: WebDriver like instance

        :type by: By object from the webdriver common libs
        :param by: By which method is used to locate the webelement

        :type value: str
        :param value: the value of the selector

        :type parent_instance: object
        :param parent_instance: a reference to the parent object.
                                for this to be useful, parent needs a
                                get_element() method that returns its
                                webelement from its parent's instance.

        :type attributes: str []
        :param attributes: list of attribute to create property
                           methods for

        :type sub_elements: SubElement []
        :param sub_elements: list of SubElement objects to attach
                             to this class

        :type input_type: InputType
        :param input_type: the input type to use to create the Input object.
        """

        if (not isinstance(attributes, list) and
           not isinstance(attributes, tuple)):
            raise AttributeError(
                "Expected 'attributes' argument to be of type list or tuple.")

        if input_type is None:
            super(Input, self).__init__(
                browser, by, value, parent_instance, attributes, sub_elements)
        else:
            # TODO: need to find a cleaner way to do this by not having a
            # bad super call.
            # pylint: disable=super-on-old-class
            # pylint: disable=fixme
            cls_type = InputType.get_class(input_type)

            class Temp(cls_type):

                """
                Temporary class to hack the in place switch of class type.
                """

                def __init__(self, *args, **kwargs):
                    """ Temp Init """
                    super(Temp, self).__init__(*args, **kwargs)

            self.__class__ = Temp
            # pylint: disable=bad-super-call
            super(Temp, self).__init__(
                browser, by, value, parent_instance, [], [])

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
            super(Input, self).clear()
        except AttributeError:
            # AttributeError: 'super' object has no attribute 'clear'
            self.method_missing('clear')()

    @property
    def value(self):
        """
        Gets the value in the value attribute of the input object

        :rtype: string
        :return: the value attribute
        """

        return self.get_attribute("value")

    @value.setter
    @wait_for_display
    def value(self, value):
        """
        Sets the value of the input object.

        :type value: str
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
            try:
                self.send_keys(six.text_type(value))
            except WebDriverException as exception:
                exception.msg = (
                    "{}\nvalue setter failed. Try set_value_with_script"
                    "".format(exception.msg))
                raise

    @wait_for_display
    def set_value_with_script(self, value):
        """
        Sets the value of the input object using javascript and triggers a
        change event.

        :type value: str
        :param value: the value to set
        """

        self.clear()
        self.execute_script(
            """
            var nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype,
                "value"
            ).set;
            nativeInputValueSetter.call(arguments[0], '{value}');

            var inputEvent = new Event('input', {bubbles_text});
            arguments[0].dispatchEvent(inputEvent);
            """.format(value=value, bubbles_text='{bubbles: true}')
        )

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
                self.send_keys(six.text_type(key))
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

    def _send_all_keys(self, value):
        """
        There's a known issue for selenium send_keys function that
        selenium won't send special characters "&", "(", "!"
        And here's the workaround for this known issue

        Jira: SPL-81162

        https://code.google.com/p/selenium/issues/detail?id=6074
        http://grokbase.com/t/gg/webdriver/129sthya41/
            web-driver-skips-and-characters-when-using-sendkeys
        """

        special_chars_and_alternative = {
            "&": [Keys.SHIFT, "7"],
            "(": [Keys.SHIFT, "9"],
            "!": [Keys.SHIFT, "1"]
        }
        regex_matching_string = r'(&|\(|!)'

        split_by_special_chars = re.split(regex_matching_string, value)
        for char in split_by_special_chars:
            if char in list(special_chars_and_alternative.keys()):
                self.send_keys(*special_chars_and_alternative[char])
            else:
                self.send_keys(char)


Input.generate_attributes_properties([
    'accept', 'align', 'alt', 'autocomplete', 'autofocus', 'checked',
    'disabled', 'form', 'formaction', 'formenctype', 'formmethod',
    'formnovalidate', 'formtarget', 'height', 'list', 'max',
    'maxlength', 'min', 'multiple', 'name', 'pattern', 'placeholder',
    'readonly', 'required', 'size', 'src', 'step', 'type', 'value',
    'width'])


class Radio(Input):

    """
    This is a class to simulate HTML radio input object interactions.

    Tag: <input[type=radio]>

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
                      the webelement

        :type value: str
        :param value: the value of the selector

        :type parent_instance: object
        :param parent_instance: a reference to the parent object.
                                for this to be useful, parent needs a
                                get_element() method that returns its
                                webelement from its parent's instance

        :type attributes: str []
        :param attributes: list of attribute to create property
                           methods for

        :type sub_elements: SubElement []
        :param sub_elements: list of SubElement objects to attach
                             to this class
        """

        attributes = [] + list(attributes)

        super(Radio, self).__init__(
            browser, by, value, parent_instance, attributes, sub_elements)

    def _get_option_elems(self):
        """
        Get all the option elements of the radio controls.

        :rtype webelement.WebElement[]
        :return list of webelements for each of the options in the radio input.
        """

        return self.browser.find_elements_by_css_selector(
            "input[type=radio][name='{n}']".format(n=self.attr_name))

    @property
    def values(self):
        """
        Gets a list of all the radio input values

        :rtype: string[]
        :return: list of all the value attributes for the radio input
        """

        return [
            elem.get_attribute("value")
            for elem in self._get_option_elems()]

    @property
    @wait_for_display
    def value(self):
        """
        Gets the selected value of the radio input

        :rtype: string
        :return: the value attribute
        """

        elems = self.browser.find_elements_by_css_selector(
            "input[type=radio][name='{n}']:checked".format(n=self.attr_name))
        if elems:
            return elems[0].get_attribute("value")
        return None

    # pylint: disable=arguments-differ
    @value.setter
    @wait_for_display
    def value(self, value):
        """
        Clicks on the radio input of the give value

        :type value: str
        :param value: the value to set
        """

        input_elem = self.browser.find_element_by_css_selector(
            "input[type=radio][name='{n}'][value='{v}']".format(
                n=self.attr_name, v=value))

        label_elems = self.browser.find_elements_by_css_selector(
            "label[for='{id}']".format(id=input_elem.attr_id))

        if label_elems:
            if len(label_elems) > 1:
                LOGGER.warn(
                    'More than one label are associated with the radio '
                    'input with id={id}'.format(id=input_elem.attr_id))
            label_elems[0].click()
        else:
            input_elem.click()

    @property
    def options(self):
        """
        Gets a list of all the radio input options

        :rtype: string[]
        :return: list of all the option attributes for the radio input
        """

        return [elem.text.strip() for elem in self._get_option_elems()]

    @property
    @wait_for_display
    def option(self):
        """
        Gets the selected option of the radio input

        :rtype: string
        :return: the option attribute
        """

        elems = self.browser.find_elements_by_css_selector(
            "input[type=radio][name='{n}']:checked".format(n=self.attr_name))
        if elems and elems[0].is_displayed():
            return elems[0].text.strip()
        return None

    @option.setter
    @wait_for_display
    def option(self, option):
        """
        Clicks on the radio input of the give option

        :type option: string
        :param option: the option to set
        """
        elems = self._get_option_elems()
        for elem in elems:
            label_elems = self.browser.find_elements_by_css_selector(
                'label[for="{}"]'.format(elem.attr_id))
            # first check the input text value if not lookup by the label
            if ((elem.text.strip() == option) or
                    (label_elems and label_elems[0].is_displayed() and
                     label_elems[0].text.strip() == option)):
                elem.click()
                return None
        raise AttributeError(
            'Can not find the option with the text "{}"'
            ''.format(option))

    @property
    def labels(self):
        """
        Gets a list of all the radio input labels

        :rtype: string[]
        :return: list of all the label attributes for the radio input
        """

        ids = [elem.attr_id for elem in self._get_option_elems()]
        label_elems = [self.browser.find_elements_by_css_selector(
            'label[for="{}"]'.format(id_val)) for id_val in ids]
        return [elems[0].text.strip()
                for elems in label_elems
                if elems and elems[0].is_displayed()]

    @property
    @wait_for_display
    def label(self):
        """
        Gets the selected label of the radio input

        :rtype: string
        :return: the option attribute
        """

        elems = self.browser.find_elements_by_css_selector(
            "input[type=radio][name='{n}']:checked".format(n=self.attr_name))
        if elems:
            id_val = elems[0].attr_id
            label_elems = self.browser.find_elements_by_css_selector(
                "label[for='{}']".format(id_val))
            if label_elems:
                return label_elems[0].text.strip()
            raise AttributeError(
                "Can not find a label for this input using the id '{}'"
                "".format(id_val))
        return None


class Checkbox(Input):

    """
    This is a class to simulate HTML checkbox input object interactions.

    Tag: <input[type=checkbox]>

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
                      the webelement

        :type value: str
        :param value: the value of the selector

        :type parent_instance: object
        :param parent_instance: a reference to the parent object.
                                for this to be useful, parent needs a
                                get_element() method that returns its
                                webelement from its parent's instance

        :type attributes: str []
        :param attributes: list of attribute to create property
                           methods for

        :type sub_elements: SubElement []
        :param sub_elements: list of SubElement objects to attach
                             to this class
        """

        attributes = [] + list(attributes)

        super(Checkbox, self).__init__(
            browser, by, value, parent_instance, attributes, sub_elements)

    @wait_for_display
    def is_checked(self):
        """
        Returns True or False if the checkbox is checked or not.

        :rtype: boolean
        :return: True if the checkbox is checked and False otherwise
        """

        return self.is_selected()

    @wait_for_display
    def _set_value(self, value):
        """
        Checks or unchecks the checkbox

        :type value: boolean
        :param value: True to check the checkbox and False to uncheck.
        """

        if value:
            self.check()
        else:
            self.uncheck()

    def check(self):
        """
        Checks the checkbox if it's not checked.
        """

        if not self.value:
            self.element.click()

    def uncheck(self):
        """
        Unchecks the checkbox if it's not checked.
        """

        if self.value:
            self.element.click()

    value = property(is_checked, _set_value)


class Date(Input):

    """
    This is a class to simulate HTML date input object interactions.

    Tag: <input[type=date]>

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
                      the webelement

        :type value: str
        :param value: the value of the selector

        :type parent_instance: object
        :param parent_instance: a reference to the parent object.
                                for this to be useful, parent needs a
                                get_element() method that returns its
                                webelement from its parent's instance

        :type attributes: str []
        :param attributes: list of attribute to create property
                           methods for

        :type sub_elements: SubElement []
        :param sub_elements: list of SubElement objects to attach
                             to this class
        """

        attributes = [] + list(attributes)

        super(Date, self).__init__(
            browser, by, value, parent_instance, attributes, sub_elements)


class File(Input):

    """
    This is a class to simulate HTML file input object interactions.

    Tag: <input[type=hidden]>

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
                      the webelement

        :type value: str
        :param value: the value of the selector

        :type parent_instance: object
        :param parent_instance: a reference to the parent object.
                                for this to be useful, parent needs a
                                get_element() method that returns its
                                webelement from its parent's instance

        :type attributes: str []
        :param attributes: list of attribute to create property
                           methods for

        :type sub_elements: SubElement []
        :param sub_elements: list of SubElement objects to attach
                             to this class
        """

        attributes = [] + list(attributes)

        super(File, self).__init__(
            browser, by, value, parent_instance, attributes, sub_elements)

    @property
    def value(self):
        """
        Gets the value in the value attribute of the input object

        :rtype: string
        :return: the value attribute
        """

        return self.get_attribute("value")

    # pylint: disable=arguments-differ
    @value.setter
    @wait_for_display
    def value(self, value):
        """
        Sets the value of the input object

        :type value: str
        :param value: the value to set
        """

        self.send_keys(value)

    def select_file(self, file_path):
        """
        Selects a file by inserting the file path into the input.

        :type file_path: string
        :param file_path: the full path to the file.
        """

        self.value = file_path


class Hidden(Input):

    """
    This is a class to simulate HTML hidden input object interactions.

    Tag: <input[type=hidden]>

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
                      the webelement

        :type value: str
        :param value: the value of the selector

        :type parent_instance: object
        :param parent_instance: a reference to the parent object.
                                for this to be useful, parent needs a
                                get_element() method that returns its
                                webelement from its parent's instance

        :type attributes: str []
        :param attributes: list of attribute to create property
                           methods for

        :type sub_elements: SubElement []
        :param sub_elements: list of SubElement objects to attach
                             to this class
        """

        attributes = [] + list(attributes)

        super(Hidden, self).__init__(
            browser, by, value, parent_instance, attributes, sub_elements)

        # Hidden input is invisible and is_displayed() always returns False
        self.check_display = False


class Text(Input):

    """
    This is a class to simulate HTML text input object interactions.

    Tag: <input[type=text]>

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
                      the webelement

        :type value: str
        :param value: the value of the selector

        :type parent_instance: object
        :param parent_instance: a reference to the parent object.
                                for this to be useful, parent needs a
                                get_element() method that returns its
                                webelement from its parent's instance

        :type attributes: str []
        :param attributes: list of attribute to create property
                           methods for

        :type sub_elements: SubElement []
        :param sub_elements: list of SubElement objects to attach
                             to this class
        """

        if (not isinstance(attributes, list) and
           not isinstance(attributes, tuple)):
            raise AttributeError(
                "Expected 'attributes' argument to be of type list or tuple.")

        attributes = [] + list(attributes) + list(attributes)

        super(Text, self).__init__(
            browser, by, value, parent_instance, attributes, sub_elements)

    @wait_for_display
    def append(self, value):
        """
        Appends to the end of the value that's already in the
        input object

        :type value: str
        :param value: the value to put into the input object.
        """

        self._send_all_keys(six.text_type(value))


class Password(Text):

    """
    This is a class to simulate HTML password input object
    interactions.

    Tag: <input[type=password]>

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
                      the webelement

        :type value: str
        :param value: the value of the selector

        :type parent_instance: object
        :param parent_instance: a reference to the parent object.
                                for this to be useful, parent needs a
                                get_element() method that returns its
                                webelement from its parent's instance

        :type attributes: str []
        :param attributes: list of attribute to create property
                           methods for

        :type sub_elements: SubElement []
        :param sub_elements: list of SubElement objects to attach
                             to this class
        """

        attributes = ["placeholder"] + list(attributes)

        super(Password, self).__init__(
            browser, by, value, parent_instance, attributes, sub_elements)


class Range(Input):

    """
    This is a class to simulate HTML range input object interactions.

    Tag: <input[type=range]>

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
                      the webelement

        :type value: str
        :param value: the value of the selector

        :type parent_instance: object
        :param parent_instance: a reference to the parent object.
                                for this to be useful, parent needs a
                                get_element() method that returns its
                                webelement from its parent's instance

        :type attributes: str []
        :param attributes: list of attribute to create property
                           methods for

        :type sub_elements: SubElement []
        :param sub_elements: list of SubElement objects to attach
                             to this class
        """
        attributes = ['min', 'max', 'step']

        super(Range, self).__init__(
            browser, by, value, parent_instance, attributes, sub_elements)


class Submit(Input):

    """
    This is a class to simulate HTML submit input object interactions.

    Tag: <input[type=submit]>

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
                      the webelement

        :type value: str
        :param value: the value of the selector

        :type parent_instance: object
        :param parent_instance: a reference to the parent object.
                                for this to be useful, parent needs a
                                get_element() method that returns its
                                webelement from its parent's instance

        :type attributes: str []
        :param attributes: list of attribute to create property
                           methods for

        :type sub_elements: SubElement []
        :param sub_elements: list of SubElement objects to attach
                             to this class
        """

        attributes = [] + list(attributes)

        super(Submit, self).__init__(
            browser, by, value, parent_instance, attributes, sub_elements)
