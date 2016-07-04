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

from subprocess import run, PIPE, DEVNULL
from game import sum_points


class InvalidMoveException(Exception):
    move = "UNKNOWN"
    description = "Unknown error"

    def __init__(self, move, description):
        self.description = description
        self.move = move

    def __str__(self):
        return "Invalid Move ({}): {}".format(self.move, self.description)


class Strategy:
    ant = None
    made_scent = False
    made_memory = False
    made_action = False
    position = (0, 0)

    def __init__(self, ant):
        self.ant = ant

    def gather_info(self, func):
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                yield func(*sum_points(self.ant.pos, (dx, dy)))

    def get_info_table(self, func):
        return (("{} " * 3 + "\n") * 3).format(*self.gather_info(func))

    def generate_input(self):
        res = "ID:\n{}\n".format(self.ant.id)
        res += "ALIVE_TIME:\n{}\n".format(self.ant.alive)
        res += "HAS_CARGO:\n{}\n".format(1 if self.ant.has_cargo else 0)
        res += "MEMORY:\n{}\n".format(" ".join(str(x) for x in self.ant.memory))
        res += "WALKABLE:\n{}".format(self.get_info_table(
            lambda x, y: 1 if self.ant.player.is_walkable_pos((x, y)) else 0
        ))
        res += "CARGO:\n{}".format(self.get_info_table(
            lambda x, y: self.ant.player.field.get_cargo_by_pos((x, y))
        ))
        res += "SCENT:\n{}".format(self.get_info_table(
            lambda x, y: self.ant.player.field.get_smell_by_pos((x, y))
        ))
        res += "FRIENDLY:\n{}".format(self.get_info_table(
            lambda x, y: len(list(
                filter(lambda ant: ant.player == self.ant.player, self.ant.player.field.ants_by_pos((x, y)))
            ))
        ))
        res += "ENEMIES:\n{}".format(self.get_info_table(
            lambda x, y: len(list(
                filter(lambda ant: ant.player != self.ant.player, self.ant.player.field.ants_by_pos((x, y)))
            ))
        ))
        return res

    def make_pass(self, command):
        if len(command) != 1:
            raise InvalidMoveException(command[0], "wrong arguments count")
        if self.made_action or self.made_scent or self.made_memory:
            raise InvalidMoveException(command[0], "must be the only instruction in the output")
        self.made_action = True
        self.made_scent = True
        self.made_memory = True

    def make_move(self, command):
        if len(command) != 3:
            raise InvalidMoveException(command[0], "wrong arguments count")
        if self.made_action:
            raise InvalidMoveException(command[0], "more than one action in the output")
        self.made_action = True
        try:
            x = int(command[1])
            y = int(command[2])
        except ValueError:
            raise InvalidMoveException(command[0], "invalid move destination")
        if abs(x) > 1 or abs(y) > 1:
            raise InvalidMoveException(command[0], "invalid move destination")
        self.ant.make_move(x, y)

    def make_drop(self, command):
        if len(command) != 1:
            raise InvalidMoveException(command[0], "wrong arguments count")
        if self.made_action:
            raise InvalidMoveException(command[0], "more than one action in the output")
        self.made_action = True
        self.ant.drop_cargo()

    def make_take(self, command):
        if len(command) != 1:
            raise InvalidMoveException(command[0], "wrong arguments count")
        if self.made_action:
            raise InvalidMoveException(command[0], "more than one action in the output")
        self.made_action = True
        self.ant.get_cargo()

    def make_scent(self, command):
        if len(command) != 2:
            raise InvalidMoveException(command[0], "wrong arguments count")
        if self.made_scent:
            raise InvalidMoveException(command[0], "more than one scent setting in the output")
        self.made_scent = True
        try:
            scent = int(command[1])
        except ValueError:
            raise InvalidMoveException(command[0], "invalid scent value")
        if not (-2**31 <= scent < 2 ** 31):
            raise InvalidMoveException(command[0], "invalid scent value")
        self.ant.player.field.smell[self.position[0]][self.position[1]] = scent

    def make_memory(self, command):
        if len(command) != 5:
            raise InvalidMoveException(command[0], "wrong arguments count")
        if self.made_memory:
            raise InvalidMoveException(command[0], "more than one memory setting in the output")
        self.made_memory = True
        new_memory = []
        try:
            for number in command[1:]:
                new_memory.append(int(number))
            if not (-2 ** 31 <= new_memory[-1] < 2 ** 31):
                raise InvalidMoveException(command[0], "invalid memory value")
        except ValueError:
            raise InvalidMoveException(command[0], "invalid memory value")
        self.ant.memory = tuple(new_memory)

    def turn(self):
        completed = run([self.ant.player.strategy_file], input=self.generate_input(), stdout=PIPE,
                         stderr=DEVNULL, universal_newlines=True, timeout=1, check=True, shell=True)
        commands = [command.strip().split() for command in completed.stdout.split('\n') if command.strip() != '']
        self.ant.alive += 1
        self.position = self.ant.pos
        operators = {
            "PASS": self.make_pass,
            "MOVE": self.make_move,
            "DROP": self.make_drop,
            "TAKE": self.make_take,
            "MEMORY": self.make_memory,
            "SCENT": self.make_scent,
        }
        for command in commands:
            if command[0] in operators:
                operators[command[0]](tuple(command))
            else:
                raise InvalidMoveException(command[0], "unknown command")



