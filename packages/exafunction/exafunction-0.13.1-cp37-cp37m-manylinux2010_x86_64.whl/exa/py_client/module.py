# Copyright Exafunction, Inc.
"""Defines the Module class."""

from typing import Dict

from exa import _C
from exa.common_pb.common_pb2 import MethodInfo
from exa.py_value.value import Value


class Module:
    """
    The Module class represents a remote module in the Exafunction system.

    Each remote module exposes one or more methods, which take in and return
    Exafunction values. Modules are created by Exafunction session, using the
    methods like Session.new_module.
    """

    def __init__(self, c: _C.Module):
        self._c = c

    def _check_valid(self):
        if not self._c.is_valid():
            raise ValueError("Module is not valid (was the session closed?)")

    def module_id(self) -> int:
        """
        Returns the module id.

        :return: The module id.
        """
        self._check_valid()
        return self._c.module_id()

    def run_method(
        self, method_name: str, raw_inputs: Dict[str, Value] = None, **inputs: Value
    ) -> Dict[str, Value]:
        """
        Runs a method on the remote module.

        :param method_name: The name of the method to run.
        :param raw_inputs: A dictionary of inputs to the method. This can be used over
            `inputs` if an input name requires special characters, such as grouped
            inputs.
        :param inputs: The inputs to the method.
        :return: The outputs of the method.
        """
        self._check_valid()
        # pylint: disable=protected-access
        cc_inputs = {k: inp._c for k, inp in inputs.items()}
        if raw_inputs is None:
            raw_inputs = {}
        for k, inp in raw_inputs.items():
            if k in cc_inputs:
                raise ValueError(f"key {k} already found in input kwargs")
            cc_inputs[k] = inp._c
        cc_outputs = self._c.run_method(method_name, cc_inputs)
        return {k: Value(out) for k, out in cc_outputs.items()}

    def run(
        self, raw_inputs: Dict[str, Value] = None, **inputs: Value
    ) -> Dict[str, Value]:
        """
        Convenience method for running the method named "run" exposed by most modules.

        Equivalent to calling run_method with the method name "run".

        :param raw_inputs: A dictionary of inputs to the method. This can be used over
            `inputs` if an input name requires special characters, such as grouped
            inputs.
        :param inputs: The inputs to the method.
        :return: The outputs of the method.
        """
        return self.run_method("run", raw_inputs=raw_inputs, **inputs)

    def ensure_local_valid(self, values: Dict[str, Value]):
        """
        Equivalent to calling ensure_local_valid on each value in the ValueMap
        to fetch its value. Using this function will generally reduce latency
        compared to fetching each value individually.

        :param values: The values to fetch.
        """

        self._check_valid()
        # pylint: disable=protected-access
        cc_values = {k: inp._c for k, inp in values.items()}
        self._c.ensure_local_valid(cc_values)

    def get_method_info(self, method_name: str = "run") -> MethodInfo:
        """
        Get information about a method, including its input and output types.

        If no method name is provided, the information for the "run" method
        is returned.

        :param method_name: The name of the method to get information about.
        :return: The method information.
        """
        self._check_valid()
        serialized_info = self._c.get_method_info(method_name)
        mi = MethodInfo()
        mi.ParseFromString(serialized_info)
        return mi

    def checkpoint(self):
        """
        Checkpoints the state of a stateful module locally. This allows the
        client and service to free up values required to recover the current
        state and also speeds up the recovery process. Checkpoints should not
        be taken too frequently if they are computationally expensive or have
        substantial network bandwidth overhead.
        """
        self._c.checkpoint()

    @property
    def id(self):
        """Returns the module ID.

        :return: The module ID.
        """
        return self._c.module_id
