import math
import random
from fractions import Fraction

import pytest

import number_names


def random_integer() -> int:
    return random.randrange(-(2 ** 128), 2 ** 128)


def random_float() -> float:
    return random.uniform(-(2 ** 128), 2 ** 128)


def random_complex() -> complex:
    return complex(random_float(), random_float())


def test_units() -> None:
    assert tuple(number_names.integer_name(i) for i in range(21)) == number_names._UNITS


def test_tens() -> None:
    assert (
        tuple(number_names.integer_name(i) for i in range(0, 100, 10))
        == number_names._TENS
    )


def test_signs() -> None:
    for function in (random_integer, random_float):
        for _ in range(50):
            number = function()
            assert (number < 0) == ("minus" in number_names.name(number))


def test_bad_numbers():
    for bad_number in (math.nan, math.inf, -math.inf):
        with pytest.raises(ValueError):
            number_names.name(bad_number)


def test_small_fractions() -> None:
    assert [
        [number_names.fraction_name(Fraction(n, d)) for n in range(1, 6)]
        for d in range(1, 6)
    ] == [
        ["one", "two", "three", "four", "five"],
        ["one half", "one", "three halves", "two", "five halves"],
        ["one third", "two thirds", "one", "four thirds", "five thirds"],
        ["one quarter", "one half", "three quarters", "one", "five quarters"],
        ["one fifth", "two fifths", "three fifths", "four fifths", "one"],
    ]
