#!/usr/bin/env python3
import sys
from argparse import ArgumentParser, ArgumentTypeError
import random
import itertools


def int_in_range(min_, max_):
    def validator(user_string):
        value = int(user_string)
        if not min_ <= value <= max_:
            raise ArgumentTypeError(
                '%r is not a integer between %s-%s' % (
                    user_string, min_, max_))
        return value
    return validator


parser = ArgumentParser()
parser.add_argument('-w', '--width', type=int_in_range(0, 10), default=5,
                    help='The width of the board')
parser.add_argument('-d', '--depth', type=int_in_range(0, 10), default=5,
                    help='The depth of the board')
parser.add_argument('--inverse-input', action='store_true',
                    help='Give input in x, -y coords instead of row, column')
parser.add_argument('-n', '--number-of-bombs', type=int_in_range(0, 100),
                    default=5, help='The number of bombs on the board')


class Spot(object):

    def __init__(self):
        self.state = '?'
        self.is_bomb = False
        self.neighbor_bombs = 0

    def display(self):
        if self.is_bomb:
            self.state = '#'
        elif self.neighbor_bombs > 0:
            self.state = str(self.neighbor_bombs)
        else:
            self.state = ' '


class Game(object):

    def __init__(self, args):
        self.args = args
        self.is_running = True
        self.exploded = False
        self._make_board()

    def _in_bounds(self, x, y):
        if x < 0 or y < 0:
            return False
        try:
            self.board[x][y]
        except IndexError:
            return False
        return True

    def _neighbors(self, x, y):
        matrix = [(0, 1), (1, 0), (-1, 0), (0, -1)]
        for xd, yd in matrix:
            xt = x + xd
            yt = y + yd
            if self._in_bounds(xt, yt):
                yield xt, yt

    def _make_board(self):
        self.board = [
            [Spot() for i in range(self.args.width)]
            for j in range(self.args.depth)
        ]
        all_coords = list(itertools.product(range(self.args.depth),
                                            range(self.args.width)))
        bomb_coordinates = random.sample(all_coords, min(
            self.args.number_of_bombs, len(all_coords)))
        for x, y in bomb_coordinates:
            self.board[x][y].is_bomb = True
        for x, y in all_coords:
            self.board[x][y].neighbor_bombs = sum(
                self.board[nx][ny].is_bomb
                for nx, ny in self._neighbors(x, y))

    def display(self, final=False):
        if final:
            self.is_running = False
            for row in self.board:
                for spot in row:
                    spot.display()
        print('   =%s=' % '=='.join(str(i) for i in range(self.args.width)))
        for i, row in enumerate(self.board):
            print('=%s=[%s]' % (i, ']['.join(spot.state for spot in row)))
        if final:
            if self.exploded:
                print('Better luck next time!')
            else:
                print('Thanks for playing!')
        else:
            print('')

    def in_bounds(self, x, y):
        if x < 0 or y < 0:
            raise ValueError('Invalid choice, use positive indexes')
        if self.args.inverse_input:
            x, y = y, x
        return self._in_bounds(x, y)

    def update(self, x, y):
        if self.args.inverse_input:
            x, y = y, x
        if self.board[x][y].is_bomb:
            self.exploded = True
            self.is_running = False
        else:
            self.reveal(x, y, set((x, y)))
            if self._has_won():
                self.is_running = False

    def _has_won(self):
        for row in self.board:
            for spot in row:
                if spot.state == '?' and not spot.is_bomb:
                    return False
        return True

    def reveal(self, x, y, visited):
        if (x, y) in visited:
            return
        self.board[x][y].display()
        visited.add((x, y))
        if self.board[x][y].neighbor_bombs == 0:
            for nx, ny in self._neighbors(x, y):
                self.reveal(nx, ny, visited)


class UserQuitsError(Exception):
    pass


def get_choice(game):
    try:
        choice = input('Enter coordinates: ')
    except (KeyboardInterrupt, EOFError):
        raise UserQuitsError()
    if choice.lower() == 'q':
        raise UserQuitsError()
    try:
        x, y = [int(p.strip()) for p in choice.split(',')]
    except ValueError:
        raise ValueError('Invalid choice, use the form "X, Y"')
    if not game.in_bounds(x, y):
        raise ValueError('Invalid choice, out of bounds')
    return x, y


def main():
    args = parser.parse_args()
    print('Welcome! (q to quit)')
    game = Game(args)
    while game.is_running:
        game.display()
        try:
            choice = get_choice(game)
        except ValueError as e:
            print('ERROR: %s\n' % e)
            continue
        except UserQuitsError:
            print('')
            break
        game.update(*choice)
    game.display(final=True)


if __name__ == "__main__":
    sys.exit(main())
