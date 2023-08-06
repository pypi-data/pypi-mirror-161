#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2021  David Arroyo Menéndez

# Author: David Arroyo Menéndez <davidam@gnu.org>
# Maintainer: David Arroyo Menéndez <davidam@gnu.org>

# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.

# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with DameBasics; see the file LICENSE.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA,

import unittest
# fix for MacOS using nose
import collections
collections.Callable = collections.abc.Callable

from src.calculator import Calculator
from src.factorial import Factorial
from src.primes import Primes
from src.fib import Fib


class TddInPythonExample(unittest.TestCase):

    # CALCULATOR #

    def test_calculator_add_method(self):
        calc = Calculator()
        result = calc.add(2, 2)
        self.assertEqual(4, result)

    def test_calculator_sub_method(self):
        calc = Calculator()
        result = calc.sub(2, 2)
        self.assertEqual(0, result)

    def test_calculator_prod_method(self):
        calc = Calculator()
        result = calc.prod(2, 2)
        self.assertEqual(4, result)

    def test_calculator_div_method(self):
        calc = Calculator()
        result = calc.div(2, 2)
        self.assertEqual(1, result)

    def test_calculator_prodUsingAdd_method(self):
        calc = Calculator()
        result = calc.prodUsingAdd(5, 4)
        self.assertEqual(20, result)

    # FACTORIAL #

    def test_factorial_fac2_method(self):
        f = Factorial()
        result = f.fac(2)
        self.assertEqual(2, result)

    def test_factorial_fac3_method(self):
        f = Factorial()
        result = f.fac(3)
        self.assertEqual(6, result)

    def test_factorial_fac4_method(self):
        f = Factorial()
        result = f.fac(4)
        self.assertEqual(24, result)

    # FIBONACCI #

    def test_fib_fib2_method(self):
        f = Fib()
        result = f.fib(2)
        self.assertEqual([1, 1], result)

    def test_fib_fib3_method(self):
        f = Fib()
        result = f.fib(3)
        self.assertEqual([1, 1, 2, 3, 5], result)

    def test_fib_fib4_method(self):
        f = Fib()
        result = f.fib(4)
        self.assertEqual([1, 1, 2, 3, 5, 8], result)

    # PRIMES #

    def test_primes_divisible_method(self):
        p = Primes()
        result = p.divisible(4, 2)
        self.assertEqual(result, True)

    def test_primes_generateList_method(self):
        p = Primes()
        result = p.generateList(2, 11)
        self.assertEqual([2, 3, 4, 5, 6, 7, 8, 9, 10, 11], result)

    def test_primes_dividers_method(self):
        p = Primes()
        result = p.dividers(4)
        self.assertEqual([1, 2, 4], result)

    def test_primes_primes_method(self):
        p = Primes()
        result = p.primes(4)
        self.assertEqual([1, 2, 3], result)


if __name__ == '__main__':
    unittest.main()
