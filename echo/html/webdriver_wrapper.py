#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# pylint: disable=too-many-arguments
# pylint: disable=dangerous-default-value
# pylint: disable=locally-disabled
# pylint: disable=invalid-name
# pylint: disable=too-many-lines
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-public-methods
# pylint: disable=invalid-name

"""
WebderiverWrapper module

"""

from __future__ import absolute_import
from functools import partial
import logging
import time
import json
import os
import re
import datetime
import polling

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import wait
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.remote.remote_connection import RemoteConnection
from html.method_missing import MethodMissing
from html.support import url
from html.support import switch_to
from html import Element
from html import TIMEOUT

IMPLICIT_TIMEOUT = 1  # in second(s)
CONNECT_TIMEOUT = 180  # webdriver connect timeout in seconds

logging.basicConfig(
    filename='htmlwd.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s')

LOGGER = logging.getLogger(__name__)


class Wrapper(MethodMissing):

    """
    Wrapper object to wrap the selenium WebDriver instance.
    """

    def __init__(
            self,
            driver,
            timeout=TIMEOUT,
            poll_frequency=wait.POLL_FREQUENCY,
            implicit_timeout=IMPLICIT_TIMEOUT,
            connect_timeout=CONNECT_TIMEOUT,
            maximize_window=True):
        """
        Init

        :type driver: selenium.webdriver.remote.element.WebDriver
        :param driver: WebDriver object like instance

        :type timeout: int
        :param timeout: timeout used in wait methods (seconds)

        :type implicit_timeout: int
        :param implicit_timeout: implicit timeout on WebDriver's
                                 find_element* methods. (seconds)

        :type connect_timeout: int
        :param connect_timeout: remote connection timeout (seconds)

        :type maximize_window: bool
        :param maximize_window: True to attempt to maximize window
                                and False to not maximize the browser
                                window
        """

        super(Wrapper, self).__init__()

        self.driver = driver
        self.timeout = timeout or TIMEOUT
        self.poll_frequency = (
            poll_frequency if poll_frequency >= 0 else wait.POLL_FREQUENCY)
        self.implicit_timeout = implicit_timeout
        self.connect_timeout = connect_timeout
        self.logger = LOGGER
        self._url = url.Url(self.driver, None)
        self._switch_to = switch_to.SwitchTo(self)

        # pylint: disable=bare-except
        try:
            # set the timeouts for WebDriver methods
            self.driver.implicitly_wait(implicit_timeout)
            self.driver.set_script_timeout(timeout)
            self.driver.set_page_load_timeout(timeout)
            RemoteConnection.set_timeout(connect_timeout)
        except:
            # warn and move on even if setting timeouts failed.
            self.logger.warn("Faild to set WebDriver timeouts, using defaults")

        if maximize_window:
            try:
                self.maximize_window()
            except:
                self.logger.warn("Failed to maximize browser window.")

        #  ----- overriding WebDriver's methods ----

        # setup the find element(s) methods.
        self.find_element_by_class_name = partial(
            self.find_element, By.CLASS_NAME)
        self.find_element_by_css_selector = partial(
            self.find_element, By.CSS_SELECTOR)
        self.find_element_by_id = partial(
            self.find_element, By.ID)
        self.find_element_by_link_text = partial(
            self.find_element, By.LINK_TEXT)
        self.find_element_by_name = partial(
            self.find_element, By.NAME)
        self.find_element_by_partial_link_text = partial(
            self.find_element, By.PARTIAL_LINK_TEXT)
        self.find_element_by_tag_name = partial(
            self.find_element, By.TAG_NAME)
        self.find_element_by_xpath = partial(
            self.find_element, By.XPATH)

        self.find_elements_by_class_name = partial(
            self.find_elements, By.CLASS_NAME)
        self.find_elements_by_css_selector = partial(
            self.find_elements, By.CSS_SELECTOR)
        self.find_elements_by_id = partial(
            self.find_elements, By.ID)
        self.find_elements_by_link_text = partial(
            self.find_elements, By.LINK_TEXT)
        self.find_elements_by_name = partial(
            self.find_elements, By.NAME)
        self.find_elements_by_partial_link_text = partial(
            self.find_elements, By.PARTIAL_LINK_TEXT)
        self.find_elements_by_tag_name = partial(
            self.find_elements, By.TAG_NAME)
        self.find_elements_by_xpath = partial(
            self.find_elements, By.XPATH)

    # pylint: disable=unused-argument
    def method_missing(self, attr, *args, **kwords):
        """
        Dispatch incoming messages to selenium and do our custom
        logging.

        Raises AttributeError if the attribute is unknown or
        an Exception if another problem occurs.
        """
        if hasattr(self.driver, attr):
            return getattr(self.driver, attr)
        else:
            raise AttributeError(
                "WebDriver does not respond to '{a}'.".format(a=attr))
    
    def get_window_height(self):
        """
        Get the browser's window.innerHeight

        :rtype: int
        :return: height of window in pixels
        """
        script = ("return window.innerHeight")
        return self.driver.execute_script(script)

    def get_window_width(self):
        """
        Get the browser's window.innerWidth

        :rtype: int
        :return: width of window in pixels
        """
        script = ("return window.innerWidth")
        return self.driver.execute_script(script)

    def get_available_height(self):
        """
        Get the browser's window.screen.availHeight

        :rtype: int
        :return: number of avaliable height in pixels
        """
        script = ("return window.screen.availHeight")
        return self.driver.execute_script(script)

    def get_available_width(self):
        """
        Get the browser's window.screen.availWidth

        :rtype: int
        :return: number of avaliable width in pixels
        """
        script = ("return window.screen.availWidth")
        return self.driver.execute_script(script)

    def maximize_window(self):
        """
        Maximize the current browser window.
        """
        width = self.get_available_width()
        height = self.get_available_height()

        self.logger.info(
            'Available width and height: %s x %s', width, height)

        if (self.driver.name in ['ios', 'android']):
            self.logger.warn(
                "maximize_window is not supported on mobile devices.")
        elif self.driver.name != 'opera':
            self.driver.set_window_position(0, 0)
            self.driver.set_window_size(width, height)
        else:
            # if a browser is not supported then we'll open a
            # new window in full screen and close the current one.
            script = ("window.open(self.location,'mywin',"
                      "'left=0,top=0,"
                      "width='+{width}+',"
                      "height='+{height}+',"
                      "toolbar=0,resizable=1,scrollbars=1');"
                      "".format(width=width, height=height))
            self.driver.execute_script(script)
            self.driver.close()
            self.driver.switch_to.window('mywin')

    def change_window_size(self, width_delta, height_delta):
        """
        Change the size of the browser window
        by the given width and height pixel amounts.

        :type width_delta: int
        :param width_delta: number of pixels to change the width by.

        :type height_delta: int
        :param height_delta: number of pixels to change the height by.
        """
        currentSize = self.driver.get_window_size()
        self.driver.set_window_size(
            currentSize['width'] + width_delta,
            currentSize['height'] + height_delta)

    def wait(self, seconds):
        """
        Wait for seconds.

        :type seconds: int
        :param seconds: Seconds to wait
        """
        self.logger.info("Waiting for %d seconds.", seconds)
        time.sleep(seconds)

    def is_alert_displayed(self):
        """
        Check an alert is displayed

        :rtype: boolean
        :return: True if an alert is displayed and False if not.
        """
        try:
            # pylint: disable=pointless-statement
            self.driver.switch_to.alert.text
            return True
        except NoAlertPresentException:
            return False

    def wait_for_condition(
            self, method, method_args=None, method_kwargs=None,
            timeout=None, frequency=None,
            error_message=None, ignore_exceptions=None):
        """
        Waits for an arbitrary condition to be true.

        :type method: method
        :param method: the method to use to poll with.

        :type method_args: list of method arguments.
        :param method_args: the list of method arguments to pass
                            into the method.

        :type method_kwargs: list of method keyword arguments.
        :param method_kwargs: the list of method keyword arguments to pass
                              into the method.

        :type timeout: int
        :param timeout: number for seconds to wait before giving up

        :type frequency: int
        :param frequency: number for seconds to wait before
                          polling again

        :type error_message: string
        :param error_message: the error message to display when the
                              condition is not met before the timeout

        :type ignore_exceptions: tuple
        :param ignore_exceptions: You can specify a tuple of exceptions that
        should be caught and ignored on every iteration. If the target function
        raises one of these exceptions, it will be caught and the exception
        instance will be pushed to the queue of values
        collected during polling. Any other exceptions raised will be
        raised as normal.

        :return: the return value of the condition method
        """

        local_timeout = timeout or self.timeout
        local_freq = frequency or self.poll_frequency

        error_message = error_message if error_message is not None else u''

        method_args = method_args or ()
        method_kwargs = method_kwargs or dict()
        ignore_exceptions = ignore_exceptions or ()

        return polling.poll_for_condition(
            method, func_args=method_args, func_kwargs=method_kwargs,
            timeout=local_timeout, frequency=local_freq,
            ignore_exceptions=ignore_exceptions,
            error_message=error_message)

    def wait_for_alert_displayed(
            self, timeout=None, frequency=None):
        """
        Method to help to make sure alert displayed and switch
        to popup alert successfully.

        :type timeout:  int
        :param timeout: number for seconds to wait before giving up

        :type frequency:  int
        :param frequency: number for seconds to wait before
                          polling again

        """

        local_timeout = timeout or self.timeout
        local_freq = frequency or self.poll_frequency

        def wait_condition(driver):
            """
            Check if switch to alert popup successfully.

            :type driver: WebDriver
            :param driver: a WebDriver instance to find elements with

            :rtype: boolean
            :return: if switch successfully, return True.
                    Otherwise, return False.
            """
            try:
                # pylint: disable=pointless-statement
                alert = driver.switch_to.alert
                # Need below command to trigger NoAlertPresentException
                alert.text
                return alert
            except NoAlertPresentException:
                self.logger.debug("No Alert present yet.")
            return False

        return self.wait_for_condition(
            wait_condition, [self], timeout=local_timeout,
            frequency=local_freq, error_message=(
                "Alert was not present after {time} second(s) "
                "with a {freq} second(s) polling interval."
                "".format(
                    time=local_timeout, freq=local_freq)))

    def capture_screenshot(self, name=None):
        """
        Captures the screenshot to a file, in the current working
        directory.

         **Notes**
            #. valid filename must be given or it won't work.

            #. if no name is provided then it will default to the name,
                "screenshot_<current datetime>.png"

        :type name: `str`
        :param name: the name of the screenshot image file.

        :rtype: `str`
        :return: the full file_path of the screenshot

        """

        if name is None:
            filename = "screenshot_{s}.png".format(
                s=str(datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')))
        else:
            filename = name

        file_path = os.path.abspath(os.path.join(os.path.curdir, filename))
        self.driver.get_screenshot_as_file(file_path)
        return file_path

    def capture_screenshot_as_base64(self):
        """
        Captures the screenshot and returns the base64 string encoding
        of the image.

        :rtype: `str`
        :return: the base64 encoding of the captured screenshot.
        """
        return self.driver.get_screenshot_as_base64()

    def hover(self, by=By.ID, value=None):
        """
        Hovers over the WebElement after locating it first.

        :type by: :class:`webdriver.commmon.by.By`
        :param by:
            Selector types:
               * By.ID
               * By.CLASS_NAME
               * By.CSS_SELECTOR
               * By.LINK_TEXT
               * By.PARTIAL_LINK_TEXT
               * By.TAG_NAME

            Default: `By.ID`

        :type value: string
        :param value: Selector value for the selector type.
        """
        elem = self.find_element(by=by, value=value)
        elem.mouse.hover()

    def send_keys(self, *keys):
        """
        Send keys to the browser

        :type keys: selenium.webdriver.common.keys.Keys
        :param keys: keys to send to the browser
        """
        action_chains = ActionChains(self.driver).send_keys(*keys)
        action_chains.perform()

    def open(self, uri):
        """
        Opens the uri in the same domain.

        :type uri: string
        :param uri: the uri to open,
                    on the same domain or a different url entirely

        Examples:

        >>> wdw.open('foobar')
        http://localhost:8000/foobar
        >>> wdw.open('/foobar')
        http://localhost:8000/foobar
        >>> wdw.open('foobar/')
        http://localhost:8000/foobar/
        >>> wdw.open('foo/bar/')
        http://localhost:8000/foo/bar/

        >>> wdw2.open('foo/bar')
        https://127.0.0.1:8089/foo/bar
        >>> wdw2.open('foo/bar')
        https://127.0.0.1:8089/foo/bar

        >>> wdw3.open("foobar")
        file:///Users/foobar
        >>> wdw3.open("file:///foobar")
        file:///foobar

        >>> wdw.open('http://google.com')
        http://google.com
        >>> wdw.open('http://www.google.com')
        http://www.google.com
        >>> wdw.open('https://www.google.com')
        https://www.google.com
        >>> wdw.open('ftp://www.google.com')
        ftp://www.google.com

        >>> wdw.open('ftp://www.google.com:8000')
        ftp://www.google.com:8000

        """
        pattern = r'([\w]*:/{2,}[^/]*)'
        match = re.match(pattern, uri)
        if not match:
            # pylint: disable=bare-except
            try:
                match = re.match(pattern, self.url.value)
                domain = match.group(0)
                new_url = "{domain}/{uri}".format(
                    domain=domain, uri=uri.lstrip('/'))
            except:
                new_url = uri
        else:
            new_url = uri
        self.driver.get(new_url)

    def get_pixel_colors(self, locations):
        """
        Take a list of coordinates, and return a list of rgba
        tuples that represents the pixel color of those coordinates.

        :type locations: {'x','y'}[]
        :param locations: list of dictionaries containing the
                          x and y coordinates

        :rtype: list of 4-tuple
        :return: a list of 4-tuple representing the rgba value
                 of each point.

        Examples:

        >>> get_pixel_colors([{"x": 5, "y": 5}, {"x": 50, "y": 50}])
        [(34, 34, 34, 255), (89, 145, 48, 255)]

        """

        script = """
        var g = (function(imageSrc, stringifiedLocations) {{
            var img = new Image();
            img.src = imageSrc;
            var canvas = document.createElement("canvas");
            var ctx = canvas.getContext("2d");
            ctx.canvas.width = img.width;
            ctx.canvas.height = img.height;
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            var rgbas = [];
            var locations = JSON.parse(stringifiedLocations);
            for(var i = 0; i < locations.length; i++) {{
                rgbas.push(ctx.getImageData(
                    locations[i].x, locations[i].y, 1, 1).data);
            }}
            return rgbas;
        }})('{src}', '{locations}');
        return JSON.stringify(g);
        """
        imgsrc = "data:image/png;base64,{s}".format(
            s=self.driver.get_screenshot_as_base64())
        rtn = self.driver.execute_script(
            script.format(src=imgsrc, locations=json.dumps(locations)))
        if rtn:
            rgba_list = []
            for colorset in json.loads(rtn):
                rgba_list.append(
                    (colorset['0'], colorset['1'],
                     colorset['2'], colorset['3']))
            return rgba_list

    @property
    def url(self):
        """
        Get the Url object.

        :rtype: Url
        :return: Url object representing the url in the browser.
        """
        return self._url.update()

    def get_url_params_as_dict(self):
        """
        Returns the current URL query string parameters as a dict

        :rtype: dict
        :return: dict with all query string parameters
        """
        return self.url.get_url_params_as_dict()

    #  ----- overriding WebDriver's methods -----

    @property
    def current_url(self):
        """
        Override the default for self.driver.current_url,
        but changes nothing.

        Use self.url instead.
        """
        return self.url.value

    @property
    def switch_to(self):
        """
        Override the default for self.driver.switch_to,
        so that active_element is Element type.
        """
        return self._switch_to

    def find_element(self, by, value):
        """
        Finds an element by a locator type and value.

        :type by: string
        :param by: the type of locator to use.

        :type value: string
        :param value: the value of the locator to use

        """
        webelement = self.driver.find_element(by, value)

        # pylint: disable=protected-access
        return Element._init_with_webelement(self, webelement)

    def find_elements(self, by, value):
        """
        Find elements by a locator type and value.

        :type by: string
        :param by: the type of locator to use.

        :type value: string
        :param value: the value of the locator to use

        """
        webelements = self.driver.find_elements(by, value)

        # pylint: disable=protected-access
        return [Element._init_with_webelement(
            self, webelement) for webelement in webelements]
