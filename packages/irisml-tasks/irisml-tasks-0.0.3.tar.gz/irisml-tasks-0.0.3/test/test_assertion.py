import unittest
from irisml.core import Context
from irisml.tasks.assertion import Task


class TestAssert(unittest.TestCase):
    def test_simple_assert(self):
        self._assert_pass(100, assert_equal=100)
        self._assert_pass('100', assert_equal='100')
        self._assert_fail(100, assert_equal='100')
        self._assert_pass(1.2345, assert_equal=1.2345)

        self._assert_pass([1, 2, 3], assert_equal=[1, 2, 3])
        self._assert_fail([3, 4], assert_equal=[1, 2])

        self._assert_pass(100, assert_not_equal=105)

        self._assert_pass(3, assert_almost_equal=3)
        self._assert_pass(3.14, assert_almost_equal=3.15)
        self._assert_fail(3.14, assert_almost_equal=3.24)
        self._assert_pass(3.14, assert_not_almost_equal=3.24)
        self._assert_pass(3.14, assert_almost_equal=3.24, delta=0.2)

        self._assert_pass(123, assert_greater=100)
        self._assert_fail(123, assert_greater=1000.5)
        self._assert_fail(123, assert_greater=123)

        self._assert_pass(123, assert_greater_equal=1)
        self._assert_pass(123, assert_greater_equal=123)
        self._assert_fail(123, assert_greater_equal=153)

        self._assert_pass(100, assert_less=105)
        self._assert_fail(100, assert_less=49)
        self._assert_fail(100, assert_less=100)

        self._assert_pass(100, assert_less_equal=200)
        self._assert_fail(100, assert_less_equal=10)
        self._assert_pass(100, assert_less_equal=100)

    def test_invalid_assert(self):
        with self.assertRaises(ValueError):
            self._execute(50, assert_almost_equal='100')

        with self.assertRaises(ValueError):
            self._execute(50, assert_greater='100')

        with self.assertRaises(ValueError):
            self._execute(50, assert_less='100')

    def _execute(self, value, **kwargs):
        inputs = Task.Inputs(value)
        config = Task.Config(**kwargs)
        task = Task(config, Context())
        task.execute(inputs)

    def _assert_pass(self, value, **kwargs):
        self._execute(value, **kwargs)

    def _assert_fail(self, value, **kwargs):
        with self.assertRaises(AssertionError):
            self._execute(value, **kwargs)
