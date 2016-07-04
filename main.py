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


import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QPainter, QColor
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QMainWindow
from game import Field, Player
from randomizer import RandomizeArenaQuoters
from strategy import Strategy


class RenderingArea(QWidget):
    SIZE_BY_CELL = 20

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setFixedSize(900, 600)

    def paintEvent(self, QPaintEvent):
        painter = QPainter(self)
        for x in range(self.parent.field.size[0]):
            for y in range(self.parent.field.size[1]):
                painter.setPen(QColor("#000000"))
                if self.parent.field.player_by_spawn((x, y)) is None:
                    painter.setBrush(QColor(0, 255 - self.parent.field.cargo[x][y] * 8, 0))
                    painter.drawRect(y * self.SIZE_BY_CELL, x * self.SIZE_BY_CELL, self.SIZE_BY_CELL, self.SIZE_BY_CELL)
                else:
                    painter.setBrush(QColor("#964B00"))
                    painter.drawRect(y * self.SIZE_BY_CELL, x * self.SIZE_BY_CELL, self.SIZE_BY_CELL, self.SIZE_BY_CELL)
                ants = list(self.parent.field.ants_by_pos((x, y)))
                if len(ants):
                    painter.setPen(ants[0].player.color)
                    painter.setBrush(ants[0].player.color)
                    painter.drawEllipse(y * self.SIZE_BY_CELL+1, x * self.SIZE_BY_CELL+1,
                                        self.SIZE_BY_CELL-2, self.SIZE_BY_CELL-2)
                    painter.setPen(QColor("#FFFFFF"))
                    painter.drawText(y * self.SIZE_BY_CELL, x * self.SIZE_BY_CELL, self.SIZE_BY_CELL, self.SIZE_BY_CELL,
                                     Qt.AlignHCenter | Qt.AlignVCenter, str(len(ants)))
        for no, player in enumerate(self.parent.field.players):
            painter.setPen(QColor("#000000"))
            painter.setBrush(player.color)
            painter.drawRect(650, 100 + no * 50, 50, 25)
            painter.drawText(720, 100 + no * 50, 180, 25, Qt.AlignVCenter, player.name)
            painter.setPen(QColor("#FFFFFF"))
            painter.drawText(650, 100 + no * 50, 50, 25, Qt.AlignVCenter | Qt.AlignHCenter, str(player.score))


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.field = Field()
        self.area = RenderingArea(self)
        self.timer = QTimer()
        self.load_players()
        self.init_ui()
        RandomizeArenaQuoters().randomize(self.field)

    def load_players(self):
        x, y = self.field.size
        for line, pos in zip(open("players.txt").readlines(), [(0, 0), (x-1, y-1), (0, y-1), (x-1, 0)]):
            name, color, file = line.strip().split(';')
            Player(self.field, name, QColor(color), file, pos).generate_ants()

    def init_ui(self):
        self.setFixedSize(900, 600)
        self.setWindowTitle("Ant Arena")
        self.setWindowIcon(QIcon("ant.gif"))
        layout = QHBoxLayout()
        layout.addWidget(self.area)
        self.setLayout(layout)
        self.show()
        self.set_timer()

    def set_timer(self):
        self.timer.singleShot(100, self.turn)

    def turn(self):
        for ant in self.field.collect_all_ants():
            try:
                Strategy(ant).turn()
            except Exception as e:
                print(repr(e), file=sys.stderr)
        self.area.repaint()
        #for row in self.field.smell:
        #    print("".join([str(x) for x in row]))
        self.set_timer()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())
