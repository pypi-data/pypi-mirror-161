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
from pprint import pprint
# fix for MacOS using nose
import collections
collections.Callable = collections.abc.Callable


class TddInPythonExample(unittest.TestCase):

    def test_set__method_returns_correct_result(self):
        conjunto = "Italia", "Grecia", "Italia", "China", "Grecia", "Brasil"
        paises = set(conjunto)
        paises.remove("China")
        paises.add("Turquia")
        paises.add("Alemania")
        self.assertEqual(paises, set({"Italia", "Grecia",
                                      "Italia", "Grecia",
                                      "Brasil", "Turquia",
                                      "Alemania"}))
        self.assertTrue(isinstance(paises, set))
        d = paises.difference(set({"Italia", "Grecia", "Turquia"}))
        self.assertEqual(d, set({"Brasil", "Alemania"}))

