#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# pylint: disable=protected-access

"""
Mouse class
===========
* handles mouse interactions.

DragTo class
============
* handles drag operation for mouse.
"""


from __future__ import absolute_import
import platform

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import MoveTargetOutOfBoundsException


class Mouse(object):

    """
    Helper class to provide the mouse APIs
    """

    def __init__(self, element):
        """
        Init

        :type element: Element
        :param element: the specified element

        """
        self._element = element
        self._browser = element.browser
        self._drag_to = DragTo(self)

    @property
    def drag_to(self):
        """
        Returns drag and drop helper
        """
        return self._drag_to

    def click(self, with_enter=False):
        """
        Click the element

        :type with_enter: bool
        :param with_enter: True to use ENTER key to click element on Windows
        """
        if platform.system() == 'Windows' and with_enter:
            self.hover()
            self._element.send_keys(Keys.ENTER)
        else:
            self._element._webelement.click()

    def hover(self):
        """
        Hovers over the element
        """
        if "safari" in self._browser.name.lower():
            self._element.focus()
        if "firefox" in self._browser.name.lower():
            try:
                webelement = self._element._webelement
                ActionChains(self._browser).move_to_element(
                    webelement).perform()
            except MoveTargetOutOfBoundsException:
                self._browser.execute_script(
                    "arguments[0].scrollIntoView();", webelement)
                webelement = self._element._webelement
                ActionChains(self._browser).move_to_element(
                    webelement).perform()
        else:
            webelement = self._element._webelement
            hover = ActionChains(self._browser).move_to_element(
                webelement)
            hover.perform()

    def release(self):
        """
        Mouse release over the element
        """
        action = ActionChains(self._browser).release(
            self._element._webelement)
        action.perform()

    def click_and_hold(self):
        """
        Click and hold the element
        """
        action = ActionChains(self._browser).click_and_hold(
            self._element._webelement)
        action.perform()

    def double_click(self):
        """
        Double click the element
        """
        action = ActionChains(self._browser).double_click(
            self._element._webelement)
        action.perform()

    def context_click(self):
        """
        Context-click (right click) on the element
        """
        action = ActionChains(self._browser).context_click(
            self._element._webelement)
        action.perform()

    def move_with_offset(self, xoffset, yoffset):
        """
        Move to the element with an x and y offset

        :type xoffset: int
        :param xoffset: the horizontal offset position from the element

        :type yoffset: int
        :param yoffset: the vertical offset position from the element
        """
        action = ActionChains(
            self._browser).move_to_element_with_offset(
                self._element._webelement, xoffset, yoffset)
        action.perform()

    def click_with_offset(self, xoffset, yoffset):
        """
        Move to the element with an x and y offset then click at that
        location.

        :type xoffset: int
        :param xoffset: the horizontal offset position from the element

        :type yoffset: int
        :param yoffset: the vertical offset position from the element
        """
        action = ActionChains(
            self._browser).move_to_element_with_offset(
                self._element._webelement, xoffset, yoffset).click()
        action.perform()

    def double_click_with_offset(self, xoffset, yoffset):
        """
        Move to the element with an x and y offset then double click at that
        location.

        :type xoffset: int
        :param xoffset: the horizontal offset position from the element

        :type yoffset: int
        :param yoffset: the vertical offset position from the element
        """
        action = ActionChains(
            self._browser).move_to_element_with_offset(
                self._element._webelement, xoffset, yoffset).double_click()
        action.perform()

    def move(self):
        """
        Move to the web element
        """
        action = ActionChains(
            self._browser).move_to_element(self._element._webelement)
        action.perform()

    def click_with_move(self):
        """
        Move to the web element and perform click
        """
        action = ActionChains(
            self._browser).move_to_element(
                self._element._webelement).click(self._element._webelement)
        action.perform()

    def double_click_with_move(self):
        """
        Move to the web element and perform double click
        """
        action = ActionChains(
            self._browser).move_to_element(
                self._element._webelement).double_click(
            self._element._webelement)
        action.perform()


class DragTo(object):

    """
    Helper class to provide the drag and drop APIs
    """

    def __init__(self, mouse):
        """
        Init

        :type mouse: Mouse
        :param mouse: the mouse helper object

        """
        self._element = mouse._element
        self._browser = mouse._browser

    def element(self, dest_element):
        """
        Drag and drop element to the position of another element.

        Will not work if top left corner of the WebElement is
        outside the viewable window/canvas.

        :type dest_element: Element
        :param src_element: the WebElement to be dragged to
        """
        action_chains = ActionChains(
            self._browser).drag_and_drop(
                self._element._webelement, dest_element._webelement)
        action_chains.perform()

    def relative_position(self, xoffset, yoffset):
        """
        Drag and drop element across by a xoffset and down
        by a yoffset.

        Will not work if top left corner of the element is
        outside the viewable window/canvas.

        :type xoffset: int
        :param xoffset: the number of pixels to move horizontally

        :type yoffset: int
        :param yoffset: the number of pixels to move vertically
        """
        if "firefox" in self._browser.name.lower():
            webelement = self._element._webelement
            try:
                ActionChains(self._browser).drag_and_drop_by_offset(
                    webelement, xoffset, yoffset).perform()
            except MoveTargetOutOfBoundsException:
                self._browser.execute_script(
                    "arguments[0].scrollIntoView();", webelement)
                ActionChains(self._browser).drag_and_drop_by_offset(
                    webelement, xoffset, yoffset).perform()
        else:
            action_chains = ActionChains(
                self._browser).drag_and_drop_by_offset(
                self._element._webelement, xoffset, yoffset)
            action_chains.perform()

    def absolute_position(self, xloc, yloc):
        """
        Drag and drop the element to the an absolute position
        on the window.

        Will not work if top left corner of the element is
        outside the viewable window/canvas.

        :type xloc: int
        :param xloc: the horizontal position of the window in pixels

        :type yloc: int
        :param yloc: the vertical horizontal position of the window
                     in pixels
        """
        loc = self._element._webelement.location
        xoffset = xloc - loc['x']
        yoffset = yloc - loc['y']
        self.relative_position(xoffset, yoffset)
