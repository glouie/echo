#!/usr/bin/python
# vim: set fileencoding=utf-8 :

from html.support import poll
import unittest
import time


class TestPollPackage(unittest.TestCase):
    """
    This file consists of the tests that needs to be run when any
    changes are made to the poll package
    """

    def test_poll_ok(self):
        """
        Test when timeout=None is provided
        """

        @poll.poll(None)
        def test_foo():
            """
            Sleep for 1 seconds
            """
            time.sleep(1)

        test_foo()

    def test_poll_default(self):
        """
        Test when no timeout is provided
        """

        @poll.poll()
        def test_foo():
            """
            Sleep for 1 seconds
            """
            time.sleep(1)

        test_foo()

    def test_break_sleep(self):
        """
        Test to timeout a method after 1 second
        """

        @poll.poll(1)
        def test_foo():
            """
            Sleep for 2 seconds
            """
            time.sleep(2)

        with self.assertRaises(poll.TimeoutException):
            test_foo()

    def test_timeout_partial(self):
        """
        Test partial timeout
        """

        @poll.poll(0.2)
        def test_foo():
            """
            Sleep for 0.4 seconds
            """
            time.sleep(0.4)

        with self.assertRaises(poll.TimeoutException):
            test_foo()

    def test_function_name(self):
        """
        Test to verify that polling is not overwriting the target method
        """

        @poll.poll(timeout=2)
        def test_foo():
            """
            To test the name of the function
            """
            pass

        assert test_foo.__name__ == 'test_foo'

    def test_time_diff(self):
        """
        Test to verify polling method times out in seconds provided
        """
        start_time = time.time()

        @poll.poll(timeout=3)
        def test_foo():
            """
            Sleep for 10 seconds
            """
            time.sleep(10)

        with self.assertRaises(poll.TimeoutException):
            test_foo()

        self.assertEqual(int(time.time() - start_time), 3)

    def test_time_diff_ok(self):
        """
        Test to verify timeout same as the operation time
        """
        start_time = time.time()

        @poll.poll(timeout=2)
        def test_foo():
            """
            Sleep for 2 seconds
            """
            time.sleep(2)

        with self.assertRaises(poll.TimeoutException):
            test_foo()

        self.assertEqual(int(time.time() - start_time), 2)

    def test_validate_exception(self):
        """
        Test to validate the exception raised
        """

        @poll.poll(1)
        def test_foo():
            """
            Sleep for 2 seconds
            """
            time.sleep(2)

        self.assertRaises(poll.TimeoutException, test_foo)

    def test_base_exception(self):
        """
        Test to validate the base exception raised
        """

        @poll.poll(3)
        def test_foo():
            """
            Sleep for 2 seconds
            """
            time.sleep(1)
            raise BaseException

        self.assertRaises(BaseException, test_foo)

    def test_ignore_exception(self):
        """
        Test to validate the ignore exception is not raise
        """

        @poll.poll(2, ignore_exceptions=RuntimeError)
        def test_foo():
            """
            Sleep for 2 seconds
            """
            try:
                raise RuntimeError
            finally:
                time.sleep(5)

        self.assertRaises(poll.TimeoutException, test_foo)

    def test_ignore_timeout_error(self):
        """
        Test to ignore timeouterror
        """
        from multiprocessing import TimeoutError
        import time

        @poll.poll(2)
        def test_foo():
            try:
                raise TimeoutError
            finally:
                time.sleep(3)

        self.assertRaises(poll.TimeoutException, test_foo)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPollPackage)
    unittest.TextTestRunner(verbosity=2).run(suite)
