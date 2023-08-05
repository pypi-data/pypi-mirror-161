#!/usr/bin/python3
# -*- coding: utf-8 -*-
#  Copyright (C) 2022 David Arroyo Menendez

#  Author: David Arroyo Menendez <davidam@gmail.com>
#  Maintainer: David Arroyo Menendez <davidam@gmail.com>
#  This file is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3, or (at your option)
#  any later version.
# 
#  This file is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# 
#  You should have received a copy of the GNU General Public License
#  along with DameBasics; see the file GPL.txt.  If not, write to
#  the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, 
#  Boston, MA 02110-1301 USA,

import unittest
import collections
collections.Callable = collections.abc.Callable

from pprint import pprint

class TddInPythonExample(unittest.TestCase):

    def test_files_write_returns_correct_result(self):
        fo = open("files/tmp.txt", "w")
        fo.write("Gora python\n");
        fo.close()
        with open('files/tmp.txt', encoding='utf8') as f:
            text = f.read().strip()
        self.assertEqual(text, "Gora python")

    def test_files_write_lines_returns_correct_result(self):
        file = open("files/tmp2.txt", "w")
        file.write("This is a test\n")
        file.write("To add more lines.\n")
        lines_of_text = ["One line of text here\n", "and another line here\n", "and yet another here\n", "and so on and so forth\n"]
        file.writelines(lines_of_text)
        file.close()
        with open('files/tmp2.txt', encoding='utf8') as f:
            text = f.read().strip()
        self.assertEqual(text, "This is a test\nTo add more lines.\nOne line of text here\nand another line here\nand yet another here\nand so on and so forth")

    def test_files_readline_returns_correct_result(self):
        fo = open("files/tmp.txt", "r+")
        char = fo.readline(1)
        self.assertEqual(char, "G")
        fo.seek(1)
        line = fo.readline()
        self.assertEqual(line, "ora python\n")
