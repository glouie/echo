#!/usr/bin/python
# vim: set fileencoding=utf-8 :

from __future__ import absolute_import

import ctypes
import logging
import sys
import threading
import time
from functools import wraps
from threading import Thread

import six

LOGGER = logging.getLogger(__name__)

TIMEOUT = 60
FREQUENCY = 0.5


class TimeoutException(Exception):
    """
    Exception raised when the polling function times out
    """
    pass


class PollingThread(Thread):
    """
    Thread class used in poll decorator
    """

    def __init__(self, target, args, kwargs):
        """
        Sets the daemon thread and starts the thread
        :param target: target function
        :param args: args
        :param kwargs: kwargs
        """
        Thread.__init__(self)
        self.setDaemon(True)
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.exception = None
        self.start()

    def run(self):
        """
        Thread run method
        :return:
        """
        try:
            self.result = self.target(*self.args, **self.kwargs)
        except Exception as exc:
            exc.traceback = sys.exc_info()[2]
            self.exception = exc
        except:
            self.exception = Exception()
            self.exception.traceback = sys.exc_info()[2]
        else:
            self.exception = None

    def _get_thread_id(self):
        """
        Get the id of the thread

        :rtype: int
        :return: the thread id
        """
        for tid, thread in threading._active.items():
            if thread is self:
                return tid
        return None

    def _raise_SystemExit(self):
        """
        Asynchronously raise a SystemExit in a thread
        """
        thread_id = self._get_thread_id()
        if thread_id is not None:
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                thread_id, ctypes.py_object(SystemExit))
            if res > 1:
                # fail to setAsyncExec, revert the effect
                ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
                raise SystemError("PyThreadState_SetAsyncExc failed")

    def stop(self):
        """
        This method is used to stop the thread
        """
        if self.is_alive():
            if sys.version_info.major == 2:
                self._Thread__stop()
            else:
                self._raise_SystemExit()


def poll(timeout=TIMEOUT, ignore_exceptions=None,
         error_message=None, event=None):
    """
    Poll by calling a target function until a certain condition is met.

    :type timeout: int
    :param timeout: timeout in seconds

    :type error_message: String or None
    :param error_message: Error message passed while calling wait for condition
        Default value is None

    :type ignore_exceptions: tuple
    :param ignore_exceptions: the specified ignored exception classes

    :type event: threading.Event
    :param event: the specified threading event to set

    ;return: Result or exception
    """
    timeout = TIMEOUT if timeout is None else timeout
    ignore_exceptions = ignore_exceptions or ()
    ignore_exception_list = []

    if isinstance(ignore_exceptions, (tuple, list)):
        # for type tuple or list
        ignore_exception_list.extend(
            [exp.__name__ for exp in ignore_exceptions])

    else:
        # single value
        ignore_exception_list.append(ignore_exceptions.__name__)

    def outer(func):
        """
        Outer method to wrap the inner method that calls the target function

        When a decorator is used it basically replaces one function with
        another function.
        Decorator can also be used as :
        check_condition = poll(check_condition)
        In this case your function check_condition will be replaced by wrapper
        and when you do check_condition.__name__ it will print wrapper because
        thats the name of your new function.
        Which means using decorator -> Missing information
        To solve this issue we use @wraps.
        @wraps takes a function used in a decorator and adds the functionality
        of copying over the function name, docstring, and  arguments list.
        @wraps will invoke the update_wrapper() method

        :param func: target function
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            Wrapper method
            :param args: functions args
            :param kwargs: function kwargs
            :return: Result
            """
            start_time = time.time()
            worker = PollingThread(func, args, kwargs)
            worker.join(timeout)

            if event is not None:
                event.set()

            elapsed_time = time.time() - start_time
            if elapsed_time >= timeout:
                if worker.is_alive():
                    worker.stop()
                msg = ("Condition for function {func} with args "
                       "{args} and kwargs {kwargs} is not met after "
                       "{time} seconds. Error message is '{e}'".
                       format(time=timeout,
                              func=func.__name__,
                              args=args, kwargs=kwargs, e=error_message))
                raise TimeoutException(msg)

            elif (worker.exception.__class__.__name__ == 'TimeoutError' and elapsed_time < timeout):
                LOGGER.debug(
                    'Specified timeout has not occurred, even '
                    'thought the method threw a TimeoutError. '
                    'Exception is {exp}, call stack {stack}'.format(
                        exp=worker.exception.__class__.__name__,
                        stack=worker.exception.traceback))

            elif worker.exception is not None:
                if (worker.exception.__class__.__name__ not in
                        ignore_exception_list and worker.exception.__class__.__name__ != 'TimeoutError'):
                    exc_class = worker.exception.__class__
                    traceback = worker.exception.traceback
                    six.reraise(exc_class, worker.exception, traceback)
            else:
                # use getattr as it can be undefined, leading to wrong exception
                return getattr(worker, "result", None)

        return wrapper

    return outer


def poll_for_value(
        value, func, func_args=[], func_kwargs=None, timeout=TIMEOUT,
        frequency=FREQUENCY, ignore_exceptions=None,
        error_message=None):
    """
    Poll for value poll to check if the value specified is equal to the
    result of the target function specified in given timeout

    :type: can be of any type
    :param value: any value

    :type func: Function
    :param func: target function

    :type func_args: list
    :param func_args: arguments in the function

    :type func_kwargs: dict
    :param func_kwargs: key words args

    :type timeout: int
    :param timeout: timeout specified

    :type error_message: string
    :param error_message: error message specified as kwargs

    :type frequency: int
    :param frequency: frequency for checking

    :type ignore_exceptions: tuple/list
    :param ignore_exceptions: You can specify a tuple/list of exceptions that
        should be caught and ignored on every iteration. If the target function
        raises one of these exceptions, it will be caught and the exception
        instance will be pushed to the queue of values
        collected during polling. Any other exceptions raised will be
        raised as normal.
    :return: wait for value specified to be true
    """
    func_args = func_args or []
    func_kwargs = func_kwargs or dict()
    ignore_exceptions = ignore_exceptions or ()

    if isinstance(ignore_exceptions, list):
        ignore_exceptions = tuple(ignore_exceptions)

    exit_loop_event = threading.Event()

    @poll(timeout, ignore_exceptions, error_message, exit_loop_event)
    def check_condition():
        """
        Return the value based on the result from target function in
        specified timeout
        """
        while not exit_loop_event.isSet():
            try:
                rtn_value = func(*func_args, **func_kwargs)
                if value == rtn_value:
                    return rtn_value
            except ignore_exceptions as exception:
                LOGGER.debug('Ignored {exp} {msg} error msg {e}'.format(
                    exp=exception.__class__.__name__,
                    msg=str(exception),
                    e=error_message))
            time.sleep(frequency)

    return check_condition()


def poll_for_condition(
        func, func_args=None, func_kwargs=None, timeout=TIMEOUT,
        frequency=FREQUENCY, ignore_exceptions=None,
        error_message=None):
    """
    Poll for condition checks if the given condition is true and return the
    value

    :type func: Function
    :param func: target function

    :type func_args: list
    :param func_args: arguments in the function

    :type func_kwargs: dict
    :param func_kwargs: key words args

    :type timeout: int
    :param timeout: timeout specified

    :type error_message: string
    :param error_message: error message specified as kwargs

    :type frequency: int
    :param frequency: frequency for checking

    :type ignore_exceptions: tuple/list
    :param ignore_exceptions: You can specify a tuple/list of exceptions that
        should be caught and ignored on every iteration. If the target function
        raises one of these exceptions, it will be caught and the exception
        instance will be pushed to the queue of values
        collected during polling. Any other exceptions raised will be
        raised as normal.
    :return: the return value of the condition function
    """

    func_args = func_args or []
    func_kwargs = func_kwargs or dict()
    ignore_exceptions = ignore_exceptions or ()
    exit_loop_event = threading.Event()

    if isinstance(ignore_exceptions, list):
        ignore_exceptions = tuple(ignore_exceptions)

    @poll(timeout, ignore_exceptions, error_message, exit_loop_event)
    def check_condition():
        """
        Return the value based on the result from target function in
        specified timeout
        """
        while not exit_loop_event.isSet():
            try:
                result = func(*func_args, **func_kwargs)
                if bool(result):
                    return result
            except ignore_exceptions as exception:
                LOGGER.debug('Ignored {exp} {msg} error msg {e}'.format(
                    exp=exception.__class__.__name__,
                    msg=str(exception),
                    e=error_message))
            time.sleep(frequency)

    return check_condition()


DEFAULT_IGNORE_RESULTS = (None, 0, False, '', [], (), {}, set())


def default_reject_func(_):
    """
    default reject function will not reject anything
    """
    return False


def poll_for_result(
        func, func_args=None, func_kwargs=None, timeout=TIMEOUT,
        frequency=FREQUENCY, ignore_exceptions=None,
        error_message=None,
        ignore_results=None, reject_func=None):
    """
    Poll for result of target function. Will keep polling if the result
        * is rejected by the reject_func
        * or is in the ignore_results

    :type func: Function
    :param func: target function

    :type func_args: list
    :param func_args: arguments in the function

    :type func_kwargs: dict
    :param func_kwargs: key words args

    :type timeout: int
    :param timeout: timeout specified

    :type error_message: string
    :param error_message: error message specified as kwargs

    :type frequency: int
    :param frequency: frequency for checking

    :type ignore_exceptions: tuple/list
    :param ignore_exceptions: You can specify a tuple/list of exceptions that
        should be caught and ignored on every iteration. If the target function
        raises one of these exceptions, it will be caught and the exception
        instance will be pushed to the queue of values
        collected during polling. Any other exceptions raised will be
        raised as normal.

    :type ignore_results: tuple/list/None
    :param ignore_results: Keep polling if the target result is one of it.
                        If None then default ignore results will be used.


    :type reject_func: Function/None
    :param reject_func: Keep polling if the target result is rejected by it.
                    Return boolean value to decide whether the result will
                    be rejected.
                    Accept target func (not predicate_func) call result
                    as the only parameter.
                    If None then the default reject func won't reject anything.

    :return: the return value of the target function
    """

    func_args = func_args or []
    func_kwargs = func_kwargs or dict()
    ignore_exceptions = ignore_exceptions or ()
    exit_loop_event = threading.Event()

    if isinstance(ignore_exceptions, list):
        ignore_exceptions = tuple(ignore_exceptions)

    if ignore_results is None:
        ignore_results = DEFAULT_IGNORE_RESULTS

    if reject_func is None:
        reject_func = default_reject_func

    if not callable(reject_func):
        raise TypeError('The reject_func should be callable')

    @poll(timeout, ignore_exceptions, error_message, exit_loop_event)
    def check_result():
        """
        Return the value based on the result from target function in
        specified timeout
        """
        while not exit_loop_event.isSet():
            try:
                result = func(*func_args, **func_kwargs)
                if (result not in ignore_results and not bool(reject_func(result))):
                    return result
            except ignore_exceptions as exception:
                LOGGER.debug('Ignored {exp} {msg} error msg {e}'.format(
                    exp=exception.__class__.__name__,
                    msg=str(exception),
                    e=error_message))

            time.sleep(frequency)

    return check_result()
