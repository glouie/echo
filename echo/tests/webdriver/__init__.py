#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta
from abc import abstractmethod


class BaseHtmlTest(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def setup_method(self, method):
        """
        Setup method to run before every tests.
        """

    @abstractmethod
    def teardown_method(self, method):
        """
        Teardown method to run after every tests.
        """
