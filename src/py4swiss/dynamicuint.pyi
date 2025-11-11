from __future__ import annotations

class DynamicUint:
    """
    An unsigned integer with a dynamic size.

    This class is implemented in C++ as a sequence of any number of 32-bit integers and can thus be used to represent
    arbitrarily large integer values. Note that the number of 32-bit integer parts needs to be manually adjusted. If the
    integer gets too large to hold with the current size, an overflow will occur. Any interaction with instances of this
    class and python integers will work properly only for integers with up to 32 bits.
    """

    def __init__(self, value: int | DynamicUint = 0) -> None:
        """
        Create a new instance by either copying from a given instance or by creating a new instance with a single 32-bit
        integer part and assigning the given integer value.
        """
        ...

    def __add__(self, other: DynamicUint) -> DynamicUint:
        """
        Call 'add' pointwise on all 32-bit integer parts. Note that this will not work properly if the number of parts
        varies.
        """
        ...

    def __sub__(self, other: DynamicUint) -> DynamicUint:
        """
        Call 'subtract' pointwise on all 32-bit integer parts. Note that this will not work properly if the number of
        parts varies.
        """
        ...

    def __or__(self, other: int) -> DynamicUint:
        """Call 'or' on the lowest 32-bit part and the given integer."""
        ...

    def __and__(self, other: int) -> DynamicUint:
        """Call 'and' on the lowest 32-bit part and the given integer."""
        ...

    def __lshift__(self, shift: int) -> DynamicUint:
        """
        Shift all 32-bit integer parts to the left by the given shift value. Bits which overflow are moved to the next
        highest part accordingly. Bits that overflow from the highest part are ignored.
        """
        ...

    def __rshift__(self, shift: int) -> DynamicUint:
        """
        Shift all 32-bit integer parts to the right by the given shift value. Bits which underflow are moved to the next
        lowest part accordingly. Bits that underflow from the lowest part are ignored.
        """
        ...

    def __iadd__(self, other: DynamicUint) -> DynamicUint:
        """In-place version of __add__()."""
        ...

    def __isub__(self, other: DynamicUint) -> DynamicUint:
        """In-place version of __sub__()."""
        ...

    def __ior__(self, other: int) -> DynamicUint:
        """In-place version of __or__()."""
        ...

    def __iand__(self, other: int) -> DynamicUint:
        """In-place version of __and__()."""
        ...

    def __ilshift__(self, shift: int) -> DynamicUint:
        """In-place version of __lshift__()."""
        ...

    def __irshift__(self, shift: int) -> DynamicUint:
        """In-place version of __rshift__()."""
        ...

    def __eq__(self, other: object) -> bool:
        """Check whether all 32-bit integer parts are equal."""
        ...

    def __ne__(self, other: object) -> bool:
        """Logical negation of __eq__."""
        ...

    def __lt__(self, other: DynamicUint) -> bool:
        """Check whether the concatenation of all 32-bit integer parts is less than that of the given one."""
        ...

    def __le__(self, other: DynamicUint) -> bool:
        """Check whether the concatenation of all 32-bit integer parts is less than or equal that of the given one."""
        ...

    def __gt__(self, other: DynamicUint) -> bool:
        """
        Check whether the concatenation of all 32-bit integer parts is greater than or equal that of the given one.
        """
        ...

    def __ge__(self, other: DynamicUint) -> bool:
        """
        Check whether the concatenation of all 32-bit integer parts is greater than or equal that of the given one.
        """
        ...

    def __bool__(self) -> bool:
        """Check whether any of the 32-bit integer parts is not 0."""
        ...

    def __str__(self) -> str:
        """Return the concatenation of all 32-bit integer parts as a binary string."""
        ...

    def __repr__(self) -> str:
        """Return the concatenation of all 32-bit integer parts as a binary string."""
        ...

    def to_binary(self) -> str:
        """Return the concatenation of all 32-bit integer parts as a binary string."""
        ...

    def shift_grow(self, shift: int) -> DynamicUint:
        """
        Shift all 32-bit integer parts to the left by the given shift value. Bits which overflow are moved to the next
        highest part accordingly. If an overflow from the highest part occurs, a new highest part is added to capture
        the overflow.
        """
        ...
