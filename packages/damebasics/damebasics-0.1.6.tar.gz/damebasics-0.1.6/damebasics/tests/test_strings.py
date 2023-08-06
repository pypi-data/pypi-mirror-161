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
import re
import subprocess
import io
import sys
# fix for MacOS using nose
import collections
collections.Callable = collections.abc.Callable


from pprint import pprint


class _AssertStdoutContext:

    def __init__(self, testcase, expected):
        self.testcase = testcase
        self.expected = expected
        self.captured = io.StringIO()

    def __enter__(self):
        sys.stdout = self.captured
        return self

    def __exit__(self, exc_type, exc_value, tb):
        sys.stdout = sys.__stdout__
        captured = self.captured.getvalue()
        self.testcase.assertEqual(captured, self.expected)


class TddInPythonExample(unittest.TestCase):

    def assertStdout(self, expected_output):
        return _AssertStdoutContext(self, expected_output)

    # as a bonus, this syntactical sugar becomes possible:
    def assertPrints(self, *expected_output):
        expected_output = "\n".join(expected_output) + "\n"
        return _AssertStdoutContext(self, expected_output)

    def test_print1(self):
       with self.assertStdout("test\n"):
          print("test")

    def test_string_check_type_method_returns_correct_result(self):
        doublestr = "str1str2"
        # a string
        self.assertTrue(isinstance(doublestr, str))
        # letters and/or numbers without white spaces
        self.assertTrue(doublestr.isalnum())
        # letters without numbers and without white spaces
        self.assertTrue(not(doublestr.isalpha()))
        # numbers without white spaces
        self.assertTrue(not(doublestr.isdigit()))
        # lower case
        self.assertTrue(doublestr.lower())
        # lower case
        self.assertEqual("Str1str2", doublestr.capitalize())

    def test_string_concat_method_returns_correct_result(self):
        string1 = "str1"
        string2 = "str2"
        self.assertEqual("str1str2", string1 + string2)

    def test_string_sub_method_returns_correct_result(self):
        str = 'purple alice@google.com, blah monkey bob@abc.com blah dishwasher'
        strsub = re.sub(r'([\w\.-]+)@([\w\.-]+)', r'\1@yo-yo-dyne.com', str)
        self.assertEqual('purple alice@yo-yo-dyne.com, blah monkey bob@yo-yo-dyne.com blah dishwasher', strsub)

    def test_string_match_method_returns_correct_result(self):
        m = re.match(r"(\w+) (\w+) (\w+)", "Isaac Newton physicist")
        self.assertEqual(m.group(0), "Isaac Newton physicist")
        self.assertEqual(m.group(1), "Isaac")
        self.assertEqual(m.group(2), "Newton")
        self.assertEqual(m.group(3), "physicist")
        n = re.match(r"(\[asf\]) (\w+) (\w+)", "[asf] tests Hola")
        self.assertEqual(n.group(0), "[asf] tests Hola")
        self.assertEqual(n.group(1), "[asf]")
        self.assertEqual(n.group(2), "tests")
        self.assertEqual(n.group(3), "Hola")

    def test_string_search_method_returns_correct_result(self):
        m = re.search(r'^(1[0-2]|[1-9])$', str(9))
        self.assertTrue(m)
        m2 = re.search(r'^(1[0-2]|[1-9])$', str(12))
        self.assertTrue(m2)
        m3 = re.search(r'^(1[0-2]|[1-9])$', str(19))
        self.assertFalse(m3)


    def test_string_group_method_returns_correct_result(self):
        p = '(?:http.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*'
        m = re.search(p,'http://www.abc.com:123/test')
        self.assertEqual(m.group('host'), 'www.abc.com') # 'www.abc.com'
        self.assertEqual(m.group('port'), str(123)) # '123'

    def test_string_split_method_returns_correct_result(self):
        self.assertEqual(re.split(r'\W+', 'Words, words, words.'), ['Words', 'words', 'words', ''])
        self.assertEqual(re.split(r'(\W+)', 'Words, words, words.'), ['Words', ', ', 'words', ', ', 'words', '.', ''])
        self.assertEqual(re.split(r'\W+', 'Words, words, words.', 1), ['Words', 'words, words.'])

    def test_string_findall_method_returns_correct_result(self):
        sentence = 'peter piper pick a peck of pickled peppers'
        ps = 'p\w+'
        l = re.findall(ps, sentence)
        self.assertEqual(l, ['peter', 'piper', 'pick', 'peck', 'pickled', 'peppers'])
        xx = "guru99,education is fun"
        r1 = re.findall(r"^\w+",xx)
        self.assertEqual(r1, ['guru99'])
        abc = 'guru99@google.com, careerguru99@hotmail.com, users@yahoomail.com, helloworld'
        emails = re.findall(r'[\w\.-]+@[\w\.-]+', abc)
        self.assertEqual(emails, ['guru99@google.com', 'careerguru99@hotmail.com', 'users@yahoomail.com'])

    def test_string_start_end_methods_returns_correct_result(self):
        email = "tony@tiremove_thisger.net"
        m = re.search("remove_this", email)
        self.assertEqual(email[:m.start()], "tony@ti")
        self.assertEqual(email[m.end():], "ger.net")
