import unittest

import numpy as np

from osaft import WaveType
from osaft.solutions.base_solution import BaseSolution
from osaft.tests.basetest import (
    BaseTest,
    ChangingBool,
    ChangingFloat,
    ChangingFromList,
    ChangingInt,
)


class DummyClass(BaseSolution):

    def __init__(self) -> None:
        super().__init__('not_empty')

        self._wave_type = WaveType.STANDING

    @property
    def wave_type(self):
        return self._wave_type

    @wave_type.setter
    def wave_type(self, value):
        self._wave_type = value

    @property
    def f1(self) -> float:
        return 42.0

    @property
    def f2(self) -> float:
        return -42.0

    def func_1(self, n: int) -> complex:
        return 1 + 1j * (-1.0) ** n

    def func_2(self, n: int, arg: complex) -> complex:
        return 1 + arg * (-1.0) ** n

    def func_3(self, n: int, arg1: complex, arg2: complex) -> complex:
        return 1 + arg2 * (-1.0) ** n - arg2

    def input_variables(self) -> list:
        return []


class TestBaseTest(BaseTest):

    def setUp(self) -> None:
        super().setUp()
        self.cls = DummyClass()

        self.list_cls = [self.cls]

        self.rng = np.random.default_rng(self.seed)

    @property
    def f1(self) -> float:
        return 42.0

    @property
    def f2(self) -> float:
        return -42.0

    def func_1(self, n: int) -> complex:
        return 1 + 1j * (-1.0) ** n

    def func_2(self, n: int, arg: complex) -> complex:
        return 1 + arg * (-1.0) ** n

    def func_3(self, n: int, arg1: complex, arg2: complex) -> complex:
        return 1 + arg2 * (-1.0) ** n - arg2

    def test_properties(self) -> None:
        properties = ['f1', 'f2']
        self._test_properties(properties)

    def test_methods_n(self) -> None:
        methods = {}
        methods['func_1'] = None

        arg1 = self.rng.random() * (1j - 1)
        methods['func_2'] = arg1

        arg2 = self.rng.random() * (-1j + 1)
        methods['func_3'] = (arg1, arg2)

        self._test_methods_n(methods)

    def test_longest_list(self) -> None:
        for val in self.test_variables:
            if isinstance(val, ChangingFromList):
                self.assertEqual(self.n_runs, val.longest_list)

    def test_longest_list_ValueError(self) -> None:
        for val in self.test_variables:
            if isinstance(val, ChangingFromList):
                self.assertRaises(
                    ValueError, self._set_n_runs,
                    val.longest_list - 1,
                )

    def _set_n_runs(self, val):
        self.n_runs = val

    def test_do_testing_zero(self):

        small_value_func_1 = lambda: 1e-20
        small_value_func_2 = lambda: 1e-18

        # Check if AssertionError without zero argument
        do_testing = lambda: (
            self.do_testing(
                func_1=small_value_func_1,
                func_2=small_value_func_2,
            )
        )
        self.assertRaises(AssertionError, do_testing)

        # Check if no error with
        self.do_testing(
            func_1=small_value_func_1,
            func_2=small_value_func_2, zero=1e-19,
        )


class TestChangingFromList(unittest.TestCase):

    def setUp(self) -> None:

        self.n_runs = 10
        self.seed = 1

        self.initial_value = 'dog'
        self.list = ['dog', 'cat', 'mouse']

        # [*list] syntax is needed for not passing a reference but creating an
        # actual new list
        self.cls = ChangingFromList(
            'test_list', self.initial_value,
            [*self.list], self.seed,
        )

    def test_change(self):
        self.assertIn(self.cls.value, self.list)
        for _ in range(self.n_runs):
            self.cls.change()
            self.assertIn(self.cls.value, self.list)

    def test_if_changing(self):
        self.cls.value = 'dog'
        while self.cls.value == 'dog':
            self.cls.change()

    def test_class_variable(self):
        A = ChangingFromList('A', 'a', ['a', 'b'], 0)
        B = ChangingFromList('B', 'b', ['a', 'b', 'c'], 0)

        self.assertEqual(3, A.longest_list)
        self.assertEqual(3, B.longest_list)


class TestChangingBool(unittest.TestCase):

    def setUp(self) -> None:

        self.n_runs = 10
        self.seed = 1

        self.cls = ChangingBool('test_bool', True, self.seed)

    def test_change(self):
        self.cls.change()
        for _ in range(self.n_runs):
            self.assertIn(self.cls.value, [True, False])

    def test_value_changes(self):
        self.cls.value = True
        while self.cls.value:
            self.cls.change()


class BaseTestChangingNumber:

    class TestChangingNumber(unittest.TestCase):

        def setUp(self) -> None:

            self.n_runs = 10
            self.seed = 1

            self.cls = None
            self.initial_value = None
            self.low = None
            self.high = None
            self.seed = None

        def test_set_low_value_error(self):
            # Test Value Error
            self.cls.high = self.high
            with self.assertRaises(ValueError):
                self.cls.low = self.high + 1

        def test_set_low_reset_value(self):
            # Reset Value if value > low
            self.cls.value = self.low - 1
            self.cls.low = self.low
            self.assertTrue(self.cls.value > self.low)

        def test_set_high_value_error(self):
            # Test Value Error
            self.cls.low = self.low
            with self.assertRaises(ValueError):
                self.cls.high = self.low - 1

        def test_set_high_reset_value(self):
            # Reset Value if value > low
            self.cls.value = self.high + 1
            self.cls.high = self.high
            self.assertTrue(self.cls.value < self.high)

        def test_change(self):
            self.assertEqual(self.cls.value, self.initial_value)
            self.cls.change()
            self.assertNotEqual(self.cls.value, self.initial_value)

        def test_low(self):
            self.cls.low = self.low
            for _ in range(self.n_runs):
                self.cls.change()
                self.assertTrue(self.cls.value >= self.low)

        def test_high(self):
            self.cls.high = self.high
            for _ in range(self.n_runs):
                self.cls.change()
                self.assertTrue(self.cls.value <= self.high)

        def test_low_high(self):
            self.cls.low = self.low
            self.cls.high = self.high
            for _ in range(self.n_runs):
                self.cls.change()
                self.assertTrue(self.cls.value >= self.low)
                self.assertTrue(self.cls.value <= self.high)

        def test_low_high_negative(self):
            self.low = -2.7
            self.high = -0.5
            self.test_low_high()


class TestChangingFloat(BaseTestChangingNumber.TestChangingNumber):

    def setUp(self) -> None:
        super().setUp()

        self.initial_value = 2.5
        self.low = 0.5
        self.high = 2.7
        self.seed = 1

        self.cls = ChangingFloat(
            'test_float',
            self.initial_value, self.seed,
        )


class TestChangingInt(BaseTestChangingNumber.TestChangingNumber):

    def setUp(self) -> None:
        super().setUp()

        self.initial_value = 4
        self.low = 1
        self.high = 12
        self.seed = 1

        self.cls = ChangingInt(
            'test_int',
            self.initial_value, self.seed,
        )


if __name__ == '__main__':
    unittest.main()
