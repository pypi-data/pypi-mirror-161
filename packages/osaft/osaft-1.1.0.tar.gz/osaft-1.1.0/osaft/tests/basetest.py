import time
import unittest
from abc import abstractmethod
from collections.abc import Callable, Sequence
from numbers import Number
from typing import Any, Optional, Union

import numpy as np

from osaft import WaveType
from osaft.core.frequency import Frequency
from osaft.solutions.base_solution import BaseSolution


class BaseChangingVariable:
    """Type used as attribute of a `TestCase` that is changed automatically.

        To test the observer pattern testing, attributes of classes are
        changed to ensure proper linking. If a test class has an attribute of
        type :class:`BaseChangingVariable` then the attribute of the tested
        class with the name `name` is initially set to `value`. During the
        testing the attribute is changed to a new value using the method
        `change`.

        :param name: name of the attribute in the class to be tested
        :param value: initial value of the attribute
        :param seed: seed for RNG to make testing reproducible
    """

    def __init__(
        self, name: str, value: Any,
        seed: int,
    ) -> None:
        """Constructor method
        """
        self.name = name
        self.value = value

        self.rng = np.random.default_rng(seed)

    @abstractmethod
    def change(self) -> None:
        """Randomly change `value`
        """
        pass


class ChangingFromList(BaseChangingVariable):
    """Child of :class:`BaseChangingVariable`.

    The method `change` changes `value` by choosing an item from
    :attr:`list_of_values`.

    :param name: name of the attribute in the class to be tested
    :param value: initial value of the attribute
    :param list_of_values: list of values to choose from
    :param seed: seed for RNG to make testing reproducible
    """
    _longest_list = 0

    def __init__(
        self, name: str, value: Any,
        list_of_values: Sequence[Any],
        seed: int,
    ) -> None:

        super().__init__(name, value, seed)

        self.list_of_values = list_of_values

    def _set_longest_list(self) -> None:
        if len(self.list_of_values) > self._longest_list:
            ChangingFromList._longest_list = len(self.list_of_values)

    def _reset_non_tested_values(self) -> None:
        # [*list] syntax is needed for not passing a reference but creating an
        # actual new list
        self._non_tested_values = [*self.list_of_values]

    @property
    def list_of_values(self) -> list[any]:
        return self._list_of_values

    @list_of_values.setter
    def list_of_values(self, lst: list[any]) -> None:
        self._list_of_values = lst
        self._set_longest_list()
        self._reset_non_tested_values()

    @property
    def longest_list(self) -> int:
        return ChangingFromList._longest_list

    def change(self) -> None:
        """Randomly change `value`
        """
        if len(self._non_tested_values) < 1:
            self._reset_non_tested_values()

        self.value = self.rng.choice(self._non_tested_values)
        self._non_tested_values.remove(self.value)


class ChangingBool(BaseChangingVariable):
    """Child of :class:`BaseChangingVariable`

    Child of :class:`BaseChangingVariable` for the case when value is of type
    `bool`.

    :param name: name of the attribute in the class to be tested
    :param value: initial value of the attribute
    :param seed: seed for RNG to make testing reproducible
    """

    def __init__(self, name: str, value: bool, seed: int) -> None:
        """Constructor method
        """
        super().__init__(name, value, seed)

    @abstractmethod
    def change(self) -> None:
        """Randomly change `value`
        """
        self.value = self.rng.random() > 0.5


class ChangingNumber(BaseChangingVariable):
    """Child of :class:`BaseChangingVariable`

    Child of :class:`BaseChangingVariable` for the case when value is a number.

    :param name: name of the attribute in the class to be tested
    :param value: initial value of the attribute
    :param seed: seed for RNG to make testing reproducible
    :param low: lowest value `value` is changed to
    :param high: highest value `value` is changed to
    """

    def __init__(
        self, name: str, value: Union[None, float, int], seed: int,
        low: Union[None, float, int], high: Union[float, int],
    ) -> None:
        """Constructor method
        """
        super().__init__(name, value, seed)
        self.test_inputs(value, low, high)
        self._low = low
        self._high = high

    @staticmethod
    def test_inputs(
        value: Union[None, int, float],
        low: Union[None, int, float],
        high: Union[None, int, float],
    ):
        if low is not None and high is not None:
            assert low < value < high, 'condition low < value < high not met'
        elif low is not None:
            assert low < value, 'condition low < value < high is not met'
        elif high is not None:
            assert value < high, 'condition low < value < high is not met'

    @property
    def low(self) -> Union[None, int, float]:
        return self._low

    @low.setter
    def low(self, value: Union[int, float]) -> None:
        if self.high is not None and value > self.high:
            raise ValueError(
                f'high (= {value}) needs to be larger than low '
                f'(= {self.low})',
            )
        elif value > self.value:
            self._low = value
            self.value = value
            self.change()
        else:
            self._low = value

    @property
    def high(self) -> Union[float, int]:
        return self._high

    @high.setter
    def high(self, value: Union[int, float]) -> None:
        if self.low is not None and value < self.low:
            raise ValueError(
                f'high (= {value}) needs to be larger than low '
                f'(= {self.low})',
            )
        elif value < self.value:
            self._high = value
            self.value = value
            self.change()
        else:
            self._high = value

    @abstractmethod
    def change(self) -> None:
        """Randomly change `value`
        """
        pass


class ChangingFloat(ChangingNumber):
    """Child of :class:`BaseChangingVariable`

    Child of :class:`BaseChangingVariable` for the case when value is a
    `float`.

    :param name: name of the attribute in the class to be tested
    :param value: initial value of the attribute
    :param seed: seed for RNG to make testing reproducible
    :param low: lowest value `value` is changed to
    :param high: highest value `value` is changed to
    """

    def __init__(
        self, name: str, value: float, seed: int,
        low: Optional[float] = None,
        high: Optional[float] = None,
    ) -> None:
        """Constructor method
        """
        super().__init__(name, value, seed, low, high)

    def change(self) -> None:
        """Randomly change `value`
        """
        if self.low is not None and self.high is not None:
            self.value = (
                self.low + (self.high - self.low) *
                self.rng.random()
            )
        elif self.low is not None:
            change = self.value * (self.rng.random() - 0.5)
            if self.value + change > self.low:
                self.value += change
            else:
                self.value -= change
        elif self.high is not None:
            change = self.value * (self.rng.random() - 0.5)
            if self.value + change < self.high:
                self.value += change
            else:
                self.value -= change
        else:
            self.value += (self.rng.random() - 0.5) * self.value


class ChangingInt(ChangingNumber):
    """Child of :class:`BaseChangingVariable`

    Child of :class:`BaseChangingVariable` for the case when value is an
    `int`. Default values for `low` and `high` are 0 and 100 respectively. If
    `value` is outside this range the parameters have to be set accordingly.

    :param name: name of the attribute in the class to be tested
    :param value: initial value of the attribute
    :param seed: seed for RNG to make testing reproducible
    :param low: lowest value `value` is changed to
    :param high: highest value `value` is changed to
    """

    def __init__(
        self, name: str, value: int, seed: int, low: int = 0,
        high: int = 100,
    ):
        """Constructor method
        """
        super().__init__(name, value, seed, low, high)

    def change(self) -> None:
        """Randomly change `value`
        """
        self.value = self.rng.integers(low=self.low, high=self.high)


class NumericTestCase(unittest.TestCase):

    def setUp(self) -> None:
        # Create seed
        seed = np.random.randint(1, 10000)
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    def assertAlmostEqual(
        self,
        val1: Number,
        val2: Number,
        threshold: Optional[float] = 1e-12,
        print_results: Optional[bool] = False,
        user_msg: Optional[str] = None,
    ) -> None:
        """ Asserting the relative difference of two values when num. rounding
        errors can occur

        Assertion is handled by :meth:`BaseTest._assertAlmostEqual()`

        If the values are complex, then the real and imaginary part will be
        tested separately. Also, if one of the test fails, automatically, a
        nice formatted output is generated as error message.

        :param val1: first value to be compared
        :param val2: second value to be compared
        :param threshold: threshold of relative difference, defaults to 1e-12
        :param print_results: if True the two values are printed to the console
            for easier debugging, defaults to False
        :param user_msg: custom message that is printed if the assertion fails.
        """
        if print_results:
            msg = f'\nval1     : {val1:+.8e}\n'
            msg += f'val2     : {val2:+.8e}\n'
            if not val1 == 0 and not val2 == 0:
                msg += f'rel diff.: {abs((val1 - val2) / val1):+.8e}'
            print(msg)

        self._assertAlmostEqual(val1.real, val2.real, threshold)
        if isinstance(val1, complex) or isinstance(val2, complex):
            self._assertAlmostEqual(val1.imag, val2.imag, threshold, user_msg)

    def _assertAlmostEqual(
        self, val1: float, val2: float,
        threshold: float, user_msg: Optional[str] = None,
    ) -> None:

        msg = '\nAssertion failed\n'
        if user_msg:
            msg += f'\n{user_msg}\n'

        if val1 == 0 or val2 == 0:
            msg += 'One of the values is Zero; the other not\n'
            msg += f'val1     : {val1:+.8e}\n'
            msg += f'val2     : {val2:+.8e}\n'
            test = abs(val1) < threshold and abs(val2) < threshold
            self.assertTrue(expr=test, msg=msg)
        else:
            diff = np.abs(val1 - val2)
            if np.abs(val1) > np.abs(val2):
                test = np.abs(diff / val2) < threshold
            else:
                test = np.abs(diff / val1) < threshold

            msg += 'The rel. diff. is bigger than the threshold\n'
            msg += f'val1     : {val1:+.8e}\n'
            msg += f'val2     : {val2:+.8e}\n'
            msg += f'rel diff.: {abs(diff/val1):+.8e}\n'
            msg += f'threshold: {threshold:+.8e}'

            self.assertTrue(expr=test, msg=msg)

    def random_z(self, low: float = -10, high: float = 10) -> complex:
        a = self.rng.uniform(low, high)
        b = self.rng.uniform(low, high)
        return a + b * 1j


class BaseTest(NumericTestCase):

    def setUp(self) -> None:

        # Create
        super().setUp()

        # set of all passive attributes that have a value of type float
        # that appear in classes in this module

        # Geometry
        self._R_0 = ChangingFloat('R_0', 1e-6, self.seed, low=0)
        # Frequency
        self._f = ChangingFloat('f', 1e6, self.seed, low=0)
        # Inviscid Fluid
        self._c_f = ChangingFloat('c_f', 1.5e3, self.seed, low=0)
        self._rho_f = ChangingFloat('rho_f', 1e3, self.seed, low=0)
        # Compressible Particle (Inviscid Fluid)
        self._c_s = ChangingFloat('c_s', 2.5e3, self.seed, low=0)
        # Compressible Particle (Viscous Fluid)
        self._eta_s = ChangingFloat('eta_s', 1e-3, self.seed, low=0)
        self._zeta_s = ChangingFloat('zeta_s', 1e-3, self.seed, low=0)
        # Viscous Fluid
        self._eta_f = ChangingFloat('eta_f', 1e-2, self.seed, low=1e-6)
        self._zeta_f = ChangingFloat('zeta_f', 1e-2, self.seed, low=0)
        # Viscoelastic Fluid
        self._eta_p = ChangingFloat('eta_p', 1e-3, self.seed, low=0)
        self._zeta_p = ChangingFloat('zeta_p', 1e-3, self.seed, low=0)
        self._lambda_M = ChangingFloat('lambda_M', 1e-3, self.seed, low=0)
        # Rigid Solid
        self._rho_s = ChangingFloat('rho_s', 1.5e3, self.seed, low=0)
        # Elastic solid
        self._E_s = ChangingFloat('E_s', 75e6, self.seed, low=0)
        self._nu_s = ChangingFloat('nu_s', 0.3, self.seed, low=0, high=0.49)
        # Background Field
        self._p_0 = ChangingFloat('p_0', 1e5, self.seed, low=0)
        self._position = ChangingFloat(
            'position', np.pi / 4, self.seed, low=0, high=2 * np.pi,
        )
        self._wave_type = ChangingFromList(
            'wave_type', WaveType.STANDING,
            WaveType, self.seed,
        )

        self.test_variables = {
            # Geometry
            self._R_0,
            # Frequency
            self._f,
            # Inviscid Fluid
            self._c_f,
            self._rho_f,
            # Compressible Particle (Inviscid Fluid)
            self._c_s,
            self._rho_s,
            self._eta_s,
            self._zeta_s,
            # Viscous Fluid
            self._eta_f,
            self._zeta_f,
            # Viscoelastic Fluid
            self._eta_p,
            self._zeta_p,
            self._lambda_M,
            # Elastic solid
            self._E_s,
            self._nu_s,
            # Background Field
            self._p_0,
            self._position,
            self._wave_type,
        }

        # Frequency Class
        self.frequency = Frequency(self.f)

        # List of classes to be tests
        self.list_cls = []

        # timing
        self._time = time.time()

        # Runs
        self._n_runs = self._wave_type.longest_list

    @property
    def n_runs(self) -> int:
        return self._n_runs

    @n_runs.setter
    def n_runs(self, val) -> None:
        if val < self._wave_type.longest_list:
            raise ValueError(
                'n_runs must be greater than the longest '
                'list of ChangingFromList._longest_list',
            )
        else:
            self._n_runs = val

    def tearDown(self) -> None:
        run_time = time.time() - self._time
        print(f'\n\trun_time: {run_time*1e3:9.4f}ms', end=' ', flush=True)
        if run_time > 0.1:
            print('>>>>TEST TOOK LONGER THAN 100ms<<<<', end=' ', flush=True)

    def test_name_attribute(self) -> None:
        if hasattr(self, 'cls'):
            if isinstance(self.cls, BaseSolution):
                self.assertTrue(self.cls.name != '')

    def test_copy(self) -> None:
        if hasattr(self, 'cls'):
            if isinstance(self.cls, BaseSolution):
                tmp = self.cls.copy()
                self.assertTrue(type(self.cls) == type(tmp))
                self.assertFalse(self.cls is tmp)

    # -------------------------------------------------------------------------
    # Generic test methods for properties and methods
    # -------------------------------------------------------------------------

    def _test_properties(
            self,
            list_of_properties: list[str],
            threshold: float = 1e-12,
    ) -> None:
        """Tests the properties inside `list_of_properties` of self & self.cls

        If a test fails the name of the failing property is printed.

        :param list_of_properties: list of properties to be tested
        :param threshold: comparing threshold for the whole list
        """

        for name in list_of_properties:
            with self.subTest(property=name):
                self.do_testing(
                    func_1=lambda: getattr(self, name),
                    func_2=lambda: getattr(self.cls, name),
                    threshold=threshold,
                )

    def _test_methods_n(
            self,
            dict_of_methods: dict[str, dict[tuple[Any]]],
            n_end: int = 5,
            threshold: float = 1e-12,
            zero: Optional[float] = None,
    ) -> None:
        """Tests the methods inside `dict_of_methods` of self & self.cls

        All methods have as first argument `n`. The key of the dict is the name
        of the methods. The `value` of the dict are the optional additional
        arguments.  If `value` == None, then it is a method solely depending on
        `n`.

        If a test fails the name of the failing method is printed.

        :param dict_of_methods: dict of methods and additional arguments to be
            tested
        :param n_end: n in [0, 1, ..., n_end]; tested in reversed order
        :param threshold: comparing threshold for the whole dict
        :param threshold: value below which test values are assumed to be zero
        """

        for method, args in dict_of_methods.items():
            func_1 = getattr(self, method)
            func_2 = getattr(self.cls, method)
            for n in reversed(np.arange(n_end)):

                if args is not None:
                    if isinstance(args, tuple):
                        arg = (n, *args)
                    else:
                        arg = (n, args)
                else:
                    arg = (n,)

                with self.subTest(method=method, arguments=arg):
                    self.do_testing(
                        func_1=func_1, args_1=arg,
                        func_2=func_2, args_2=arg,
                        threshold=threshold,
                    )

    # -------------------------------------------------------------------------
    # Getters & Setters
    # -------------------------------------------------------------------------

    @property
    def R_0(self) -> float:
        return self._R_0.value

    @R_0.setter
    def R_0(self, value: float) -> None:
        self._R_0.value = value

    @property
    def f(self) -> float:
        return self._f.value

    @f.setter
    def f(self, value: float) -> None:
        self._f.value = value

    @property
    def c_f(self) -> float:
        return self._c_f.value

    @c_f.setter
    def c_f(self, value: float) -> None:
        self._c_f.value = value

    @property
    def rho_f(self) -> float:
        return self._rho_f.value

    @rho_f.setter
    def rho_f(self, value: float) -> None:
        self._rho_f.value = value

    @property
    def c_s(self) -> float:
        return self._c_s.value

    @c_s.setter
    def c_s(self, value: float) -> None:
        self._c_s.value = value

    @property
    def eta_s(self) -> float:
        return self._eta_s.value

    @eta_s.setter
    def eta_s(self, value: float) -> None:
        self._eta_s.value = value

    @property
    def zeta_s(self) -> float:
        return self._zeta_s.value

    @zeta_s.setter
    def zeta_s(self, value: float) -> None:
        self._eta_s.value = value

    @property
    def rho_s(self) -> float:
        return self._rho_s.value

    @rho_s.setter
    def rho_s(self, value: float) -> None:
        self._rho_s.value = value

    @property
    def eta_f(self) -> float:
        return self._eta_f.value

    @eta_f.setter
    def eta_f(self, value: float) -> None:
        self._eta_f.value = value

    @property
    def zeta_f(self) -> float:
        return self._zeta_f.value

    @zeta_f.setter
    def zeta_f(self, value: float) -> None:
        self._zeta_f.value = value

    @property
    def eta_p(self) -> float:
        return self._eta_p.value

    @eta_p.setter
    def eta_p(self, value: float) -> None:
        self._eta_p.value = value

    @property
    def zeta_p(self) -> float:
        return self._zeta_p.value

    @zeta_p.setter
    def zeta_p(self, value: float) -> None:
        self._zeta_p.value = value

    @property
    def lambda_M(self) -> float:
        return self._lambda_M.value

    @lambda_M.setter
    def lambda_M(self, value: float) -> None:
        self._lambda_M.value = value

    @property
    def E_s(self) -> float:
        return self._E_s.value

    @E_s.setter
    def E_s(self, value: float) -> None:
        self._E_s.value = value

    @property
    def nu_s(self) -> float:
        return self._nu_s.value

    @nu_s.setter
    def nu_s(self, value: float) -> None:
        self._nu_s.value = value

    @property
    def p_0(self) -> float:
        return self._p_0.value

    @p_0.setter
    def p_0(self, value: float) -> None:
        self._p_0.value = value

    @property
    def position(self) -> float:
        return self._position.value

    @position.setter
    def position(self, value: float) -> None:
        self._position.value = value

    @property
    def wave_type(self) -> WaveType:
        return self._wave_type.value

    @wave_type.setter
    def wave_type(self, value: WaveType) -> None:
        self._wave_type.value = value

    # -----------------------------------------------------------------------------
    # Tests
    # -----------------------------------------------------------------------------

    def do_testing(
        self, func_1: Callable, func_2: Callable,
        args_1: Optional[Any] = None,
        args_2: Optional[Any] = None,
        threshold: float = 1e-10,
        zero: Optional[float] = None,
    ) -> None:
        """Compares the outputs of `func_1` against `func_2`.

        The variables in
        :attr:`BaseTest.test_variables` are changed and assigned one
        after the other to test all dependencies. This procedure is repeated
        :attr:`BaseTest.n_runs` times. Arguments to the functions can be
        passed with `args_1` and `args_2` to the respective functions.
        Testing is handled by :meth:`BaseTest._test_variables()` and changing
        of the values :meth:`BaseTest.change_and_assign_single_variable`

        In order to test properties of a class the following syntax is used:

        .. highlight:: python

        self.do_testing(lambda: self.cls.some_property, self.some_function)

        :param func_1: first function
        :param func_2: second function
        :param args_1: arguments for first function
        :param args_2: arguments for second functions
        :param threshold: threshold for failing the test, defaults to 1e-12
        :param zero: value below which test values are assumed to be zero
        """
        self.assign_parameters()
        self._test_variables(
            func_1, args_1, func_2, args_2,
            threshold, zero,
        )
        for _ in np.arange(self.n_runs):
            for var in self.test_variables:
                if self._check_if_has_attr(var.name):
                    with self.subTest(msg=f'Changing {var.name}'):
                        self.change_and_assign_single_variable(var)
                        self._test_variables(
                            func_1, args_1, func_2, args_2,
                            threshold, zero,
                        )

    def _check_if_has_attr(self, name: str):
        """Check if any class in list_cls has the attribute `name`

        param name: name of the attribute
        """
        list_hasattr = [hasattr(cls, name) for cls in self.list_cls]
        return np.any(list_hasattr)

    def _test_variables(
        self,
        func_1: Callable,
        args_1: tuple,
        func_2: Callable,
        args_2: tuple,
        threshold: Optional[float] = 1e-12,
        zero: Optional[float] = None,
    ) -> None:
        """Checks if func_1(args) is almost equal to func_2 args

        Checks if func_1(args) is almost equal to func_2 args with tolerance
        `threshold`. Values below `zero` are assumed to be 0.

        :param func_1: first function
        :param args_1: arguments for the first function
        :param func_2: second function
        :param args_2: arguments for the second function
        :param threshold: tolerance
        "param zero: value below which test values are assumed to be zero
        """
        # check type of parameters1
        first = self._get_value(func_1, args_1)
        second = self._get_value(func_2, args_2)

        if zero is not None:
            first = 0 if abs(first) < zero else first
            second = 0 if abs(second) < zero else second

        self.assertAlmostEqual(first, second, threshold=threshold)

    @staticmethod
    def _get_value(func: Callable, args: tuple):
        """Get the value of the function `func` with arguments `arg`

        :param func: function
        :param args: arguments
        """
        if args is None:
            out = func()
        elif isinstance(args, tuple):
            out = func(*args)
        else:
            out = func(args)
        return out

    def assign_parameters(self) -> None:
        """Assigns the changed parameters to all instances

        This needs to be implemented in each derived object of `BaseTest`

        :raises NotImplementedError: Needs to be implemented in the
            derived object of BaseTest
        """
        for var in self.test_variables:
            for cls in self.list_cls:
                if hasattr(cls, var.name):
                    setattr(cls, var.name, var.value)

    def change_and_assign_single_variable(
        self, var: BaseChangingVariable,
    ) -> None:
        """`var` is changed and its value is assigned so the attribute with
        the name `var.name`.

        The method `var.change` is called which randomly changes
        `var.value`. `var.value` is then assigned to the attribute of `self`
        with the name `var.name`.
        Assigning is handled by :meth:`BaseTest.assign_parameters()`

        :param var: Attribute name
        """
        var.change()
        self.assign_parameters()

    def assertAlmostEqual(
        self,
        val1: Number,
        val2: Number,
        threshold: Optional[float] = 1e-12,
        print_results: Optional[bool] = False,
    ) -> None:

        super().assertAlmostEqual(
            val1, val2, threshold, print_results,
            user_msg=f'\nseed number {self.seed}\n',
        )


if __name__ == '__main__':
    pass
