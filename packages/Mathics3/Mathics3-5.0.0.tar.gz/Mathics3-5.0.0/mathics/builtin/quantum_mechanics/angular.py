"""
Angular Momentum
"""

from mathics.builtin.base import Builtin

from mathics.core.attributes import (
    listable as LISTABLE,
    numeric_function as NUMERIC_FUNCTION,
    protected as PROTECTED,
    read_protected as READ_PROTECTED,
)

class PauliMatrix(Builtin):
    """
    <dl>
      <dt>'PauliMatrix[]'
      <dd>returns the $k$th zero of the Airy function Ai($z$).
    </dl>
    """
    attributes = LISTABLE | NUMERIC_FUNCTION | PROTECTED | READ_PROTECTED
