"""
Meta
====
    $Id$
    $DateTime$
    $Author$
    $Change$
"""

from __future__ import absolute_import
import socket
from random import Random
import logging

PORT_MIN = 8000
PORT_MAX = 65500


class PortUtil(object):
    """
    Base class to get the utility functions in your tests
    """

    def __init__(self, port_min=PORT_MIN, port_max=PORT_MAX):
        '''
        Constructor
        'port_min' and 'port_max' are the range of ports
        '''
        self.port_min = port_min
        self.port_max = port_max
        self.logger = logging.getLogger("PortUtil")
        self.list_ports = []

    def _get_random_port(self):
        '''
        generates a random int between port_min and port_max.
        @rtype: integer
        @return: returns a random port between port_min and port_max
        '''
        rand = Random()
        num = rand.randint(self.port_min, self.port_max)
        while(num in self.list_ports):
            num = rand.randint(self.port_min, self.port_max)
        self.list_ports.append(num)
        return num

    def find_open_port(self, target='localhost', tries=100):
        '''
        Checks and returns open port else returns errors

        @type target: string
        @param target: hostname

        @type tries: int
        @param tries: number of attempt to get a random port that is open

        @rtype: integer
        @return: returns a random open port
        '''
        if (self.port_max - self.port_min) < tries:
            raise ValueError("Number of tries must not exceed the difference "
                             "in the port numbers.")
        targetIP = socket.gethostbyname(target)
        self.logger.info("Starting scan on host{IP}".format(IP=targetIP))

        count = 0
        while count < tries:
            port = self._get_random_port()
            try:
                soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                soc.connect((targetIP, port))
                soc.close()
            except socket.error as error:
                if 'refused' in error.strerror:
                    return port
            count += 1
        raise Exception("Tried for {n} times, but found no random port "
                        "that is opened.".format(n=tries))


class DeprecationHelper(object):
    '''
    Helper class used to deprecate classes.
    '''
    def __init__(self, new_class, message="This class has been deprecated."):
        '''
        DeprecationHelper Init

        @type new_class: class object
        @param new_class: the replacement class object for the deprecated class

        @type message: string
        @param message: the deprecation warning message
        '''
        self.new_class = new_class
        self._deprecation_message = message

    def _warn(self):
        '''
        Warn the user that this class is deprecated
        '''
        from warnings import warn
        warn(self._deprecation_message)

    def __call__(self, *args, **kwargs):
        '''
        Overwrite the __call__ method to warn and return the new class
        instantiation.
        '''
        self._warn()
        return self.new_class(*args, **kwargs)

    def __getattr__(self, attr):
        '''
        Overwrite __getattr__ to warn on every access of the class attributes
        '''
        self._warn()
        return getattr(self.new_class, attr)
