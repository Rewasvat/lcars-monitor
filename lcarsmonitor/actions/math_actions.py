import re
import math
import libasvat.imgui.editors.primitives as primitives
from lcarsmonitor.actions.actions import Action, ActionColors
from libasvat.imgui.nodes import input_property, output_property, DataPin, DataPinState, PinKind, SelectableTypeMixin
from libasvat.imgui.general import not_user_creatable
from libasvat.imgui.math import Vector2


@not_user_creatable
class Operation(Action):
    """Base class for math-related actions."""

    def __init__(self, create_data_pins=True):
        super().__init__(False, create_data_pins)
        self.node_header_color = ActionColors.Operations


class Sum(Operation):
    """Sum values together.

    Accepts ints, floats or Vector2s as inputs. However the result type depends on the inputs:
    * If one of them is a Vector2, then the result will be a vector as well.
    * Otherwise if one input is a float, the result will be a float.
    * Otherwise all inputs would be ints, and thus the result will also be an integer.
    """

    @input_property(dynamic_input_pins=True)
    def values(self) -> list[float | Vector2 | int]:
        """The values to sum"""
        return []

    @output_property(use_prop_value=True)
    def result(self) -> float | Vector2 | int:
        """The result of the sum of our input values"""
        vals = self.values
        types = [type(v) for v in vals]
        default = 0
        if Vector2 in types:
            default = Vector2()
        elif float in types:
            default = 0.0
        return sum(vals, default)


class Subtract(Operation):
    """Subtract given values.

    Accepts ints, floats or Vector2s as inputs. However the result type depends on the inputs:
    * If one of them is a Vector2, then the result will be a vector as well.
    * Otherwise if one input is a float, the result will be a float.
    * Otherwise all inputs would be ints, and thus the result will also be an integer.
    """

    @input_property(dynamic_input_pins=True)
    def values(self) -> list[float | Vector2 | int]:
        """The values to subtract"""
        return []

    @output_property(use_prop_value=True)
    def result(self) -> float | Vector2 | int:
        """The result of the subtraction of our input values"""
        vals = self.values
        if len(vals) <= 0:
            return 0.0
        ret = vals[0]
        for v in vals[1:]:
            if isinstance(v, Vector2) and not isinstance(ret, Vector2):
                ret = v - ret
            else:
                ret -= v
        return ret


class Multiply(Operation):
    """Multiply given values.

    Accepts ints, floats or Vector2s as inputs. However the result type depends on the inputs:
    * If one of them is a Vector2, then the result will be a vector as well.
    * Otherwise if one input is a float, the result will be a float.
    * Otherwise all inputs would be ints, and thus the result will also be an integer.
    """

    @input_property(dynamic_input_pins=True)
    def values(self) -> list[float | Vector2 | int]:
        """The values to multiply"""
        return []

    @output_property(use_prop_value=True)
    def result(self) -> float | Vector2 | int:
        """The result of the multiplication of our input values"""
        vals = self.values
        if len(vals) <= 0:
            return 0.0
        ret = vals[0]
        for v in vals[1:]:
            if isinstance(v, Vector2) and not isinstance(ret, Vector2):
                ret = v * ret
            else:
                ret *= v
        return ret


class Divide(Operation):
    """Performs division between A and B.

    Notes:
    * If the divisor is 0, the result will be a ``nan``.
    * If the divisor is a Vector2, but the dividend isn't, then the result will be a ``nan``.
    """

    @input_property()
    def dividend(self) -> float | Vector2 | int:
        """The division's dividend."""

    @input_property()
    def divisor(self) -> float | Vector2 | int:
        """The division's divisor."""

    @output_property(use_prop_value=True)
    def result(self) -> float | Vector2 | int:
        """The resulting division's quotient."""
        if self.divisor == 0:
            return math.nan
        if isinstance(self.divisor, Vector2):
            if not isinstance(self.dividend, Vector2) or self.divisor.x == 0 or self.divisor.y == 0:
                return math.nan
        return self.dividend / self.divisor


class Concatenate(Operation):
    """Concatenate various strings together.

    Equivalent to Python's ``string.join`` method.
    """

    @input_property(dynamic_input_pins=True)
    def strings(self) -> list[str]:
        """The strings to join."""
        return []

    @input_property()
    def separator(self) -> str:
        """The text to use as separator when joining the strings."""
        return ""

    @output_property(use_prop_value=True)
    def result(self) -> str:
        """The concatenated string."""
        return self.separator.join(self.strings)


class FormatString(Operation):
    """Formats a string with given input values."""

    def __init__(self):
        self._subpins: dict[str, DataPin] = {}
        super().__init__()

    @input_property()
    def base(self) -> str:
        """Base format string.

        Any ``{name}`` tags in this string will become input pins to allow the node to receive the
        value for the ``name`` variable.
        """

    @base.setter
    def base(self, value: str):
        new_keys = set(self.get_base_keys(value))
        cur_keys = set(self._subpins.keys())
        missing = new_keys - cur_keys
        for name in missing:
            self.create_subpin(name)
        removed = cur_keys - new_keys
        for name in removed:
            pin = self._subpins.pop(name)
            pin.delete()

    @output_property(use_prop_value=True)
    def result(self) -> str:
        """The formatted string."""
        try:
            return self.base.format(**self.get_format_args())
        except ValueError:
            return self.base + "\n<!INVALID FORMAT!>"
        except IndexError:
            return self.base + "\n<!UNSUPPORTED POSITIONAL ARG!>"

    def get_format_args(self) -> dict[str, str]:
        """Gets the values for all args for our ``self.base`` format string from our subpins for each arg.

        Returns:
            dict[str, str]: a dict of {arg key -> value} to use to format our self.base string.
        """
        return {key: pin.get_value() for key, pin in self._subpins.items()}

    def get_base_keys(self, value: str = None) -> list[str]:
        """Gets a list of keys from ``{key}`` tags in a format string.

        Args:
            value (str, optional): A format string to check. Defaults to None, in which case we'll use our ``self.base`` string.

        Returns:
            list[str]: list of keys
        """
        return re.findall(r"[{]([^:}]+)[^}]*[}]", value or self.base)

    def create_subpin(self, name: str):
        """Creates a new string input sub-pin in this node with the given name.
        These subpins are meant to represent the args the user has defined in the ``self.base`` format string.

        Args:
            name (str): sub-pin name.
        """
        tooltip = f"Input value for the '{name}' tag in the BASE format string."
        state = DataPinState(name, PinKind.input, tooltip, str)
        pin = DataPin(self, state)
        self.add_pin(pin)
        self._subpins[name] = pin


class FormatPercent(Operation):
    """Formats a percent value (a float in [0,1] range) to a proper string"""

    @input_property()
    def percent(self) -> float:
        """The percent value in [0,1] range"""

    @output_property(use_prop_value=True)
    def text(self):
        """The percent value, formatted as a string from 0% to 100% with up to 2 decimal plates."""
        return f"{self.percent*100.0:.2f}%"


class AND(Operation):
    """Performs logical AND operation between ``A`` and ``B``."""

    @input_property()
    def a(self) -> bool:
        """Left value for operation ``A and B``"""

    @input_property()
    def b(self) -> bool:
        """Right value for operation ``A and B``"""

    @output_property(use_prop_value=True)
    def result(self) -> bool:
        """Result of ``A and B``"""
        return self.a and self.b


class OR(Operation):
    """Performs logical OR operation between ``A`` and ``B``."""

    @input_property()
    def a(self) -> bool:
        """Left value for operation ``A or B``"""

    @input_property()
    def b(self) -> bool:
        """Right value for operation ``A or B``"""

    @output_property(use_prop_value=True)
    def result(self) -> bool:
        """Result of ``A or B``"""
        return self.a or self.b


class NOT(Operation):
    """Performs logical NOT operation with the given value."""

    @input_property()
    def value(self) -> bool:
        """Value to negate."""

    @output_property(use_prop_value=True)
    def result(self) -> bool:
        """Result of ``not value``."""
        return not self.value


class GreaterThan(SelectableTypeMixin, Operation):
    """Performs mathematical ``>`` comparison between two values."""

    def __init__(self):
        super().__init__(False)
        self._use_equals: bool = False
        self.value_type = float
        self.create_data_pins_from_properties()

    @primitives.bool_property()
    def use_equals(self) -> bool:
        """If true, will use equals comparison along with ``>``, thus performing ``>=``."""
        return self._use_equals

    @use_equals.setter
    def use_equals(self, value: bool):
        self._use_equals = value

    @input_property()
    def a(self):
        """Left value for comparison ``A > B``"""
        return self.value_type()

    @input_property()
    def b(self):
        """Right value for comparison ``A > B``"""
        return self.value_type()

    @output_property(use_prop_value=True)
    def result(self) -> bool:
        """Result of ``A > B``"""
        if self.use_equals:
            return self.a >= self.b
        return self.a > self.b

    def render_edit_details(self):
        super().render_edit_details()
        type(self).use_equals.render_editor(self)


class LessThan(SelectableTypeMixin, Operation):
    """Performs mathematical ``<`` comparison between two values."""

    def __init__(self):
        super().__init__(False)
        self._use_equals: bool = False
        self.value_type = float
        self.create_data_pins_from_properties()

    @primitives.bool_property()
    def use_equals(self) -> bool:
        """If true, will use equals comparison along with ``<``, thus performing ``<=``."""
        return self._use_equals

    @use_equals.setter
    def use_equals(self, value: bool):
        self._use_equals = value

    @input_property()
    def a(self):
        """Left value for comparison ``A < B``"""
        return self.value_type()

    @input_property()
    def b(self):
        """Right value for comparison ``A < B``"""
        return self.value_type()

    @output_property(use_prop_value=True)
    def result(self) -> bool:
        """Result of ``A < B``"""
        if self.use_equals:
            return self.a <= self.b
        return self.a < self.b

    def render_edit_details(self):
        super().render_edit_details()
        type(self).use_equals.render_editor(self)


class Equals(SelectableTypeMixin, Operation):
    """Performs logical ``==`` (is equal to) comparison between two values."""

    def __init__(self):
        super().__init__(False)
        self.value_type = float
        self.create_data_pins_from_properties()

    @input_property()
    def a(self):
        """Left value for comparison ``A == B``"""
        return self.value_type()

    @input_property()
    def b(self):
        """Right value for comparison ``A == B``"""
        return self.value_type()

    @output_property(use_prop_value=True)
    def result(self) -> bool:
        """Result of ``A == B``"""
        return self.a == self.b


class DifferentThan(SelectableTypeMixin, Operation):
    """Performs logical ``!=`` (is different than) comparison between two values."""

    def __init__(self):
        super().__init__(False)
        self.value_type = float
        self.create_data_pins_from_properties()

    @input_property()
    def a(self):
        """Left value for comparison ``A != B``"""
        return self.value_type()

    @input_property()
    def b(self):
        """Right value for comparison ``A != B``"""
        return self.value_type()

    @output_property(use_prop_value=True)
    def result(self) -> bool:
        """Result of ``A != B``"""
        return self.a != self.b
