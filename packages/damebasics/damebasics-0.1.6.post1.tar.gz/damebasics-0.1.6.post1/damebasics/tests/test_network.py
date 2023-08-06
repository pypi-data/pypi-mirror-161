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
import socket
from pprint import pprint
# fix for MacOS using nose
import collections
collections.Callable = collections.abc.Callable


class TddInPythonExample(unittest.TestCase):

    def test_network_socket_method_returns_correct_result(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("www.python.org", 80))
        self.assertTrue("<socket.socket" in str(s))

    def test_network_socket_get_method_returns_correct_result(self):
        self.assertTrue(socket.gethostbyname(socket.gethostname()), "127.0.0.1")
        self.assertTrue(socket.gethostbyaddr('127.0.0.1'), ('localhost', [], ['127.0.0.1']))
        proto = "tcp"
        self.assertEqual(socket.getservbyname("ftp",proto), 21)
        self.assertEqual(socket.getservbyname("http",proto), 80)
        self.assertEqual(socket.getservbyname("https",proto), 443)
        self.assertEqual(socket.getservbyport(21,proto), "ftp")
        self.assertEqual(socket.getservbyport(80,proto), "http")
        self.assertEqual(socket.getservbyport(443,proto), "https")

    def test_network_startswith_method_returns_correct_result(self):
        my_ip = socket.gethostbyname(socket.gethostname())
        self.assertTrue(my_ip.startswith('127.0.'))
