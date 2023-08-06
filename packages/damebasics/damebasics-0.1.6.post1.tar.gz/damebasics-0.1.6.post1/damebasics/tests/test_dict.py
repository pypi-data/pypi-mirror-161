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

    def test_dict_method_returns_correct_result(self):
        dicc = {"precio1": 2300, "precio2": 3450, "precio3": 2760}
        self.assertEqual(dicc["precio3"], 2760)
        self.assertEqual(list(dicc.keys()), ["precio1", "precio2", "precio3"])
        self.assertEqual(list(dicc.values()), [2300, 3450, 2760])
        dicc2 = {"elem1": list(), "elem2": [1, 2, 3]}
        dicc2["elem1"].append(1)
        dicc2["elem1"].append(2)
        self.assertEqual(dicc2["elem1"], [1, 2])
        self.assertEqual(dicc2["elem2"], [1, 2, 3])
        self.assertTrue(isinstance(dicc, dict))
        self.assertTrue(isinstance(dicc2, dict))
