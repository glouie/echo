#!/usr/bin/python
# vim: set fileencoding=utf-8 :

from html.support.poll import TimeoutException
from html.support.poll import poll_for_result
import unittest


class TestPollForResult(unittest.TestCase):
    """
    This file consists of the tests that needs to be run when any
    changes are made to the poll package
    """

    def test_default_negative(self):
        """
        0 is in default ignore results. it will time out
        """

        def test_foo():
            return 0

        with self.assertRaises(TimeoutException):
            poll_for_result(
                test_foo,
                timeout=3,
                frequency=1,
            )

    def test_default_positive(self):
        """
        1 is not in default ignore results.
        Will return 1 as the poll result
        """

        def test_foo():
            return 1

        res = poll_for_result(
            test_foo
        )
        assert res == 1

    def test_ignore_results_passed(self):
        """
        Customize reject_results to let 0 return
        """

        def test_foo():
            return 0

        res = poll_for_result(
            test_foo,
            ignore_results=[None]
        )
        assert res == 0

    def test_ignore_results_denied(self):
        """
        Customize reject_results to reject the string 'abc'
        """

        def test_foo():
            return 'abc'

        with self.assertRaises(TimeoutException):
            poll_for_result(
                test_foo,
                ignore_results=['abc', ''],
                timeout=3,
                frequency=1,
            )

    def test_reject_func(self):
        """
        test the function of reject_func
        """

        def test_foo():
            return {
                'key1': 'value1',
            }

        # reject the result by checking the string 'key'
        with self.assertRaises(TimeoutException):
            poll_for_result(
                test_foo,
                reject_func=lambda x: 'key1' in x,
                timeout=3,
                frequency=1,
            )

        # won't reject the result because the reject_func
        # rejects 'value2' but not 'value1'
        res = poll_for_result(
            test_foo,
            reject_func=lambda x: x['key1'] == 'value2',
            timeout=3,
            frequency=1,
        )
        assert res == {'key1': 'value1'}

        # although this reject_func didn't reject the result
        # but the ignore results still rejected it
        with self.assertRaises(TimeoutException):
            poll_for_result(
                test_foo,
                reject_func=lambda x: x['key1'] == 'value2',
                ignore_results=[{'key1': 'value1'}],
                timeout=3,
                frequency=1,
            )

    def test_reject_func_type_error(self):
        """
        raise type error when the reject_func is not callable
        """
        with self.assertRaises(TypeError):
            poll_for_result(
                lambda x: True,
                reject_func=666,
                timeout=3,
                frequency=1,
            )

    def test_reject_func_return_value(self):
        """
        Test if reject func return a NON Boolean value
        Expected boo(reject_func(x)) will run
        """
        # For reject_func, return non empty string is treated as True
        with self.assertRaises(TimeoutException):
            poll_for_result(
                lambda: 20,
                reject_func=lambda x: 'Always reject',
                timeout=3,
                frequency=1,
            )

        # For reject_func, return empty dict is treated as False
        res = poll_for_result(
            lambda: 20,
            reject_func=lambda x: {},
            timeout=3,
            frequency=1,
        )
        assert res == 20


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPollForResult)
    unittest.TextTestRunner(verbosity=2).run(suite)
