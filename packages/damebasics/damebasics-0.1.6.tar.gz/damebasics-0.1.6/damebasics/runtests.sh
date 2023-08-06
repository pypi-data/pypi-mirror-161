#!/bin/sh

#  Copyright (C) 2022 David Arroyo Menéndez

#  Author: David Arroyo Menéndez <davidam@gmail.com> 
#  Maintainer: David Arroyo Menéndez <davidam@gmail.com> 
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
#  along with damebasics; see the file LICENSE.  If not, write to
#  the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, 
#  Boston, MA 02110-1301 USA,

# mkdir -p logs
# touch logs/nose.txt
# for i in $(ls tests/*); do
#     echo $i
#     nosetests $i 
# done

nosetests tests/test_arithmetics.py
nosetests tests/test_collections.py
nosetests tests/test_control_structures.py
nosetests tests/test_date.py
nosetests tests/test_dict.py
nosetests tests/test_files.py
nosetests tests/test_lists.py
nosetests tests/test_network.py
nosetests tests/test_network.py
nosetests tests/test_poo.py
nosetests tests/test_set.py
nosetests tests/test_strings.py
nosetests tests/test_tuples.py


