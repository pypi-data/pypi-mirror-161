#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2018  David Arroyo Menéndez

# Author: David Arroyo Menéndez <davidam@gnu.org>
# Maintainer: David Arroyo Menéndez <davidam@gnu.org>

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

# import pdb

class Primes(object):

    def divisible(self, x, y):
        return (0 == (x % y))

    def generateList(self, x, y):
        if (x == y):
            return [y]
        else:
            return [x] + self.generateList(x+1, y)

    def dividers(self, x):
        l1 = self.generateList(1, x)
        laux = []
        for i in l1:
            if (0 == (x % i)):
                laux = laux + [i]
        return laux

    def primes(self, x):
        l1 = self.generateList(1, x)
        laux = []
        for i in l1:
            d = self.dividers(i)
            if ((len(d) == 2) or (i == 1)):
                laux = laux + [i]
        return laux
