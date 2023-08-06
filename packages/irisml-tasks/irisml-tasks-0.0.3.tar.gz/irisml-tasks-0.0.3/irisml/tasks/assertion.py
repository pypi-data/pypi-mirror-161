import dataclasses
from typing import Any, Optional
import irisml.core


class Task(irisml.core.TaskBase):
    """Assert the given input.

    For assert_equal and assert_not_equal, the supported type is str, int, float. List and Dict is also supported.
    For other assertions, only float is supported.
    """
    VERSION = '0.1.0'
    CACHE_ENABLED = False

    @dataclasses.dataclass
    class Inputs:
        value: Any

    @dataclasses.dataclass
    class Config:
        assert_equal: Optional[Any] = None
        assert_not_equal: Optional[Any] = None
        assert_almost_equal: Optional[float] = None
        assert_not_almost_equal: Optional[float] = None
        assert_greater: Optional[float] = None
        assert_greater_equal: Optional[float] = None
        assert_less: Optional[float] = None
        assert_less_equal: Optional[float] = None
        delta: float = 1e-2  # Threshold for assert_almost_equal and assert_not_almost_equal

    def execute(self, inputs):  # noqa: C901
        value = inputs.value

        if self.config.assert_equal is not None:
            if value != self.config.assert_equal:
                raise AssertionError(f"{value} != {self.config.assert_equal}")

        if self.config.assert_not_equal is not None:
            if value == self.config.assert_equal:
                raise AssertionError(f"{value} == {self.config.assert_equal}")

        if self.config.assert_almost_equal is not None:
            self._raise_if_not_number(value, "assert_almost_equal requires a number.")
            self._raise_if_not_number(self.config.assert_almost_equal, "assert_almost_equal requires a number.")

            diff = abs(value - self.config.assert_almost_equal)
            if diff > self.config.delta:
                raise AssertionError(f"Diff between {value} and {self.config.assert_almost_equal} is {diff} ( > {self.config.delta} )")

        if self.config.assert_not_almost_equal is not None:
            self._raise_if_not_number(value, "assert_not_almost_equal requires a number.")
            self._raise_if_not_number(self.config.assert_not_almost_equal, "assert_not_almost_equal requires a number.")

            diff = abs(value - self.config.assert_not_almost_equal)
            if diff < self.config.delta:
                raise AssertionError(f"Diff between {value} and {self.config.assert_not_almost_equal} is {diff} ( > {self.config.delta} )")

        if self.config.assert_greater is not None:
            self._raise_if_not_number(value, "assert_greater requires a number.")
            self._raise_if_not_number(self.config.assert_greater, "assert_greater requires a number.")

            if value <= self.config.assert_greater:
                raise AssertionError(f"{value} <= {self.config.assert_greater}")

        if self.config.assert_greater_equal is not None:
            self._raise_if_not_number(value, "assert_greater_equal requires a number.")
            self._raise_if_not_number(self.config.assert_greater_equal, "assert_greater_equal requires a number.")

            if value < self.config.assert_greater_equal:
                raise AssertionError(f"{value} < {self.config.assert_greater_equal}")

        if self.config.assert_less is not None:
            self._raise_if_not_number(value, "assert_less requires a number.")
            self._raise_if_not_number(self.config.assert_less, "assert_less requires a number.")

            if value >= self.config.assert_less:
                raise AssertionError(f"{value} >= {self.config.assert_less}")

        if self.config.assert_less_equal is not None:
            self._raise_if_not_number(value, "assert_less_equal requires a number.")
            self._raise_if_not_number(self.config.assert_less_equal, "assert_less_equal requires a number.")

            if value > self.config.assert_less_equal:
                raise AssertionError(f"{value} > {self.config.assert_less_equal}")

        return self.Outputs()

    def _raise_if_not_number(self, value, msg):
        if not isinstance(value, (int, float)):
            raise ValueError(f"{msg}: {type(value)}({value})")
