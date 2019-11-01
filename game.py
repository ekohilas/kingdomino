import random
import typing
import dataclasses
import csv
import enum
import json
import unionfind


@dataclasses.dataclass
class Point(typing.NamedTuple):
    x: int
    y: int

    def adjacent(self) -> typing.List[Point]:
        return [
            self + direction
            for direction in Direction
        ]


class Color(enum.Flag):
    BLUE    = enum.auto()
    GREEN   = enum.auto()
    RED     = enum.auto()
    YELLOW  = GREEN | RED


class MaxTurns(enum.Int):
    DYNASTY         = 3
    STANDARD        = 6
    MIGHTY_DUEL     = 12


class DrawNum(enum.Int):
    THREE   = 3
    FOUR    = 4


class Points(enum.Int):
    HARMONY         = 5
    MIDDLE_KINGDOM  = 10


class Rule(enum.Flag):
    TWO_PLAYERS     = enum.auto()
    THREE_PLAYERS   = enum.auto()
    FOUR_PLAYERS    = enum.auto()
    DYNASTY         = enum.auto()
    MIDDLE_KINGDOM  = enum.auto()
    HARMONY         = enum.auto()
    MIGHTY_DUEL     = enum.auto()

    @classmethod
    def default(cls, num_players):
        if num_players == 2:
            return cls.TWO_PLAYERS
        if num_players == 3:
            return cls.THREE_PLAYERS
        if num_players == 4:
            return cls.FOUR_PLAYERS


class Suit(enum.Enum):
    WHEAT   = enum.auto()
    FOREST  = enum.auto()
    WATER   = enum.auto()
    GRASS   = enum.auto()
    SWAMP   = enum.auto()
    MINE    = enum.auto()
    CASTLE  = enum.auto()


class Direction(enum.Enum):
    EAST    = Point( 0, 1)
    SOUTH   = Point(-1, 0)
    WEST    = Point( 0, -1)
    NORTH   = Point( 1, 0)


@dataclasses.dataclass
class Player:
    name: str
    color: Color



@dataclasses.dataclass
class Tile:
    suit: Suit
    crowns: int = 0


@dataclasses.dataclass(order=True)
class Domino:
    number: int
    left: Tile
    right: Tile
    direction: Direction = Direction.EAST
    player: Player = None

    def flip(self):
        self.left, self.right = self.right, self.left


@dataclasses.dataclass
class Play:
    domino: Domino
    point: Point
    direction: Direction

    def adjacent(self) -> typing.List[Point]:
        return (
            self.point.adjacent()
            + (self.point + self.direction).adjacent()
        )



@dataclasses.dataclass
class Board:
    discards: List[Domino] = field(default_factory=list)
    grid: typing.List[typing.Optional[Tile]] = field(default_factory=self.create_grid)
    playable: typing.List[Tile] = field(default_factory=list)
    rules: enum.Rule
    union: unionfind.UnionFind = field(default_factory=unionfind.UnionFind)

    def create_grid(self):
        size = 12 if Rule.MIGHTY_DUEL in self.rules else 9
        middle = size // 2
        grid = [[None] * size for _ in range(size)]
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
            * int(Rule.MIDDLE_KINGDOM in self.rules)
            * int(self.kingdom_in_middle())
        )

    def kingdom_in_middle(self):
        """Returns False if there are any tiles placed outside the grid."""
        j = 3 if Rule.MIGHTY_DUEL in self.rules else 0

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
            * int(Rule.HARMONY in self.rules)
            * int(not self.discards)
        )

    def _find_matching():
        ...

    def valid_plays(self, play: Play) -> typing.Set[Play]:
        """Returns a list of all valid plays given a Play containing a domino."""
        assert play.Domino is not None
        directions = iter((play.direction,)) if play.direction else Direction
        points = iter((point,)) if point else self._all_points()
        for point in points:
            for direction in directions:
                ...

    def play(self, play: Play):
        try:
            self._is_valid_play(play)
            self._add_to_grid(play)
            self._unionise(play)


        except:
            raise ValueError

    def _add_to_grid(self, play: Play):

        x, y = play.point
        dx, dy = play.direction
        left, right = play.domino

        self.grid[x][y] = left
        self.grid[x + dx][y + dy] = right

    def _unionise(self, play: Play):
        for point_a, point_b in play.adjacent_points(_all_neighbours(play):
            if point_a is None or point_b is None:
                continue
            union.join(point_a, point_b)


    def _is_valid_play(self, play: Play):
        return all(
            (
                self._within_bounds(play),
                self._matching_nieghbours(play),
                self._n
                play in self.valid_plays(play),
            )
        )







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
class Line:

    def __init__(
        self,
        dominos: typing.List[Domino]
    ):
        self.line = sorted(dominos)

    def pop(self) -> Domino:
        return self.line.pop(0)

    def choose(
        self
        player: Player,
        domino: Domino=None,
        index: int=None
    ) -> None:
        if domino:
            index = self.line.index(domino)
        self.line[index].player = player

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

    def empty(self):
        return bool(self.deck)

    def draw(self):
        """Returns n dominos from the shuffled deck, sorted by their numbers"""
        return [
            self.deck.pop()
            for _ in range(self.draw_num)
        ]

    @staticmethod
    def to_dict(list_: typing.List[Domino]) -> typing.List[
        typing.Dict[
            str,
            typing.Union[
                str,
                typing.Dict[
                    str,
                    str,
                ],
            ]
        ]
    ]:
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
    boards: typing.Dict[Player, Board]
    line: Line
    deck: Deck
    turn: int = 0
    rules: enum.Rule

    def __init__(self, deck, players, rules=None):

        self.players = players

        self.rules = Rule.default(len(self.players))
        self.add_rules(rules)

        self.boards = {
            player: Board(
                rules=self.rules
            ) for player in self.players
        }

        self.set_initial_order()

    def add_rules(self, rules):
        """TODO: add rule checking"""
        if rules:
            self.rules |= rules

    def max_turns(self):
        if Rule.DYNASTY in self.rules:
            return MaxTurns.DYNASTY
        else Rule.MIGHTY_DUEL in self.rules:
            return MaxTurns.MIGHTY_DUEL
        else:
            return MaxTurns.STANDARD

    def deck_size(self):
        return self.max_turns() * len(self.players)

    def num_to_draw(self):
        if Rule.THREE_PLAYERS in self.rules:
            return DrawNum.THREE
        elif (
            Rule.MIGHTY_DUEL | Rule.FOUR_PLAYERS | Rule.TWO_PLAYERS
        ) in self.rules:
            return DrawNum.FOUR

    def set_initial_order(self):
        self.order = random.sample(self.players, len(self.players))

    def start(self):
        self.turn += 1
        while not self.deck.empty():
            self.turn()
        self.final_score()

    def draw(self):
        self.line = Line(
            self.deck.draw(
                self.num_to_draw()
            )
        )

    def select(self):
        while self.order:
            print(self.line)
            self.line.choose(
                input(f"0 - {self.num_to_draw() + 1} : "),
                self.order.pop(0)
            )

    def place(self):
        while not self.line.empty():
            domino = self.line.pop()
            player = domino.player
            board = self.boards[player]

            x, y, z = map(int, input("x, y, z: ").split(", "))
            domino.direction = Direction(z)
            board.play(domino, Point(x, y))
            self.order.append(player)

    def turn(self):
        print(f"Turn {self.turn}")
        self.draw()
        self.select()
        self.place()
        self.turn += 1

    def final_score(self):
        for i, name, score in enumerate(
            sorted(
                player.name, player.board.score() for player in self.players,
                key=lambda x: x[1],
                reversed=True
            ),
            start=1
        ):
            print("{i}. {name}: {score}")


if __name__ == "__main__":

    filename = "kingdomino.json"

    dominos = Deck.from_json(filename)

    players = [
        Player(
            name=input("Player {i} name: "),
            color=Color(i),
        )
        for i in range(int(input("How many players? (2/3/4)")))
    ]

    game = Game(
        deck=dominos
        players=players
    )
    game.start()
