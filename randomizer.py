#!/usr/bin/python3

# This file is part of AntArena.
# Copyright (C) 2016, Ivan Koryabkin
#
# AntArena is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# AntArena is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with AntArena.  If not, see <http://www.gnu.org/licenses/>.

from random import randint
from PyQt5.QtGui import QColor
from game import Player


class RandomizeArenaQuoters:
    def randomize(self, field):
        x, y = field.size
        for i in range(x):
            for j in range(y):
                if i == 0 and j == 0:
                    continue
                if randint(1, 3) == 1:
                    field.cargo[i][j] = randint(1, 20)
                original_i, original_j = min(i, x-i-1), min(j, y-j-1)
                field.cargo[i][j] = field.cargo[original_i][original_j]


