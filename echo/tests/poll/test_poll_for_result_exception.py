#!/usr/bin/python
# vim: set fileencoding=utf-8 :

from html.support.poll import poll_for_result
import unittest


class TimeoutException(Exception):
    """
    Exception only defined in this module.
    Test the behavior along with the one with same name in polling
    """
    pass


class TestPollForResultException(unittest.TestCase):
    """
    This file consists of the tests that needs to be run when any
    changes are made to the poll package
    """

    def test_normal_exception_raise(self):
        """
        test raise exception inside reject_func
        """
        with self.assertRaises(ZeroDivisionError):
            poll_for_result(
                lambda: 20,
                reject_func=lambda x: 1 / 0,
                timeout=3,
                frequency=1,
            )

    def test_normal_exception_ignore(self):
        """
        test raise exception inside reject_func, but ignored
        """
        target_list = [2, 1]

        def reject_func(value):
            """
            Raise exception only when value is 1
            """
            if value == 1:
                raise RuntimeError('value is 1')
            else:
                return False

        res = poll_for_result(
            lambda: target_list.pop(),
            reject_func=reject_func,
            ignore_exceptions=(RuntimeError,),
            timeout=3,
            frequency=1,
        )
        assert res == 2

    def test_timeout_exception(self):
        """
        Test raise a customized TimeoutException
        """
        def reject_func(_):
            """
            Raise TimeoutException
            """
            raise TimeoutException()

        with self.assertRaises(TimeoutException):
            poll_for_result(
                lambda: 20,
                reject_func=reject_func,
                timeout=3,
                frequency=1,
            )


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(
        TestPollForResultException)
    unittest.TextTestRunner(verbosity=2).run(suite)
