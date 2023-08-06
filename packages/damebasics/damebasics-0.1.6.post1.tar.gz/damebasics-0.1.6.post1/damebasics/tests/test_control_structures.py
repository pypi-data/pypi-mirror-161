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

    def test_conditional_method_returns_correct_result(self):
        x = 2
        if x < 0:
            x = 0
            x = 'Negative changed to zero'
        elif x == 0:
            x = 'Zero'
        elif x == 1:
            x = 'Single'
        else:
            x = 'More than one'

        self.assertEqual(x, 'More than one')

    def test_for_method_returns_correct_result(self):
        words = ['cat', 'window', 'defenestrate']
        string = ""
        for w in words:
            string = string + w + "," + str(len(w)) + ";"

        self.assertEqual("cat,3;window,6;defenestrate,12;", string)

    def test_zip_method_returns_correct_result(self):
        v = [1, 2, 3]
        w = [1, 2, 3]
        z = []
        for v_i, w_i in zip(v, w):
            z = z + [v_i + w_i]
        self.assertEqual(z, [2, 4, 6])

    def test_enumerate_method_returns_correct_result(self):
        words = ['cat', 'window', 'defenestrate']
        string = ""
        for i, w in enumerate(words):
            string = string + str(i) + w

        self.assertEqual("0cat1window2defenestrate", string)

    def test_range_method_returns_correct_result(self):
        words = ['cat', 'window', 'defenestrate']
        string = ""
        for i in range(1, 10):
            string = string + str(i)

        self.assertEqual("123456789", string)

    def test_format_method_returns_correct_result(self):
        string1 = ','.join('{}'.format(i) for i in range(1, 10, 4))
        self.assertEqual("1,5,9", string1)
        string2 = ','.join('{},{}'.format(i, i + 1) for i in range(1, 30, 4))
        self.assertEqual("1,2,5,6,9,10,13,14,17,18,21,22,25,26,29,30", string2)

    def test_while_method_returns_correct_result(self):
        vector = [1, 2, 3, 4, 5]
        i = 0
        string = ""
        while (i < len(vector)):
            string = string + str(vector[i])
            i = i + 1
        self.assertEqual(string, "12345")
