from interpreter import variable
import time
from interpreter import LOG_WAY

cells = {
    ' ': 'empty',
    'E': 'exit',
    '#': 'wall'
}

back_cells = {
    'empty': ' ',
    'exit': 'E',
    'wall': '#'
}




class Cell:
    def __init__(self, type):
        self.type = type

    def __repr__(self):
        return f'{self.type}'

class Robot:
    def __init__(self, x, y, map):
        self.x = x
        self.y = y
        self._right = True
        self.map = map

    def __repr__(self):
        if self.right:
            return f'x = {self.x}, y = {self.y}; side scan = right\n'
        else:
            return f'x = {self.x}, y = {self.y}; side scan = left\n'

    def show(self):
        for i in range(len(self.map)):
            for j in range(len(self.map[0])):
                if i == self.y and j == self.x:
                    print('R', end='')
                else:
                    if back_cells[self.map[i][j].type] == ' ':
                        if (i+j) % 2 == 0:
                            print('▲', end='')
                        else:
                            print('▼', end='')
                    else:
                        print(back_cells[self.map[i][j].type], end='')
            print()
        print()

    def move(self, direction):
        if LOG_WAY:
            print(direction)
        if direction == 'move':
            if (self.x+self.y) % 2 == 0:
                return self.down()
            else:
                return self.up()
        elif direction == 'left':
            return self.left()
        elif direction == 'right':
            return self.right()
        else:
            return variable('int', '', 0)

    def up(self):
        if self.y <= 0:
            return variable('int', '', 0)
        if (self.x + self.y) % 2 == 0:
            return variable('int', '', 0)
        else:
            if self.map[self.y - 1][self.x].type != 'wall':
                self.y -= 1
                return variable('int', '', 1)
        return variable('int', '', 0)

    def down(self):
        if self.y >= len(self.map):
            return variable('int', '', 0)
        if (self.x + self.y) % 2 == 0:
            if self.map[self.y + 1][self.x].type != 'wall':
                self.y += 1
                return variable('int', '', -1)
        return variable('int', '', 0)

    def left(self):
        if self.x <= 0:
            return variable('int', '', 0)
        else:
            if self.map[self.y][self.x - 1].type != 'wall':
                self.x -= 1
                return variable('int', '', -1)
        return variable('int', '', 0)

    def right(self):
        if self.x >= len(self.map[0]):
            return variable('int', '', 0)
        else:
            if self.map[self.y][self.x + 1].type != 'wall':
                self.x += 1
                return variable('int', '', 1)
        return variable('int', '', 0)

    def exit(self):
        if self.map[self.y][self.x].type == 'exit':
            return True
        return False

    def lms(self):
        iter_i = 1
        length = 5
        if self._right:
            while self.map[self.y][self.x+iter_i].type == 'empty':
                if length == 0:
                    return variable('int', '', 0)
                iter_i += 1
                length -= 1
            if self.map[self.y][self.x+iter_i].type == 'exit':
                return variable('int', '', -iter_i)
            elif self.map[self.y][self.x+iter_i].type == 'wall':
                return variable('int', '', iter_i)
        else:
            self._right = True
            while self.map[self.y][self.x-iter_i].type == 'empty':
                if length == 0:
                    return variable('int', '', 0)
                iter_i += 1
                length -= 1
            if self.map[self.y][self.x-iter_i].type == 'exit':
                return variable('int', '', iter_i)
            elif self.map[self.y][self.x-iter_i].type == 'wall':
                return variable('int', '', -iter_i)

