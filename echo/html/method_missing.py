#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# pylint: disable=too-few-public-methods
# pylint: disable=redefined-builtin

"""
MethodMissing module
"""

from __future__ import absolute_import
import logging


class MethodMissing(object):

    """
    A Python version of Ruby's method_missing function.
    """

    def __init__(self):
        '''
        Init
        '''
        self.logger = logging.getLogger('MethodMissing')

    def method_missing(self, attr, *args, **kwargs):
        """
        Stub: override this function
        """
        raise NotImplementedError(
            "Missing method '{s}' called.".format(s=attr))

    def __getattr__(self, attr):
        """
        Returns a function def 'callable' that wraps method_missing
        """

        if not hasattr(attr, '__call__'):
            # self.logger.info("no call in method missing")
            return self.method_missing(attr)

        def callable(*args, **kwargs):
            """
            Returns a method that will be calling an overloaded
            method_missing

            :return: the return value of the missing method
                     in the subclass
            """
            return self.method_missing(attr, *args, **kwargs)
        return callable
