# Copyright 2022 Jasper Spaans <j@jasper.es>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import time

import pytest

from deca import Deca, DecaFactory


@pytest.fixture(scope='session')
def df() -> DecaFactory:
    half_life = 4
    return DecaFactory(half_life)


@pytest.fixture(scope='session')
def d(df: DecaFactory) -> Deca:
    value = 1
    now = time.time()

    return df(value, now)


def test_basics() -> None:
    """Instantiation and getting values works."""

    before = time.time()
    # keyword arguments for construction works
    d1 = Deca(value=1, half_life=4, timestamp=before)

    # positional arguments for construction works
    d2 = Deca(1, 4, before)

    # instantiation without a timestamp uses time.time()
    d3 = Deca(value=1, half_life=4)
    after = time.time()
    # as some people may start twitching when they see mocks, do an
    # indirect test assuming ``time.time()`` is monotonically increasing.
    assert before <= d3.timestamp <= after

    # equality just works thanks to attrs
    assert d1 == d2

    # the .at() function returns the value with decay having happened
    # and Deca instances have value, timestamp and half_life attributes
    assert d1.at(d1.timestamp) == d1.value
    assert d1.at(d1.timestamp + d1.half_life) == d1.value / 2


def test_comparisons() -> None:
    """Comparing Deca instances works"""
    now = time.time()
    d1 = Deca(value=1, half_life=4, timestamp=now)
    d2 = Deca(value=1, half_life=4, timestamp=now)
    d3 = Deca(value=2, half_life=4, timestamp=now)
    d4 = Deca(value=4, half_life=5, timestamp=now)
    assert d1 == d2
    assert d2 < d3
    with pytest.raises(TypeError):
        d3 < 1  # type: ignore  # mypy is drunk
        assert False, 'Comparing Deca instances to other types should fail'
    with pytest.raises(ValueError):
        d2 < d4
        assert False, 'Comparing Deca instances with different half_lifes should fail'

    assert d3.value != d3  # type: ignore  # mypy is drunk


def test_matmul(d: Deca) -> None:
    """The @ operator works."""

    # fmt: off
    before = time.time()
    value = d@()
    after = time.time()

    assert d@(before) == d.at(before)
    assert d@(after) == d.at(after)

    # assuming ``time.time()`` is monotonically increasing
    assert d@after < value < d@before
    # fmt: on


def test_addition(d: Deca) -> None:
    """Addition of Deca with identical half_life works."""

    assert d + d
    with pytest.raises(TypeError):
        d + 1  # type: ignore  # mypy is drunk
        assert False, 'Adding a number to a Deca should fail'
    d2 = Deca(d.value, d.half_life * 2, d.timestamp)
    with pytest.raises(ValueError):
        d + d2
        assert (
            False
        ), 'Adding two Deca instances with mismatching half_life values should fail'

    # adding 0 does work!
    assert d + 0  # type: ignore  # mypy is drunk
    assert 0 + d  # type: ignore  # mypy is drunk

    # adding 0 does make a new instance!
    d2 = d + 0
    assert d is not d2

    # allowing sum() to work
    list_of_d = [d, d, d]
    sum_of_d: Deca = sum(list_of_d)  # type: ignore  # mypy is drunk
    assert isinstance(sum_of_d, Deca)


def test_multiply(d: Deca) -> None:
    """Multiplying works."""
    d2 = d * 2  # type: ignore  # mypy is drunk
    assert d2.at(d.timestamp) == d.value * 2

    d2 = 2 * d  # type: ignore  # mypy is drunk
    assert d2.at(d.timestamp) == d.value * 2

    with pytest.raises(TypeError):
        d * d2
        assert False, 'Multiplying two Deca instances should fail'


def test_division(d: Deca) -> None:
    """Division works."""
    d2 = d / 2  # type: ignore  # mypy is drunk
    assert d2.at(d.timestamp) == d.value / 2

    with pytest.raises(TypeError):
        d2 = 2 / d  # type: ignore  # mypy is drunk
        assert False, 'Division with Deca as divider should fail'

    with pytest.raises(TypeError):
        d / d2
        assert False, 'Dividing two Deca instances should fail'


def test_increment_no_ts(d: Deca) -> None:
    """Increment without timestamps work"""

    d_before = d.at()
    d.inc(1)
    d_after = d.at()

    # (assuming time.time() is monotonically increasing)
    # d_after should larger than d_before,
    # and a tiny bit less than d_before + the increment
    assert d_before < d_after <= d_before + 1


def test_increment_with_ts(d: Deca) -> None:
    """Increment with timestamps work"""

    now = d.timestamp
    increment = d.value
    d_before = d.at(now)
    d.inc(increment, now)  # this doubles the value
    assert d_before + increment == d.at(now)

    # increment one half_life somewhat later
    now_plus_hl = now + d.half_life
    d.inc(increment, now_plus_hl)
    # the timestamp has moved on
    assert d.timestamp == now_plus_hl
    assert d.at(now_plus_hl) == d_before + increment
