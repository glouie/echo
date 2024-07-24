#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# pylint: disable=locally-disabled
# pylint: disable=too-many-arguments
# pylint: disable=dangerous-default-value
# pylint: disable=too-many-lines
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-public-methods
# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods
# pylint: disable=nonstandard-exception
# pylint: disable=protected-access


"""
These are the base fundamental classes for all the html objects.

Classes: WebElementWrapper, Element, SubElement, SubElements,
         ElementType

:Authors: glouie
"""

from __future__ import absolute_import

import contextlib
import logging
import os
import re
from abc import abstractmethod
from functools import partial
from html.method_missing import MethodMissing
from html.support import mouse, size

from selenium.common.exceptions import (NoSuchElementException,
                                        StaleElementReferenceException,
                                        WebDriverException)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebElement
from selenium.webdriver.support import color
from selenium.webdriver.support.expected_conditions import \
    element_to_be_clickable

LOGGER = logging.getLogger(__name__)
TIMEOUT = 60  # 60 seconds for default timeout
DEBUG = False  # used only for _debug_log()
global SLOW_WEBDRIVER_ENV
SLOW_WEBDRIVER_ENV = (
    False if os.environ.get(
        'SLOW_WEBDRIVER_ENV', 'false').strip().lower() in ['false', '0']
    else True)


def _debug_log(*msg):
    """
    Outputs debug log only when the DEBUG flag is set.
    """

    if LOGGER.getEffectiveLevel() == logging.DEBUG and DEBUG:
        # print msg
        LOGGER.debug(*msg)


class InvalidScriptException(WebDriverException):
    """
    Exception to handle invalid script exceptions

    """
    pass


def _normalize_attribute_name(name, replace_char='_'):
    """
    Normalize name, and convert camelcase to underscores

    :type name: str
    :param name: the specified name

    :type replace_char: str
    :param replace_char: the char to be replaced with

    :rtype: str
    :return: normalized name
    """
    chars_to_replace = r'[-* ]'

    first_cap_re = re.compile('(.)([A-Z][a-z]+)')
    all_cap_re = re.compile('([a-z0-9])([A-Z])')

    replace_char_string = re.sub(chars_to_replace, replace_char, name.strip())
    first_cap_string = first_cap_re.sub(r'\1_\2', replace_char_string)
    underscore_name = all_cap_re.sub(r'\1_\2', first_cap_string).lower()

    return underscore_name


def wait_for_display(func):
    """
    Decorator for specifying methods that should wait or
    not wait for the element to be visible.

    Only works with the Element objects.

    :type func: method
    :param func: the method to run after we check for display

    :return: return value of the function call
    """

    def _decorator(self, *args, **kwargs):
        """
        Waits for the element to be displayed if check_display is True

        """
        _debug_log('-- wait_for_display -- %s', self)
        if self.check_display:
            self.wait_to_be_displayed()
        return func(self, *args, **kwargs)

    return _decorator


class ElementType(type):
    """
    This is a metaclass that all the object that wraps a webelement
    or element should have.

    """

    @abstractmethod
    def get_element(cls):
        """
        This should return a Element object.

        Returns:
            Element
        """


class WebElementWrapper(MethodMissing):
    """
    Wraps the WebElement into a simple class to use as a parent object
    """

    def __init__(self, webelement):
        """
        Init

        :type webelement:
            selenium.webdriver.remote.webelement.WebElement
        :param webelement: WebElement that is being wrapped.

        """
        super(WebElementWrapper, self).__init__()

        self._element = webelement
        self._by = None
        self._value = None
        self._parent_instance = None
        self._attributes = []
        self._sub_elements = []
        self.browser = webelement.parent
        self.id = webelement.id

    # pylint: disable=unused-argument
    def method_missing(self, attr, *args, **kwords):
        """
        Dispatch incoming messages to selenium and do our
        custom logging.

        Raises AttributeError if the attribute is unknown or
        an Exception if another problem occurs.

        """
        if hasattr(self._element, attr):
            return getattr(self._element, attr)
        else:
            raise AttributeError(
                "WebElement does not respond to '{a}'.".format(a=attr))

    def get_element(self):
        """
        Return the WebElement

        :rtype:
            selenium.webdriver.remote.webelement.WebElement
        :return: returns the WebElement using at init.
        """
        return self._element

    element = property(get_element)


class SubElement(object):
    """
    SubElement objects help facilitates the ability to add nested
    Elements in our Element
    """

    def __init__(
            self, name, element_class, browser, by, value,
            parent_instance=None, attributes=[], sub_elements=[],
            *args, **kwargs):
        """
        Init

        :type name: str
        :param name: the name of that attribute used to
                     reference the object.

        :type browser: selenium.webdriver.remote.webelement.WebDriver
        :param browser: WebDriver object like instance

        :type by: selenium.webdriver.common.by.By
        :param by: by which selector method is used to
                   locate the WebElement

        :type value: str
        :param value: the value of the selector

        :type parent_instance: object
        :param parent_instance: a reference to the parent object.
                                for this to be useful, parent needs a
                                get_element() method that returns its
                                WebElement from its parent's instance

        :type attributes: str[]
        :param attributes: list of attribute to create property
                           methods for

        :type sub_elements: SubElement []
        :param sub_elements: list of SubElement objects to attach
                            to this class

        :type args: tuple
        :param args: the args list of the element_class

        :type kwargs: dict
        :param kwargs: the dictionary or key value pairs for
                       the args going into the element_class

        """

        self.name = name
        self.element_class = element_class
        self.browser = browser
        self.by = by
        self.value = value
        self.parent_instance = parent_instance
        self.attributes = attributes
        self.sub_elements = sub_elements
        self.args = args
        self.kwargs = kwargs


class SubElements(object):
    """
    SubElements object help facilitates the ability to add nested
    method to get a list of elements of different types.
    """

    def __init__(
            self, name, element_class, browser, by, value,
            parent_instance=None, attributes=[], sub_elements=[],
            *args, **kwargs):
        """
        Init

        :type name: string
        :param name: the name of the method

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

        :type attributes: str[]
        :param attributes: list of attribute to create property
                           methods for

        :type sub_elements: SubElement []
        :param sub_elements: list of SubElement objects to attach
                             to this class.

        :type args: tuple
        :param args: the args list of the element_class

        :type kwargs: dict
        :param kwargs: the dictionary or key value pairs for the
                       args going into the element_class

        """

        self.name = name
        self.element_class = element_class
        self.browser = browser
        self.value = value
        self.by = by
        self.value = value
        self.parent_instance = parent_instance
        self.attributes = attributes
        self.sub_elements = sub_elements
        self.args = args
        self.kwargs = kwargs


class partialmethod(partial):
    # pylint: disable=no-init
    # pylint: disable=no-member

    """
    Provides the partial method feature like functools.partialmethod in 3.4
    https://gist.github.com/carymrobbins/8940382

    """

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return partial(self.func, instance,
                       *(self.args or ()), **(self.keywords or {}))


class Element(MethodMissing):
    """
    Base HTML element object that represents an html tag element.
    """

    def __init__(
            self, browser, by, value, parent_instance=None,
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

        :type attributes: str[]
        :param attributes: list of attribute to create property
                           methods for

        :type sub_elements: SubElement []
        :param sub_elements: list of SubElement objects to attach
                             to this class
        """

        super(Element, self).__init__()
        self.browser = browser
        self._by = by
        self._value = value
        self._parent_instance = parent_instance
        self._attributes = attributes
        self._sub_elements = sub_elements
        self._element = None
        self._check_display = True
        self._mouse_helper = mouse.Mouse(self)
        self._id = None

        if type(attributes) not in (list, tuple):
            raise AttributeError(
                "Expected 'attributes' argument to be of "
                "type list or tuple.")

        if type(sub_elements) not in (list, tuple):
            raise AttributeError(
                "Expected 'subelements' argument to be of "
                "type list or tuple.")

        if self.browser is not None:
            self.timeout = self.browser.timeout
            self.poll_frequency = self.browser.poll_frequency

        self.__class__.generate_attributes_properties(attributes)

        for sub_elem in sub_elements:

            if isinstance(sub_elem, SubElement):

                # This is VERY important in order to keep the hierarchy
                # Note: purposely setting it to None will not work
                #       and you should think long and hard why you
                #       would ever need a "sub" element have a
                #       parent_instance to be None.
                parent_inst = sub_elem.parent_instance or self

                self.__setattr__(
                    sub_elem.name,
                    sub_elem.element_class(
                        browser=sub_elem.browser,
                        by=sub_elem.by,
                        value=sub_elem.value,
                        parent_instance=parent_inst,
                        attributes=sub_elem.attributes,
                        sub_elements=sub_elem.sub_elements,
                        *sub_elem.args, **sub_elem.kwargs))

            elif isinstance(sub_elem, SubElements):

                def gen_get_method(sub_elements):
                    """
                    Generate the method to get a list of the objects

                    :type sub_elements: SubElements
                    :param sub_elements: the specified SubElements object
                    :rtype: Function
                    :return: the generated get method
                    """

                    def get_method():
                        """
                        Method to get a list of the objects

                        :rtype: element_class[]
                        :return: list of all the element class object
                                matching the selector.
                        """

                        parent_inst = sub_elem.parent_instance or self
                        elems = parent_inst.find_elements(
                            sub_elements.by, sub_elements.value)

                        return sub_elements.element_class.init_with_elements(
                            elements=elems,
                            parent_instance=parent_inst,
                            attributes=sub_elements.attributes,
                            sub_elements=sub_elements.sub_elements,
                            *sub_elements.args, **sub_elements.kwargs)

                    return get_method

                self.__setattr__(sub_elem.name, gen_get_method(sub_elem))

            else:
                raise ValueError(
                    "The sub_elements param must be of type "
                    "SubElement or SubElements.")

    @property
    def id(self):  # pylint: disable=invalid-name
        """
        Cache the webelement's id if we fetch for it.

        :rtype: string
        :return: the _webelement's id
        """
        old_id = self._id
        new_id = self._webelement.id

        if old_id is None:
            self._id = new_id
        elif old_id != new_id:
            self._id = new_id
            raise StaleElementReferenceException(
                "Got a new _webelement.id {new} the old element "
                "{old} was stale.".format(new=new_id, old=old_id))

        return new_id

    @id.setter
    def id(self, value):  # pylint: disable=invalid-name
        """
        Set the cached _id value.

        :type value: string
        :param value: the id value to set the _id to.
        """
        self._id = value

    def _check_driver_prop_and_set(self, name, default):
        """
        Check the driver for the property and if driver has it, use it.
        If driver does not have it, then set the default.

        NOTE: Driver property takes precedence over the default value.

        :type name: string
        :param name: name of the property to check and set.

        :type default: object
        :param default: the default value to set if not found
                        in the driver
        """
        if name in self.browser.__dict__:
            self.__setattr__(name, getattr(self.browser, name))
        else:
            self.__setattr__(name, default)

    @property
    def check_display(self):
        """
        Property to get the underling _check_display flag, also looking
        through the _parent_instance to see that it's all consistent

        :rtype: boolean
        :return: True if and only if the _check_display flag is True
                 and all it's ancestor's _check_display flag is True too.
        """

        if not self._check_display:
            return False
        elif self._parent_instance is None:
            return self._check_display
        else:
            return self._parent_instance.check_display

    @check_display.setter
    def check_display(self, value):
        """
        Setter for the check_display property.

        :type value: boolean
        :param value: the boolean value to set the _check_display flag.
        """

        self._check_display = value

    @contextlib.contextmanager
    def ignore_display(self):
        """
        Context manager to allow execution of code while the _check_display
        is set to False, and sets it back to True when the code
        execution is complete.

        ex:

            with self.ignore_display():
                # will get the text value of the _webelement even if
                # the DOM is not displayed
                self.text

        """
        original = self._check_display
        self._check_display = False
        try:
            yield
        finally:
            self._check_display = original

    @classmethod
    def init_with_element(
            cls, element, parent_instance=None,
            attributes=(), sub_elements=(), *args, **kwargs):
        """
        Returns an instance of Element reusing the element.

        :type element: Element
        :param element: the web element to init with

        :type parent_instance: Element
        :param parent_instance: the parent instance

        :type attributes: str[]
        :param attributes: list of attribute to create property
                           methods for

        :type sub_elements: SubElement []
        :param sub_elements: list of SubElement objects to attach
                             to this class

        :rtype: Element
        :return: Element object wrapping the element
        """

        elem = cls(
            browser=element.browser, by=None, value=None,
            parent_instance=parent_instance,
            attributes=attributes, sub_elements=sub_elements,
            *args, **kwargs)
        elem._element = element
        return elem

    @classmethod
    def init_with_elements(
            cls, elements, parent_instance=None,
            attributes=(), sub_elements=(), *args, **kwargs):
        """
        Returns a list of Elements reusing the elements.

        :type elements: Element[]
        :param elements: the web elements to init with

        :type parent_instance: Element
        :param parent_instance: the parent instance

        :type attributes: str[]
        :param attributes: list of attribute to create property
                           methods for

        :type sub_elements: SubElement []
        :param sub_elements: list of SubElement objects to attach
                             to this class

        :rtype: Element []
        :return: a list of Element objects wrapping the
                 elements
        """

        temp_elems = []

        for element in elements:
            temp_elem = cls.init_with_element(
                element, parent_instance=parent_instance,
                attributes=attributes, sub_elements=sub_elements,
                *args, **kwargs)
            temp_elems.append(temp_elem)

        return temp_elems

    # pylint: disable=unused-argument
    def method_missing(self, attr, *args, **kwords):
        """
        Dispatch incoming messages to selenium and do our
        custom logging.

        Raises AttributeError if the attribute is unknown or
        an Exception if another problem occurs.

        """
        # don't use self.element here, as self.element will trigger the
        # function __getattr__, which calls this function if self.get_element()
        # throws AttributeError, it causes RecursionError
        element = self.get_element()
        if hasattr(element, attr):
            return getattr(element, attr)
        else:
            raise AttributeError(
                "WebElement does not respond to '{a}'.".format(a=attr))

    @classmethod
    def generate_attributes_properties(cls, attributes):
        """
        Generates class properties for the specified
        element attributes.


        :type attributes: list or tuple
        :param attributes: the element attributes to
                           generate properties
        """

        for elem_attribute in attributes:
            attr_name = 'attr_{}'.format(
                _normalize_attribute_name(elem_attribute))
            if not hasattr(cls, attr_name):
                setattr(
                    cls, attr_name,
                    cls._generate_attribute_property(elem_attribute))

    @staticmethod
    def _generate_attribute_property(attribute):
        """
        Generates property for the specified element attribute.

        :type attribute: str
        :param attribute: the attribute name to generate a property

        :rtype: property
        :return: the property object for the element attribute
        """

        def template(self):
            """
            Get the attribute '{attr}'

            :rtype: str
            :return: None if attribute is not there, otherwise the
                     value of the '{attr}' attribute.
            """.format(attr=attribute)

            return self.get_attribute(attribute)

        return property(template)

    @property
    def driver(self):
        """
        Returns the webdriver like instance.

        :rtype: selenium.webdriver.remote.webdriver.WebDriver
        :return: WebDriver like instance being used to run
                 webdriver commands
        """

        return self.browser

    @property
    @wait_for_display
    def mouse(self):
        """
        Returns mouse helper

        :rtype: Mouse
        :return: the Mouse support object that handles mouse interactions
        """
        return self._mouse_helper

    @property
    def size(self):
        """
        Returns size helper

        :rtype: Size
        :return: the size support object that prvoides functionalities to size
        """
        elem_size = self._webelement.size
        return size.Size(elem_size)

    @staticmethod
    def _is_element_stale(element):
        """
        Returns True if the specified element is stale

        :type element: Element/WebElement
        :param element: the specified element
        """
        _debug_log('checking if element is stale -- %s', element)
        try:
            if isinstance(element, Element):
                with element.ignore_display():
                    element.get_attribute('*')
            else:
                element.get_attribute('*')
        except (StaleElementReferenceException, NoSuchElementException):
            if isinstance(element, Element):
                element._element = None
                element.id = None
            return True
        else:
            return False

    def get_element(self):
        """
        Gets the element og this instance

        :rtype: Element/WebElement
        :return: element of this instance
        """
        _debug_log("inside get_element for %s", self)

        _self__element = self._element

        if (_self__element is not None and
                not self._is_element_stale(_self__element)):
            _debug_log("    _element is None and not stale")
            return _self__element
        else:
            _debug_log("    set _element to None")
            self._element = None
            self._id = None

        _self__by = self._by
        _self__value = self._value

        if _self__by is None or _self__value is None:
            _debug_log("    _by or _value is None")
            raise StaleElementReferenceException(
                'The attached web element is stale. Please init with '
                'valid web element again.')

        if ('_parent_instance' in self.__dict__ and
                self._parent_instance is not None and
                hasattr(self._parent_instance, 'get_element')):
            _debug_log(
                "    _parent_instance is not None and has get_element")
            parent_elem = self._parent_instance.get_element()
            _elem = parent_elem.find_element(
                by=_self__by, value=_self__value)
            _elem._check_display = self._check_display
            self._element = _elem
            self._id = _elem.id
            return _elem

        if 'browser' in self.__dict__:
            _debug_log(
                "    finding element by %s with %s", _self__by, _self__value)
            _elem = self.browser.find_element(
                by=_self__by, value=_self__value)
            _elem._check_display = self._check_display
            self._element = _elem
            self._id = _elem.id
            return _elem

    def _get_element_wrapper(self):
        """
        Wrapper for getting the webelement for static binding of
        element property
        """
        return self.get_element()

    element = property(_get_element_wrapper)

    def wait_for_condition(
            self, method, method_args=[], timeout=None, frequency=None,
            error_message=None, ignore_exceptions=()):
        """
        Waits for an arbitrary condition to be true.

        :type method: method
        :param method: the method to use to poll with.

        :type method_args: list of method arguments
        :param method_args: the list of method arguments to pass
                            into the method.

        :type timeout: int
        :param timeout: Number for seconds to wait before giving up

        :type frequency: int
        :param frequency: Number for seconds to wait before
                          polling again

        :type error_message: string
        :param error_message: the error message to display when
                              the condition is not met before the
                              timeout

        :type ignore_exceptions: tuple or Exception
        :param ignore_exceptions: You can specify a tuple of exceptions or
        single exception that should be caught and ignored on every iteration.
        If the target function raises one of these exceptions, it will be
        caught and the exception instance will be pushed to the queue of values
        collected during polling. Any other exceptions raised will be
        raised as normal.
        """

        local_timeout = timeout or self.timeout
        local_freq = frequency or self.poll_frequency

        return self.browser.wait_for_condition(
            method, method_args, ignore_exceptions=ignore_exceptions,
            timeout=local_timeout, frequency=local_freq,
            error_message=error_message)

    def wait_to_be_displayed(
            self, timeout=None, frequency=None, refresh=False):
        """
        Waits for this object to be displayed up to the timeout amount.

        :type timeout:  int
        :param timeout: Number for seconds to wait total

        :type frequency:  int
        :param frequency: Number for seconds to wait before
                          polling again

        :type refresh: bool
        :param refresh: True to fresh page for every poll,
                        and False to not
                        Default: False
        """

        local_timeout = timeout or self.timeout
        local_freq = frequency or self.poll_frequency

        def wait_condition():
            """
            Wait condition to satisfy this specific wait method

            :rtype: bool
            :return: True if element is displayed and False if not
            """

            if refresh:
                self.browser.refresh()

            if self._by is None or self._value is None:
                return self._webelement.is_displayed()
            else:
                return self.is_displayed()

        self.wait_for_condition(
            wait_condition, timeout=local_timeout,
            frequency=local_freq,
            error_message=(
                "Unable to find element '{elem}' by '{by}'."
                "".format(elem=self._value, by=self._by)))

    def wait_to_not_be_displayed(
            self, timeout=None, frequency=None, refresh=False):
        """
        Waits for an element to not be displayed on a page.

        It can wait for an element not displayed using the by,
        value selector starting from a webelement, with the specified
        timeout and polling frequency, and with page refreshing on
        every poll.

        :type timeout:  int
        :param timeout: Number for seconds to wait total

        :type frequency:  int
        :param frequency: Number for seconds to wait before
                          polling again

        :type refresh:  bool
        :param refresh: True to fresh page for every poll,
                        and False to not
                        Default: False

        """

        local_timeout = timeout or self.timeout
        local_freq = frequency or self.poll_frequency

        def wait_condition():
            """Wait condition to satisfy this specific wait method"""
            if refresh:
                self.browser.refresh()
            return not self.is_displayed()

        self.wait_for_condition(
            wait_condition, timeout=local_timeout, frequency=local_freq,
            error_message=(
                "Still able to find element '{elem}' by '{by}'."
                "".format(elem=self._value, by=self._by)))

    def wait_to_be_present(
            self, timeout=None, frequency=None, refresh=False):
        """
        Waits for an element to be present on a page.

        It can wait for an element present using the by, value selector
        starting from a webelement, with the specified timeout and
        polling frequency, and with page refreshing on every poll.

        :type timeout:  int
        :param timeout: Number for seconds to wait total

        :type frequency:  int
        :param frequency: Number for seconds to wait before
                          polling again

        :type refresh:  bool
        :param refresh: True to fresh page for every poll,
                        and False to not
                        Default: False

        """

        local_timeout = timeout or self.timeout
        local_freq = frequency or self.poll_frequency

        def wait_condition():
            """Wait condition to satisfy this specific wait method"""

            if refresh:
                self.browser.refresh()
            return self.is_present()

        self.wait_for_condition(
            wait_condition, timeout=local_timeout, frequency=local_freq,
            error_message=(
                "Unable to find element '{elem}' by '{by}'."
                "".format(elem=self._value, by=self._by)))

    def wait_to_not_be_present(
            self, timeout=None, frequency=None, refresh=False):
        """
        Waits for an element to not be present on a page.

        It can wait for an element not present using the by,
        value selector starting from a webelement, with the specified
        timeout and polling frequency, and with page refreshing on
        every poll.

        :type timeout:  int
        :param timeout: Number for seconds to wait total

        :type frequency:  int
        :param frequency: Number for seconds to wait before
                          polling again

        :type refresh:  bool
        :param refresh: True to fresh page for every poll,
                        and False to not
                        Default: False

        """

        local_timeout = timeout or self.timeout
        local_freq = frequency or self.poll_frequency

        def wait_condition():
            """Wait condition to satisfy this specific wait method"""
            if refresh:
                self.browser.refresh()
            return not self.is_present()

        self.wait_for_condition(
            wait_condition, timeout=local_timeout, frequency=local_freq,
            error_message=(
                "Still able to find element '{elem}' by '{by}'."
                "".format(elem=self._value, by=self._by)))

    def wait_to_be_stale(self, timeout=None, frequency=None):
        """
        Wait for the element to be stale.

        :type timeout:  int
        :param timeout: Number for seconds to wait total

        :type frequency:  int
        :param frequency: Number for seconds to wait before
                          polling again

        """
        local_timeout = timeout or self.timeout
        local_freq = frequency or self.poll_frequency

        # First check to see if it's not already stale or not there.
        # We need to use the webelement's get attribute so that it will
        # not require our element to be visible.
        _debug_log('waiting for this to stale: %s', self)
        try:
            old_id = None
            if self._element is not None:
                old_id = self._element.id

            webelement = self._webelement

            _debug_log('    current _webelement: %s', self.id)

            # first check to see if the _webelement.id is the same or not
            # if it's not the same then assume we are stale.
            if old_id != webelement.id:
                return None
        except (StaleElementReferenceException, NoSuchElementException):
            return None

        def wait_condition():
            """
            Helper method to attempt to get an attribute off
            the webelement.

            If we are successful in getting the attribute,
            then return False otherwise we would return True.

            :rtype: bool
            :return: True if element is stale and False if not.
            """

            try:
                webelement.get_attribute('*')
            except (StaleElementReferenceException, NoSuchElementException):
                return True
            return False

        msg = ("Element still not stale after {time} second(s) "
               "with a {freq} second(s) polling interval."
               "".format(time=local_timeout, freq=local_freq))

        self.wait_for_condition(
            wait_condition, timeout=local_timeout, frequency=local_freq,
            error_message=msg)

    @property
    def _webelement(self):
        """
        Get the webelement

        :rtype: WebElement
        :return: the core WebElement of this object.
        """
        _debug_log("looking for _webelement: %s", self)
        if isinstance(self, WebElement):
            return self
        elif isinstance(type(self).element, property):
            welem = self.element
            while not isinstance(welem, WebElement):
                welem = welem.element
            return welem
        else:
            raise WebDriverException(
                'WebElement root is not found in this object.')

    def is_displayed(self):
        """
        Returns True if the element is present and displayed and false
        if it's not found or displayed.

        :rtype: bool
        :return: True if object is displayed and false otherwise.
        """
        try:
            return self._webelement.is_displayed()
        except NoSuchElementException:
            return False
        except StaleElementReferenceException:
            return False
        except WebDriverException:
            return False

    def is_disabled(self):
        """
        Check to see if the element is in a disabled state.

        :rytpe: boolean
        :return: True if the button is in an disabled state
                 and False if not.
        """

        return not self.is_enabled()

    def wait_to_be_enabled(self, timeout=None, frequency=None):
        """
        Wait for the element to be in a enabled state.

        :type timeout:  int
        :param timeout: Number for seconds to wait total

        :type frequency:  int
        :param frequency: Number for seconds to wait before
                          polling again
        """
        local_timeout = timeout or self.timeout
        local_freq = frequency or self.poll_frequency
        self.wait_for_condition(
            self.is_enabled,
            timeout=local_timeout, frequency=local_freq,
            error_message="Failed to wait for element enabled"
        )

    def wait_to_be_clickable(self, timeout=None, frequency=None):
        """
        Wait for the element to be clickable
        (visible in the clickable area and enabled)

        :type timeout:  int
        :param timeout: Number for seconds to wait total

        :type frequency:  int
        :param frequency: Number for seconds to wait before
                          polling again
        """
        local_timeout = timeout or self.timeout
        local_freq = frequency or self.poll_frequency
        self.wait_for_condition(
            element_to_be_clickable([self._by, self._value]),
            method_args=[self.browser],
            timeout=local_timeout, frequency=local_freq,
            error_message="Failed to wait for element to be clickable"
        )

    def wait_to_be_disabled(self, timeout=None, frequency=None):
        """
        Wait for the element to be in a disabled state.

        :type timeout:  int
        :param timeout: Number for seconds to wait total

        :type frequency:  int
        :param frequency: Number for seconds to wait before
                          polling again
        """
        local_timeout = timeout or self.timeout
        local_freq = frequency or self.poll_frequency
        self.wait_for_condition(
            self.is_disabled,
            timeout=local_timeout, frequency=local_freq,
            error_message="Failed to wait for element disabled"
        )

    def is_present(self):
        """
        Returns True if the element is present and False
        if it's not found

        :rtype: bool
        :return: True if object is present and false otherwise.
        """
        try:
            self.get_element()
        except (NoSuchElementException, StaleElementReferenceException):
            return False
        else:
            return True

    def execute_script(self, script):
        """
        Execute a script on this element.

        :type script: string
        :param script: the javascript string to execute.

        :rtype: str
        :return: the return value from executing the javascript
                 string on this element.
        """
        if 'arguments[0]' not in script:
            raise InvalidScriptException(
                "Expecting webelement arguments to be used in script:"
                "\n{}\n".format(script))

        return self.browser.execute_script(script, self._webelement)

    def execute_async_script(self, script):
        """
        Execute an asynchronous script on this element.

        :type script: string
        :param script: the javascript string to execute.

        :rtype: str
        :return: the return value from executing the javascript
                 string on this element.
        """
        if 'arguments[0]' not in script:
            raise InvalidScriptException(
                "Expecting webelement arguments to be used in script:"
                "\n{}\n".format(script))

        return self.browser.execute_async_script(script, self._webelement)

    @wait_for_display
    def trigger(self, event_name):
        '''
        Send a trigger event to the element using javascript.

        @type event_name: string
        @param event_name: the name of the event to trigger.
        '''
        script = '''
        $(arguments[0]).trigger('{e}');
        '''.format(e=event_name)

        self.execute_script(script)

    @wait_for_display
    def is_focused(self):
        """
        See if the current element has the focus or not.

        :rtype: bool
        :return: True if the element has focus and False if not.
        """
        return self.browser.switch_to.active_element == self._webelement

    @wait_for_display
    def focus(self):
        """
        Set the focus on this element.

        This uses javascript.
        """
        script = "return arguments[0].focus();"
        self.execute_script(script)

    @wait_for_display
    def blur(self):
        """
        Removes focus on this element.

        This uses javascript.
        """
        script = "return arguments[0].blur();"
        self.execute_script(script)

    def scroll_into_view(self):
        """
        Use javascript to scroll the element into view
        Please use with precaution.

        :type element: selenium.webdriver.remote.webelement.WebElement
        :param element: the WebElement to trigger event for
        """
        script = "arguments[0].scrollIntoView(true);"
        self.execute_script(script)

    def scroll_by(self, x, y):
        """
        Use javascript to scroll on an element
        Please use with precaution, especially as this is resolution dependent.

        :type element: selenium.webdriver.remote.webelement.WebElement
        :param element: the WebElement to trigger event for
        """
        script = "arguments[0].scrollBy({},{});".format(x, y)
        self.execute_script(script)

    @wait_for_display
    def css(self, property_name, value=None):
        """
        Get the css property or set the property.

        :type property_name: str
        :param property_name: name of the css property to get or set.

        :type value: str
        :param value: the value of the css property to set.

        :rtype: str
        :return: the value of the css property or None.

        Examples:

            >>> self.css('background-color', "'green'")  # string
            >>> self.css('background-color')
            u'rgba(0, 128, 0, 1)'
            >>> self.css('background-color', "null")     # null
            >>> self.css('width', "300")  # number
            >>> self.css('width')
            u'300px'

        """
        if value is None:
            return self._webelement.value_of_css_property(property_name)
        else:
            script = (
                "return arguments[0].style['{prop}'] = {val}"
                "".format(prop=property_name, val=value))
            self.execute_script(script)

    def color(self, property_name="color"):
        """
        Get a color property of the element.

        Defaults to css 'color' property.

        :type property_name: string
        :param property_name: the css color property you want to get.

        :rtype: color.Color
        :return: returns the Color object for the css color property
        """
        if 'color' not in property_name:
            raise ValueError(
                "The property '{}' you are looking for is not color related."
                "".format(property_name))
        return color.Color.from_string(self.css(property_name))

    @property
    @wait_for_display
    def inner_html(self):
        """
        Get the innerHTML.

        :rtype: str
        :return: HTML string of the WebElement
        """
        script = "return arguments[0].innerHTML"
        return self.execute_script(script).strip()

    @property
    @wait_for_display
    def label(self):
        """
        Looks for a label tag that has the same 'for' attribute
        value as and 'id' attribute value of an html object

        :type value: str
        :param value: the text value to the label tag
        """
        label_elem = self.browser.find_element_by_css_selector(
            "label[for='{id}']".format(
                id=self.element.get_attribute('id')))
        return label_elem.text.strip()

    @property
    @wait_for_display
    def text(self):
        """
        Returns the text value for the element.

        By default it will wait for the element to first be present and
        visible before getting the attribute.

        :rtype: str
        :return: the text value for the element.

        """
        return self._webelement.text

    def click(self, with_enter=False):
        """
        Override click() to first check
        for the element is displayed before clicking

        :type with_enter: bool
        :param with_enter: True to use ENTER key to click element on Windows

        Note: Don't need @wait_for_display decorator because the
              the 'mouse' property already has the decorator.
        """
        self.mouse.click(with_enter=with_enter)

    @wait_for_display
    def get_attribute(self, attribute):
        """
        Returns the attribute value for the given attribute.

        By default it will wait for the element to first be present and
        visible before getting the attribute.

        :type attribute: string
        :param attribute:

        :rtype: str
        :return: None if attribute is not there, otherwise the
                 value of the 'accesskey' attribute.

        """
        return self._webelement.get_attribute(attribute)

    @wait_for_display
    def get_data(self, data_attribute):
        """
        Get the attribute with the 'data-' prefix

        :type data_attribute: string
        :param data_attribute: the data-attribute to get the value for.

        :rtype: str
        :return: None if attribute is not there, otherwise the
                 value of the data-attribute
        """
        return self._webelement.get_attribute('data-{}'.format(data_attribute))

    @wait_for_display
    def has_overlap_with(self, element):
        """
        This methods determines the percentage of this element's
        bounding box is being overlapped by the given element's
        bounding box.

        :rtype: boolean
        :return: True if the given element's bounding box
                 overlaps with this element's bounding box
                 and False otherwise
        """
        this_location = self.location
        this_size = self.size

        elem_location = element.location
        elem_size = element.size

        this_h_min = this_location['x']
        this_h_max = this_location['x'] + this_size['width']
        this_v_min = this_location['y']
        this_v_max = this_location['y'] + this_size['height']

        elem_h_min = elem_location['x']
        elem_h_max = elem_location['x'] + elem_size['width']
        elem_v_min = elem_location['y']
        elem_v_max = elem_location['y'] + elem_size['height']

        return bool(
            (this_h_min <= elem_h_max and elem_h_min <= this_h_max) and
            (this_v_min <= elem_v_max and elem_v_min <= this_v_max))

    @classmethod
    def _init_with_webelement(
            cls, browser, webelement, parent_instance=None):
        """
        Returns an instance of Element reusing the element.

        @type browser: WebDriverWrapper
        @param browser: WebDriverWrapper instance

        :type webelement: WebElement
        :param webelement: the web element to init with.

        :type parent_instance: Element
        :param parent_instance: the parent instance

        :rtype: Element
        :return: Element object wrapping the element
        """
        elem = cls(
            browser, by=None, value=None, parent_instance=parent_instance)
        elem._element = webelement
        elem.id = webelement.id  # pylint: disable=invalid-name
        return elem

    # pylint: disable=invalid-name
    def find_element(self, by, value):
        """
        Finds an element by a locator type and value.

        :type by: string
        :param by: the type of locator to use.

        :type value: str
        :param value: the value of the locator to use

        """
        webelement = self._webelement.find_element(by, value)
        return Element._init_with_webelement(
            self.browser, webelement, parent_instance=self)

    # pylint: disable=invalid-name
    def find_elements(self, by, value):
        """
        Find elements by a locator type and value.

        :type by: string
        :param by: the type of locator to use.

        :type value: str
        :param value: the value of the locator to use

        """
        webelements = self._webelement.find_elements(by, value)
        elems = []
        for webelement in webelements:
            elem = Element._init_with_webelement(
                self.browser, webelement, parent_instance=self)
            elems.append(elem)
        return elems

    def is_slow_run_enabled(self):
        """
        Returns True if the global variable SLOW_WEBDRIVER_ENV is set to True
        else return False.

        :return: Whether SLOW_WEBDRIVER_ENV is eanbled or not.
        :rtype: bool
        """
        return SLOW_WEBDRIVER_ENV

    def __eq__(self, other):
        """
        Overloading the '==' operator

        If they have same web elements, return True, otherwise False.

        :type other: Element
        :param other: the other Element object to compare with

        :rtype: boolean
        :return: True if the web elements are same.
        """
        if isinstance(other, WebElement):
            return self._webelement == other
        elif isinstance(other, Element):
            return self._webelement == other._webelement
        return False

    def __ne__(self, other):
        """
        Overloading the '!=' operator

        If they don't have same web elements, return True, otherwise False.

        :type other: Element
        :param other: the other Element object to compare with

        :rtype: boolean
        :return: True if the web elements are not same.
        """
        return not self.__eq__(other)

    #  ----- overriding WebElements's methods ----

    # setup the find element(s) methods.
    # pylint: disable=invalid-name
    find_element_by_class_name = partialmethod(
        find_element, By.CLASS_NAME)
    find_element_by_css_selector = partialmethod(
        find_element, By.CSS_SELECTOR)
    find_element_by_id = partialmethod(
        find_element, By.ID)
    find_element_by_link_text = partialmethod(
        find_element, By.LINK_TEXT)
    find_element_by_name = partialmethod(
        find_element, By.NAME)
    find_element_by_partialmethod_link_text = partialmethod(
        find_element, By.PARTIAL_LINK_TEXT)
    find_element_by_tag_name = partialmethod(
        find_element, By.TAG_NAME)
    find_element_by_xpath = partialmethod(
        find_element, By.XPATH)

    find_elements_by_class_name = partialmethod(
        find_elements, By.CLASS_NAME)
    find_elements_by_css_selector = partialmethod(
        find_elements, By.CSS_SELECTOR)
    find_elements_by_id = partialmethod(
        find_elements, By.ID)
    find_elements_by_link_text = partialmethod(
        find_elements, By.LINK_TEXT)
    find_elements_by_name = partialmethod(
        find_elements, By.NAME)
    find_elements_by_partialmethod_link_text = partialmethod(
        find_elements, By.PARTIAL_LINK_TEXT)
    find_elements_by_tag_name = partialmethod(
        find_elements, By.TAG_NAME)
    find_elements_by_xpath = partialmethod(
        find_elements, By.XPATH)


#  ----- predefined element properties ----
Element.generate_attributes_properties([
    'accesskey',
    'class',
    'contenteditable',
    'contextmenu',
    'dir',
    'draggable',
    'dropzone',
    'hidden',
    'id',
    'lang',
    'spellcheck',
    'style',
    'tabindex',
    'title',
    'translate'])
