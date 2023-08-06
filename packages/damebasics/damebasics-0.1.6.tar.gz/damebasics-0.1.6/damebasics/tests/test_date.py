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
# along with DameBasics; see the file LICENSE.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA,

import unittest
import datetime
from datetime import timedelta
from pprint import pprint
# fix for MacOS using nose
import collections
collections.Callable = collections.abc.Callable


class TddInPythonExample(unittest.TestCase):

    def test_datetime_date_method_returns_correct_result(self):
        mydate = datetime.date(1943, 3, 13)  # year, month, day
        self.assertEqual(mydate.strftime("%A"), "Saturday")
        self.assertEqual(mydate.strftime("%B"), "March")
        self.assertTrue(isinstance(mydate, datetime.date))

    def test_datetime_timedelta_method_returns_correct_result(self):
        seconds = 153.1205153
        d = timedelta(seconds)
#        self.assertEqual("153 days, 2:53:32.521920", d)
        self.assertEqual(d.days, 153)
        self.assertEqual(d.seconds, 10412)

    def test_datetime_comparing_methods_returns_correct_result(self):
        t1 = datetime.time(12, 55, 0)
        t2 = datetime.time(13, 5, 0)
        self.assertTrue(t1 < t2)
