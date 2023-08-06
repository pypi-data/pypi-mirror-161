"""
This module provides functions for getting the English names of numbers.

Use integer_name, float_name or complex_name to get the name of number.
"""
from __future__ import annotations

import math
from contextlib import suppress
from decimal import Decimal
from fractions import Fraction
from functools import wraps
from typing import Callable, Iterable, Iterator

__all__ = [
    "complex_name",
    "decimal_name",
    "float_name",
    "fraction_name",
    "integer_name",
    "name",
]
__version__ = "0.1.0"

_MINUS = "minus"
_UNITS = (
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
    "twenty",
)
_TENS = (
    _UNITS[0],
    _UNITS[10],
    _UNITS[20],
    "thirty",
    "forty",
    "fifty",
    "sixty",
    "seventy",
    "eighty",
    "ninety",
)
_HUNDRED = "hundred"
_SMALL_POWERS = (
    "",
    "thousand",
    "mi",
    "bi",
    "tri",
    "quadri",
    "quinti",
    "sexti",
    "septi",
    "octi",
    "noni",
)
_POWER_UNITS = (
    "",
    "un",
    "duo",
    "tre",
    "quattuor",
    "quin",
    "sex",
    "septen",
    "octo",
    "novem",
)
_POWER_TENS = (
    "",
    "dec",
    "vigin",
    "trigin",
    "quadragin",
    "quinquagin",
    "sexagin",
    "septuagin",
    "octogin",
    "nonagin",
)
_POWER_HUNDREDS = (
    "",
    "cen",
    "duocen",
    "trecen",
    "quadringen",
    "quingen",
    "sescen",
    "septingen",
    "octingen",
    "nongen",
    "millia",
)
_SMALL_SUFFIX = "llion"
_OTHER_SUFFIX = "tillion"


def _words(function: Callable[..., Iterable[str]]) -> Callable[..., str]:
    @wraps(function)
    def inner(*args, **kwargs) -> str:
        return " ".join(function(*args, **kwargs))

    return inner


def _power_name(power_index: int) -> str:
    with suppress(IndexError):
        name = _SMALL_POWERS[power_index]
        if power_index > 1:
            name += _SMALL_SUFFIX
        return name
    power_index -= 1
    parts = []
    millias = 0
    while power_index:
        power_index, part = divmod(power_index, 1000)
        if not part:
            millias += 1
            continue
        hundreds, units = divmod(part, 100)
        tens, units = divmod(units, 10)
        parts.append(
            "".join(
                (
                    _POWER_HUNDREDS[hundreds],
                    _POWER_UNITS[units],
                    _POWER_TENS[tens],
                    "millia" * millias,
                )
            )
        )
        millias += 1
    return "".join(parts[::-1] + [_OTHER_SUFFIX]).replace("dectillion", "decillion")


@_words
def _to_thousand_name(number: int) -> Iterator[str]:
    with suppress(IndexError):
        yield _UNITS[number]
        return
    hundreds, units = divmod(number, 100)
    if hundreds:
        yield from (_UNITS[hundreds], _HUNDRED)
        if not units:
            return
        yield "and"
    with suppress(IndexError):
        yield _UNITS[units]
        return
    tens, units = divmod(units, 10)
    if tens:
        yield _TENS[tens]
    if units:
        yield _UNITS[units]


def _denominator_name(name: str) -> str:
    if name == "two":
        return "half"
    if name == "four":
        return "quarter"
    for old_suffix, new_suffix in (
        ("one", "first"),
        ("two", "second"),
        ("three", "third"),
        ("five", "fifth"),
        ("eight", "eighth"),
        ("nine", "ninth"),
        ("twelve", "twelfth"),
        ("y", "ieth"),
    ):
        if name.endswith(old_suffix):
            return name.removesuffix(old_suffix) + new_suffix
    return name + "th"


@_words
def integer_name(number: int) -> Iterator[str]:
    if number == 0:
        yield _UNITS[0]
        return
    if number < 0:
        yield _MINUS
        number = -number
    string = str(number)
    parts = []
    while string:
        parts.append(int(string[-3:]))
        string = string[:-3]

    for power, part in reversed(tuple(enumerate(parts))):
        if part:
            yield _to_thousand_name(part)
            if power:
                yield _power_name(power)


@_words
def decimal_name(number: Decimal) -> Iterator[str]:
    yield integer_name(int(number))
    _, _, decimals = format(number, "f").partition(".")
    if decimals in {"", "0"}:
        return
    yield "point"
    for digit in decimals:
        yield _UNITS[int(digit)]


@_words
def float_name(number: float) -> Iterator[str]:
    if not math.isfinite(number):
        raise ValueError("non-finite number has no name")
    yield decimal_name(Decimal(str(number)))


def complex_name(number: complex) -> str:
    real_name = float_name(number.real)
    imag_name = float_name(number.imag)
    if number.imag == 0:
        return real_name
    if number.real == 0:
        return f"{imag_name} i"
    if number.real > 0:
        return f"{real_name} plus {imag_name} i"
    return f"{real_name} {imag_name} i"


def fraction_name(number: Fraction) -> str:
    numerator = integer_name(number.numerator)
    denominator = _denominator_name(integer_name(number.denominator))
    if number.denominator == 1 or not number.numerator:
        return numerator
    if abs(number.numerator) > 1:
        if denominator == "half":
            denominator = "halves"
        else:
            denominator += "s"
    return f"{numerator} {denominator}"


def name(number: complex | Fraction | Decimal) -> str:
    if isinstance(number, Fraction):
        return fraction_name(number)
    if isinstance(number, Decimal):
        return decimal_name(number)
    return complex_name(number)
