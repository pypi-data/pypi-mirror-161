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

    def test_list_append_method_returns_correct_result(self):
        mylist = []
        mylist.append(1)
        mylist.append(2)
        mylist.append(3)

        self.assertEqual(1, mylist[0])
        self.assertEqual(2, mylist[1])
        self.assertEqual(3, mylist[2])
        self.assertTrue(isinstance(mylist, list))

    def test_list_methods_returns_correct_result(self):
        li = ["a", "b", "mpilgrim", "z", "example"]
        self.assertEqual(li[0], "a")
        self.assertEqual(li[0], "a")
        li.extend(["two", "elements"])
        self.assertEqual(li[-1], "elements")
        li.insert(2, "new")
        self.assertEqual(li[2], "new")
        self.assertEqual(5, li.index("example"))
        li.remove("example")
        self.assertEqual(["a", "b", "new", "mpilgrim",
                          "z", "two", "elements"],
                         li)
        self.assertTrue(isinstance(li, list))


    def test_list_union_method_returns_correct_result(self):
        lista = ['a', 'b', 'mpilgrim']
        lista = lista + ['example', 'new']
        lista += ['two']
        self.assertEqual(lista, ['a', 'b', 'mpilgrim',
                                 'example', 'new', 'two'])
        self.assertTrue(isinstance(lista, list))

    def test_list_sort_method_returns_correct_result(self):
        milista = ['This', 'used', 'to', 'be', 'a',
                   'Whopping', 'Great', 'sentence']
        milista2 = sorted(milista, key=str.lower)
        self.assertEqual(milista2, ['a', 'be', 'Great',
                                    'sentence', 'This',
                                    'to', 'used', 'Whopping'])
        self.assertTrue(isinstance(milista2, list))

    def test_list_lambda_method_returns_correct_result(self):
        l1 = list(map(lambda x: x**2, range(10)))
        l2 = [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
        self.assertEqual(l1, l2)
        self.assertTrue(isinstance(l1, list))
        self.assertTrue(isinstance(l2, list))
