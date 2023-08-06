# Copyright 2022 Jasper Spaans <j@jasper.es>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
import math
import numbers
import time
import typing

import attrs
import attrs.converters

log = logging.getLogger(__name__)

LN2 = math.log(2)


@attrs.define()
class Deca:
    """Decaying numbers

    This data structure can be used to represent values that decay over time.

    It offers the standard mathematical operators to make them work a
    bit like regular numbers:
     - addition and substraction are supported for pairs of Deca
     - multiplication and division is supported between Deca and real numbers

    Equality and ordering operators also work as expected, and take
    care to compare the Decas at the same point in time.

    Binary operators for Deca instances with different half_life's are not supported.
    """

    value: float
    half_life: float
    timestamp: float = attrs.field(
        default=None,
        converter=attrs.converters.default_if_none(factory=time.time),  # type: ignore
    )

    def at(self, timestamp: float | None = None) -> float:
        """Return the value at a point in time (defaulting to now).

        Accepts an optional ``timestamp`` argument for returning the
        value at a point in time that is not now.

        Refuses to go back in time.
        """
        if timestamp is None:
            timestamp = time.time()
        delta_t = timestamp - self.timestamp
        if delta_t < 0:
            raise ValueError(
                'Refusing to update to a timestamp that lies before the last update'
            )
        if delta_t == 0:
            return self.value
        return self.value * math.exp(-LN2 * delta_t / self.half_life)

    def inc(self, increment: float, timestamp: float | None = None) -> None:
        """Recalculate value at ``timestamp`` and increment by ``increment``"""
        if timestamp is None:
            timestamp = time.time()
        self.value = self.at(timestamp) + increment
        self.timestamp = timestamp

    def __matmul__(self, timestamp: float | tuple[()] | None = None) -> float:
        """Syntactic sugar as an alternative to ``.at(..)``

        This enables the delightful notations
          d@() instead of d.at()
          d@ts instead of d.at(ts)

        Unfortunately, uncompromising codemods make it look ugly with whitespace.
        """
        if isinstance(timestamp, tuple):
            return self.at()
        return self.at(timestamp)

    def _assert_half_life_equal(self, other: Deca) -> None:
        if self.half_life != other.half_life:
            raise ValueError('Cannot add Deca instances with unequal half_life valus')

    def __add__(self, other: Deca | typing.Literal[0]) -> Deca:
        if other == 0:
            return attrs.evolve(self)
        if not isinstance(other, Deca):
            return NotImplemented
        self._assert_half_life_equal(other)
        timestamp = max(self.timestamp, other.timestamp)
        return attrs.evolve(
            self, value=self.at(timestamp) + other.at(timestamp), timestamp=timestamp
        )

    def __radd__(self, other: typing.Literal[0]) -> Deca:
        # This awful hack is here to support sum(list-of-deca)
        if other == 0:
            return attrs.evolve(self)
        return NotImplemented

    def __sub__(self, other: Deca) -> Deca:
        if not isinstance(other, Deca):
            return NotImplemented
        self._assert_half_life_equal(other)
        timestamp = max(self.timestamp, other.timestamp)
        return attrs.evolve(
            self, value=self.at(timestamp) - other.at(timestamp), timestamp=timestamp
        )

    def __mul__(self, other: numbers.Real) -> Deca:
        if isinstance(other, numbers.Real):
            return attrs.evolve(self, value=self.value * other)
        return NotImplemented

    def __rmul__(self, other: numbers.Real) -> Deca:
        if isinstance(other, numbers.Real):
            return attrs.evolve(self, value=self.value * other)
        return NotImplemented

    def __imul__(self, other: numbers.Real) -> Deca:
        if isinstance(other, numbers.Real):
            self.value *= other
            return self
        return NotImplemented

    def __truediv__(self, other: numbers.Real) -> Deca:
        if isinstance(other, numbers.Real):
            return attrs.evolve(self, value=self.value / other)
        return NotImplemented

    def __itruediv__(self, other: numbers.Real) -> Deca:
        if isinstance(other, numbers.Real):
            self.value /= other
            return self
        return NotImplemented

    def __lt__(self, other: Deca) -> bool:
        if not isinstance(other, Deca):
            return NotImplemented
        if self.half_life != other.half_life:
            raise ValueError(
                'Cannot compare Deca instances with unequal half_life valus'
            )
        if self.timestamp == other.timestamp:
            return self.value < other.value
        if self.timestamp > other.timestamp:
            return self.value < other.at(self.timestamp)
        return self.at(other.timestamp) < other.value


@attrs.define()
class DecaFactory:
    """Decaying Float Factory"""

    half_life: float

    def __call__(self, value: float, timestamp: float | None = None) -> Deca:
        return Deca(value, self.half_life, timestamp)
