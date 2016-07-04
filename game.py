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


def sum_points(a, b):
    return tuple(map(sum, zip(a, b)))


class Field:
    size = (30, 30)
    cargo = None
    smell = None
    players = list()

    def __init__(self, x=30, y=30):
        self.size = (x, y)
        self.cargo = [[0] * y for _ in range(x)]
        self.smell = [[0] * y for _ in range(x)]

    def collect_all_ants(self):
        return sum([player.ants for player in self.players], list())

    def pos_is_inside(self, pos):
        for p, s in zip(pos, self.size):
            if not(0 <= p < s):
                return False
        return True

    def player_by_spawn(self, pos):
        for player in self.players:
            if player.spawn == pos:
                return player
        return None

    def get_cargo_by_pos(self, pos):
        if not self.pos_is_inside(pos):
            return 0
        return self.cargo[pos[0]][pos[1]]

    def get_smell_by_pos(self, pos):
        if not self.pos_is_inside(pos):
            return 0
        return self.smell[pos[0]][pos[1]]

    def ants_by_pos(self, pos):
        return list(filter(lambda ant: ant.pos == pos, self.collect_all_ants()))

    def is_game_over(self):
        if sum([c for line in self.cargo for c in line]) > 0:
            return False
        return sum(1 if ant.has_cargo else 0 for ant in self.collect_all_ants()) > 0


class Player:
    field = None
    name = "Unnamed Player"
    color = None
    strategy_file = "/bin/false"
    spawn = (0, 0)
    ants = list()
    score = 0

    def __init__(self, field, name, color, strategy_file, spawn):
        self.field = field
        self.name = name
        self.color = color
        self.strategy_file = strategy_file
        self.spawn = spawn
        field.players.append(self)

    def generate_ants(self, n=10):
        self.ants = list([Ant(self, i + 1) for i in range(n)])

    def is_walkable_pos(self, pos):
        return self.field.pos_is_inside(pos) and (self.field.player_by_spawn(pos) is None or
                                                  self.field.player_by_spawn(pos) == self)


class Ant:
    player = None
    pos = (0, 0)
    memory = (0, 0, 0, 0)
    id = 0
    has_cargo = False
    alive = 0

    def __init__(self, player, id):
        self.player = player
        self.pos = player.spawn
        self.id = id
        player.ants.append(self)

    def drop_cargo(self):
        if not self.has_cargo:
            return
        self.has_cargo = False
        if self.player.spawn == self.pos:
            self.player.score += 1
        else:
            self.player.field.cargo[self.pos[0]][self.pos[1]] += 1

    def get_cargo(self):
        if self.has_cargo:
            return
        if self.player.field.cargo[self.pos[0]][self.pos[1]] <= 0:
            return
        self.has_cargo = True
        self.player.field.cargo[self.pos[0]][self.pos[1]] -= 1

    def get_killed(self):
        self.drop_cargo()
        self.pos = self.player.spawn
        self.alive = 0

    def make_move(self, dx, dy):
        new_pos = sum_points(self.pos, (dx, dy))
        if not self.player.is_walkable_pos(new_pos):
            return
        self.pos = new_pos
        enemy_ants = list(filter(lambda ant: ant.player != self.player, self.player.field.ants_by_pos(new_pos)))
        if len(enemy_ants) > 1:
            self.get_killed()
            return
        for ant in enemy_ants:
            ant.get_killed()
