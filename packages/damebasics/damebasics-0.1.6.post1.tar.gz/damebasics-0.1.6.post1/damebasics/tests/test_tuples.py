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
# fix for MacOS using nose
import collections
collections.Callable = collections.abc.Callable

from pprint import pprint


class TddInPythonExample(unittest.TestCase):

    def test_tuple_set_method_returns_correct_result(self):
        a = (1, 1, 2, 2, 3, 3)
        tsa = tuple(set(a))
        self.assertEqual((1, 2, 3), tsa)
        self.assertTrue(isinstance(tsa, tuple))

    def test_tuple_join_method_returns_correct_result(self):
        a = ('2',)
        b = 'z'
        new = a + (b,)
        self.assertEqual(('2', 'z'), new)
        self.assertTrue(isinstance(new, tuple))


