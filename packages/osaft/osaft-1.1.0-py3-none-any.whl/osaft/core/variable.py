from abc import ABC
from collections.abc import Callable
from typing import Any, Optional

import numpy as np

from osaft import log
from osaft.core.functions import full_range


class BaseVariable(ABC):
    """ BaseVariable class defining basic methods and attributes shared between
    active and passive attributes.

    This class and its children are based on the Observer Design Pattern.
    In the present context value changes shall be tracked so
    :class:`ActiveVariable` know when their dependencies changed, and they
    need to recompute their underlying value.

    :param name: Name of the variable
    :raises: TypeError if :attr:`name` is of wrong type
    """

    def __init__(self, name: Optional[str] = None) -> None:
        """Constructor method
        """
        self._value = None
        self._variables_to_notify: list[BaseVariable] = []

        if name is None:
            self._name = 'Unnamed'
        elif isinstance(name, str):
            self._name = name
        else:
            raise TypeError(f'name is of type {type(name)} instead of str')

    @property
    def name(self) -> str:
        """Returns name of the variable.

        :setter: sets :attr:`~osaft.variable.BaseVariable._name`
        """
        return self._name

    @property
    def value(self) -> Any:
        """Value of the attribute

        :setter: just defined in :class:`PassiveVariable`
        :getter: returns/computes the value of the instance
        """
        return self._value

    def notify(self) -> None:
        """Notifies all items in :attr:`BaseVariable._variables_to_notify` that
        a dependent value changed. Just the information of a changed dependency
        is passed.
        """
        log.debug(f'Variable {repr(self)} notifies:')
        for att in self._variables_to_notify:
            log.debug(f'attribute: {att}')
            att._change_update_status()

    def _link(self, input_variable: Any) -> None:
        """Links the inputs to self, so it knows who needs to update when
        :attr:`BaseVariable.value` changes.

        :param input_variable:
        """
        log.info(
            f'Variables linked: {str(input_variable)} depends on'
            f' {str(self)}',
        )
        self._variables_to_notify.append(input_variable)

    @staticmethod
    def _check_types(
        inputs: tuple,
    ) -> None:
        """ Checks if elements of :attr:`inputs` are of type
        :class:`BaseVariable`

        :param inputs: iterable to be checked
        :raises: TypeError if :attr:`inputs` is of wrong type
        """
        for item in inputs:
            if not isinstance(item, BaseVariable):
                out = f'{item} is of type {type(item)} instead of BaseVariable'
                raise TypeError(out)


class PassiveVariable(BaseVariable):
    """ Passive variable without any computation dependencies

    :param val: initial value
    :param name: Name of the variable
    """

    def __init__(
        self, val: Any, name: Optional[str] = None,
    ) -> None:
        """Constructor method
        """
        super().__init__(name)
        self.value = val

        # no if clause needed because last in inheritance
        log.debug(f'Creating {self}')

    @BaseVariable.value.setter
    def value(self, value: Any) -> None:
        """
        Checks if :attr:`BaseVariable._value` is already equal to value.
        If not, first :attr:`BaseVariable._value` is set to `value`
        and then all item in :attr:`BaseVariable._variables_to_notify` are
        notified.

        :param value: new value
        """
        has_changed = True
        if self._value is not None:
            try:
                L1 = len(self._value)
            except TypeError:
                L1 = 0
            try:
                L2 = len(value)
            except TypeError:
                L2 = 0

            if L1 == 0 and L2 == 0:
                has_changed = self._value != value
            elif L1 == L2:
                has_changed = not np.alltrue(self._value == value)

        if has_changed:
            log.debug(f'value change of {repr(self)} to {value}')
            self._value = value
            self.notify()

    def __repr__(self) -> str:
        return f'PassiveVariable(name={self.name}, value={self.value})'

    def __str__(self):
        return f'{self.name} = {self.value}'


class BaseActiveVariable(BaseVariable, ABC):
    """ Base for variables that depended on at least one :class:`.BaseVariable`

    :param functionCall: function signature that defines how
        :attr:`ActiveVariable._value` is computed
        Callable[[], Any]
    :param name: Name of the variable
    """
    def __init__(
        self, functionCall: Callable[[], Any], name: Optional[str] = None,
    ) -> None:
        """Constructor method
        """
        super().__init__(name)
        self._update_function = functionCall
        self._needs_update = True

        # no if clause needed because last in inheritance
        log.debug(f'Creating {self}')

    @property
    def needs_update(self) -> bool:
        """ Returns if an update is needed for the next value retrieval
        """
        return self._needs_update

    def _change_update_status(self) -> None:
        """Set :attr:`ActiveVariable._needs_update` to `True` and calls
        :meth:`BaseVariable.notify`.
        """
        log.debug(f'{repr(self)} changes _needs_update to True')
        self._needs_update = True
        self.notify()

    def is_computed_by(self, *variables: Any) -> None:
        """ Adds the notification dependencies

        :param variables: variables that are referenced in
            :meth:`~ActiveVariable._update`
        :raises: TypeError if no arguments are passed
        """
        if len(variables) == 0:
            out = 'is_computed_by() takes at least one positional argument '
            out += '(0 were given)'
            raise TypeError(out)
        self._check_types(variables)
        for variable in variables:
            variable._link(self)

    def __repr__(self) -> str:
        if not self._needs_update:
            return f'ActiveVariable(name={self.name}, value={self.value})'
        else:
            return f'ActiveVariable(name={self.name}, value=N.A.)'

    def __str__(self):
        if not self._needs_update:
            return f'{self.name} = {self.value}'
        else:
            return f'{self.name} = N.A.'


class ActiveVariable(BaseActiveVariable):
    """ Variables that depended on at least one :class:`.BaseVariable`

    :param functionCall: function signature that defines how
        :attr:`ActiveVariable._value` is computed
    :param name: Name of the variable
    """

    def __init__(
        self, functionCall: Callable[[], Any], name: Optional[str] = None,
    ) -> None:
        """Constructor method
        """
        super().__init__(functionCall, name)

    @property
    def value(self) -> Any:
        """Returns the value of the attribute. If
        :attr:`ActiveVariable.needs_update` is true, it calls
        :meth:`ActiveVariable._update` first and then changes
        :attr:`ActiveVariable._needs_update` to `False` before returning the
        value.
        """
        if self.needs_update:
            self._update()
        return self._value

    def _update(self) -> None:
        """Executes the assigned routine and outputs its value."""
        log.debug(f'{repr(self)} recomputes its value')
        self._value = self._update_function()
        self._needs_update = False
        log.debug(f'Recomputed: {repr(self)}')


class ActiveListVariable(BaseActiveVariable):
    """ ActiveVariables with an expendable list as :attr:`value`

    :param functionCall: function signature that defines how the n-the
    element of the `list` :attr:`ActiveVariable._value` is computed
    :param name: Name of the variable
    """

    def __init__(
        self, functionCall: Callable[[int], Any], name: Optional[str] = None,
    ) -> None:
        """Constructor method
        """
        super().__init__(functionCall, name)

    @property
    def value(self) -> list:
        """Returns the `list` containing the data of the instance. If
        :attr:`ActiveVariable.needs_update` is true, it calls the list is
        emptied, :attr:`ActiveVariable._needs_update` to `False` and an
        empty list is returned.
        """
        if self._needs_update:
            self._reset_value()
        return self._value

    def item(self, index: int) -> Any:
        """Returns the item stored at `item` index. If the value variable
        needs recomputation first, the whole `list` up to the index is
        recomputed. If the index does not exist then all the missing items
        up to `index` are computed.

        :param index: index
        """
        if index < len(self.value):
            return self._value[index]
        else:
            self._update(index)
            return self._value[index]

    def _update(self, index: int) -> None:
        """Computes the missing values in the list up to `index`.

        :param index: index
        """
        before = len(self._value)
        for n in full_range(before, index):
            self._value.append(self._update_function(n))
        log.debug(f'Computed: {repr(self)} up to index = {index}')
        self._needs_update = False

    def _reset_value(self):
        """Resets the value to an empty list.
        """
        log.debug(f'{repr(self)} recomputes its value')
        self._value = []


if __name__ == '__main__':
    pass
