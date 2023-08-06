#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2021  David Arroyo Menéndez

# Author: David Arroyo Menéndez <davidam@gmail.com>
# Maintainer: David Arroyo Menéndez <davidam@gmail.com>

# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.

# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with damebasics; see the file LICENSE.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA,

import unittest
import collections
collections.Callable = collections.abc.Callable

from pprint import pprint


class TddInPythonExample(unittest.TestCase):

    def test_arithmetics_calculator_returns_correct_result(self):
        mysum = 2 + 2
        sumres = 4
        self.assertEqual(mysum, sumres)
        myminus = 3 - 2
        minusres = 1
        self.assertEqual(myminus, minusres)
        mymul = 3 * 2
        mulres = 6
        self.assertEqual(mymul, mulres)
        mydiv = 4 / 2
        divres = 2
        self.assertEqual(mydiv, divres)
        mypow = pow(2, 3)
        powres = 8
        self.assertEqual(mypow, powres)
        mymod = 5 % 2
        modres = 1
        self.assertEqual(mymod, modres)

    def test_arithmetics_round_returns_correct_result(self):
        myround1 = round(3.6)
        round1res = 4
        self.assertEqual(round1res, myround1)
        myround2 = round(3.1459, 2)
        round2res = 3.15
        self.assertEqual(round2res, myround2)
