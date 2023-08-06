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
import re

from collections import Counter
from collections import defaultdict
from collections import deque
from collections import namedtuple
from collections import ChainMap
# fix for MacOS using nose
import collections
collections.Callable = collections.abc.Callable


class TddInPythonExample(unittest.TestCase):

    def test_counter_method_returns_correct_result(self):
        cnt = Counter()
        for word in ['red', 'blue', 'red', 'green', 'blue', 'blue']:
            cnt[word] += 1
        self.assertEqual(Counter({'blue': 3, 'red': 2, 'green': 1}), cnt)
        words = re.findall(r'\w+', open('files/pg1513.txt').read().lower())
        self.assertEqual(Counter(words).most_common(10), [('the', 757), ('and', 755), ('i', 659), ('to', 638), ('a', 505), ('of', 457), ('is', 368), ('that', 365), ('my', 359), ('you', 350)])

    def test_defaultdict_method_returns_correct_result(self):
        maxprob = defaultdict(lambda: 0.0)
        self.assertEqual(maxprob[0], 0.0)
        self.assertEqual(maxprob[1], 0.0)
        self.assertEqual(maxprob["asdf"], 0.0)
        minprob = defaultdict(lambda: 1.0)
        self.assertEqual(minprob[0], 1.0)
        self.assertEqual(minprob[99], 1.0)

    def test_deque_methods_returns_correct_result(self):
        d = deque('ghi')
        self.assertEqual(deque(['g', 'h', 'i']), d)
        self.assertEqual(d.popleft(), 'g')
        d.append('a')
        self.assertEqual(deque(['h', 'i', 'a']), d)

    def test_namedtuple_methods_returns_correct_result(self):
        Point = namedtuple('Point', ['x', 'y'])
        p = Point(11, y=22)
        res = p.x + p.y
        self.assertEqual(res, 33)

    def test_chainmap_methods_returns_correct_result(self):
        d1 = {'a': 1, 'b': 2}
        d2 = {'c': 3, 'd': 4}
        d3 = {'e': 5, 'f': 6}
        d4 = { 'g' : 5 }
        c = ChainMap(d1, d2, d3)
        self.assertEqual(c, ChainMap({'a': 1, 'b': 2}, {'c': 3, 'd': 4}, {'e': 5, 'f': 6}))
        c = c.new_child(d4)
        self.assertEqual(c, ChainMap({'a': 1, 'b': 2}, {'c': 3, 'd': 4}, {'e': 5, 'f': 6}, { 'g' : 5}))
