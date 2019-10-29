import random
import typing
import dataclasses
import csv
import enum
import json
import unionfind
import itertools


HARMONY_POINTS = 5
MIDDLE_KINGDOM_POINTS = 10


class MaxTurns(enum.Int):
    DYNASTY         = 3
    STANDARD        = 6
    MIGHTY_DUEL     = 12


class DrawNum(enum.Int):
    THREE   = 3
    FOUR    = 4


class Rule(enum.Flag):
    TWO_PLAYERS     = enum.auto()
    THREE_PLAYERS   = enum.auto()
    FOUR_PLAYERS    = enum.auto()
    DYNASTY         = enum.auto()
    MIDDLE_KINGDOM  = enum.auto()
    HARMONY         = enum.auto()
    MIGHTY_DUEL     = enum.auto()


class Suit(enum.Enum):
    WHEAT   = enum.auto()
    FOREST  = enum.auto()
    WATER   = enum.auto()
    GRASS   = enum.auto()
    SWAMP   = enum.auto()
    MINE    = enum.auto()
    CASTLE  = enum.auto()


class Orientation(enum.Enum):
    EAST    = ( 0, 1)
    SOUTH   = (-1, 0)
    WEST    = (0, -1)
    NORTH   = ( 1, 0)


@dataclasses.dataclass
class Tile:
    suit: Suit
    crowns: int = 0


@dataclasses.dataclass(order=True)
class Domino:
    number: int
    left: Tile
    right: Tile
    orientation: Orientation = Orientation.EAST


@dataclasses.dataclass
class Grid:
    grid: typing.List[Tile] = field(default_factory=self.create_grid)
    playable: typing.List[Tile] = field(default_factory=list)
    union: unionfind.UnionFind
    rules: enum.Rule = Rule.TWO_PLAYERS
    discards: List[Domino] = field(default_factory=list)

    def create_grid(self):
        size = 12 if not self.rules & Rule.MIGHTY_DUEL else 9
        middle = size // 2
        grid = [
            [
                None
                for _ in range(size)
            ]
            for _ in range(size)
        ]
        grid[middle][middle] = Tile(Suit.CASTLE)
        return grid

    def score(self):

        total = [
            (
                sum(
                    self.grid[x][y].crowns
                    for x, y in group
                ),
                len(group)
            )
            for group in union.unions()
        ]

        return (
            sum(
                crowns * tiles
                for crowns, tiles in total
            )
            + self.middle_kingdom_points()
            + self.harmony_points()
        )

    def middle_kingdom_points(self):
        return (
            MIDDLE_KINGDOM_POINTS
            * int(not self.rules & Rule.MIDDLE_KINGDOM)
            * int(self.kingdom_in_middle())
        )

    def kingdom_in_middle(self):
        """Returns False if there are any tiles placed outside the grid."""
        j = 3 if not self.rules & Rule.MIGHTY_DUEL else 0

        return not any(
            any(
                self.grid[1][i],
                self.grid[7 + j][i],
                self.grid[i][1],
                self.grid[i][7 + j],
            )
            for i in range(2, 8 + j)
        )

    def harmony_points(self):
        return (
            HARMONY_POINTS
            * int(not self.rules & Rule.HARMONY)
            * int(not self.discards)
        )

    def _find_matching():
        ...

    def playable_tiles(self, domino, orientation):
        ...

    def _add_to_grid(self, domino, orientation, x, y):
        # check if valid

        grid[x][y] = domino.left
        dx, dy = orientation
        grid[x + dx][y + dy] = domino.right

        self._unionise(domino, orientation, x, y)

    def play(self, domino, orientation, x, y):
        ...

    def _all_tile_edges(self, domino, orientation, x, y):
        dx, dy = orientation
        return (
            _tile_edges(domino.left, x, y)
            + _tile_edges(domino.right, x + dx, y + dy)
        )


    def _tile_edges(self, tile, x, y):
        return [
            ((x, y), (x + i, y + j))
            for i, j in Orientation
        ]

    def _unionise(self, domino, x, y):
        for tile_x, tile_y in _all_tile_edges(domino.left, x, y):
            if tile_x is None or tile_y is None:
                continue
            union.join(edge_x, edge_y)


    def __str__(self):
        colours = [
            "on_grey",
            "on_red",
            "on_green",
            "on_yellow",
            "on_blue",
            "on_magenta",
            "on_cyan",
            "on_white",
        ]
        string = ""
        for row in grid:
            for tile in row:
                if tile is None:
                    char = " "
                elif tile.crowns > 0:
                    char = tile.crowns
                if tile.suit:
                    string += coloured(char, "white", colours[tile.suit])
            string += "\n"
        return string


@dataclasses.dataclass
class Player:
    name: str
    board: Grid
    discards: List[Domino] = dataclasses.field(default_factory=list)
    ...


@dataclasses.dataclass
class Line:
    line: typing.List[typing.Tuple[Domino, Player]]

    def dominos(self):
       return [domino for domino, player in line]

    def selected(self):
        return all(player for domino, player in line)

    def choose(self, player, position):
        if line[position][1] is None:
            line[position][1] = player
        else:
            raise ValueError


@dataclasses.dataclass
class Deck:
    deck = typing.List[Domino]
    draw_num: int
    deck_size: int
    dominos = typing.List[Domino]

    def __init__(self, dominos, draw_num, deck_size):
        self.deck = random.sample(self.dominos, self.deck_size)
        self.deck_size = deck_size
        self.dominos = dominos
        self.draw_num = draw_num

    def draw(self):
        """Returns n dominos from the shuffled deck, sorted by their numbers"""
        return sorted(
            self.deck.pop()
            for _ in range(self.draw_num)
        )

    @staticmethod
    def to_dict(list_):
        return [
            {
                "number": domino.number,
                "left": {
                    "suit": domino.left.suit,
                    "crowns": domino.left.crowns,
                },
                "right": {
                    "suit": domino.right.suit,
                    "crowns": domino.right.crowns,
                },
            }
            for domino in list_
        ]

    def to_json(self, filename):
        with open(filename, 'w') as f:
            json.dump(
                Deck.to_dict(self.dominos),
                f,
                indent=2,
            )

    @classmethod
    def from_json(cls, filename):
        with open(filename) as f:
            dominos = json.load(f)
            return cls(
                Domino(
                    domino["number"],
                    Tile(
                        domino["left"]["suit"],
                        domino["left"]["crowns"],
                    ),
                    Tile(
                        domino["right"]["suit"],
                        domino["right"]["crowns"],
                    ),
                )
                for domino in dominos
            )


@dataclasses.dataclass
class Game:
    players: typing.List[Player]
    line: Line
    deck: Deck
    turn: int = 0
    rules: enum.Rule = Rule.TWO_PLAYERS

    def setup(self):
        ...

    def max_turns(self):
        if not self.rules & Rule.DYNASTY:
            return MaxTurns.DYNASTY
        else not self.rules & Rule.MIGHTY_DUEL:
            return MaxTurns.MIGHTY_DUEL
        else:
            return MaxTurns.STANDARD

    def deck_size(self):
        return self.max_turns() * len(self.players)

    def num_to_draw(self):
        if not self.rules & Rule.THREE_PLAYERS:
            return DrawNum.THREE
        elif not self.rules & (
            Rule.MIGHTY_DUEL
            | Rule.FOUR_PLAYERS
            | Rule.TWO_PLAYERS
        ):
            return DrawNum.FOUR

    def determine_initial_player_order(self):
        random.shuffle(self.players)

    def play(self):
        while self.deck:
            self.turn()
        self.final_score()

    def select(self):
        while not self.line.selected():
            print(self.line)
            self.line.choose(player, position)

    def redraw(self):
        self.line = self.deck.draw(self.num_to_draw())

    def place(self):
        while self.line:
            domino, player = self.line.line.pop(0)
            player.place(domino)

    def turn(self):
        self.select()
        self.redraw()
        self.place()

    def final_score(self):
        for player in self.players:
            print(player, player.grid.score())


if __name__ == "__main__":
    filename = "kingdomino.json"
    d = Deck.from_json(filename)
    d.to_json(filename)
