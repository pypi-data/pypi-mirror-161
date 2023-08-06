# Number Names

`number_names` converts numbers to their English names.

The main useful function this package provides is called `name`. Usage
is as follows:

```python
>>> import number_names
>>> number_names.name(0)
'zero'
>>> number_names.name(1)
'one'
>>> number_names.name(2)
'two'
>>> number_names.name(123_456_789)
'one hundred and twenty three million four hundred and fifty six thousand seven hundred and eighty nine'
>>> number_names.name(3.1415)
'three point one four one five'
>>> number_names.name(-10 ** 15)
'minus one quadrillion'
>>> number_names.name(10 ** 100000)
'ten tretriginmilliatrecenduotrigintillion'
>>> number_names.name(3 + 2j)
'three plus two i'
>>> from fractions import Fraction
>>> number_names.name(Fraction(1, 2))
'one half'
>>> number_names.name(Fraction(3, 221))
'three two hundred and twenty firsts'
```
