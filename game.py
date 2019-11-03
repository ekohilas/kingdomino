import random
import typing
import dataclasses
import csv
import enum
import json
import unionfind
import collections
import colored

class InvalidPlay(ValueError):
    pass

@dataclasses.dataclass(frozen=True)
class Point:
    x: int
    y: int

    def __add__(self, other):
        if isinstance(other, Direction):
            other = other.value
        return Point(self.x + other.x, self.y + other.y)

    def adjacent_points(self) -> typing.List["Point"]:
        return [
            self + direction
            for direction in Direction
        ]

    def adjacent_edges(self) -> typing.List[typing.Tuple["Point", "Point"]]:
        return [
            (self, point)
            for point in self.adjacent_points()
        ]


class Color(enum.Flag):
    BLUE    = enum.auto()
    GREEN   = enum.auto()
    RED     = enum.auto()
    YELLOW  = GREEN | RED


class MaxTurns(enum.IntEnum):
    DYNASTY         = 3
    STANDARD        = 6
    MIGHTY_DUEL     = 12


class DrawNum(enum.IntEnum):
    THREE   = 3
    FOUR    = 4


class Points(enum.IntEnum):
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
    FOREST  = enum.auto()
    GRASS   = enum.auto()
    MINE    = enum.auto()
    SWAMP   = enum.auto()
    WATER   = enum.auto()
    WHEAT   = enum.auto()
    CASTLE  = enum.auto()
    NONE    = enum.auto()


    @classmethod
    def from_string(cls, string: str):
        return {
            "forest": cls.FOREST,
            "grass" : cls.GRASS,
            "mine"  : cls.MINE,
            "swamp" : cls.SWAMP,
            "water" : cls.WATER,
            "wheat" : cls.WHEAT,
        }[string]

    def to_string(self) -> str:
        return {
            Suit.FOREST:    "forest",
            Suit.GRASS:     "grass",
            Suit.MINE:      "mine",
            Suit.SWAMP:     "swamp",
            Suit.WATER:     "water",
            Suit.WHEAT:     "wheat",
        }[self]

    def to_color(self) -> str:
        return {
            Suit.FOREST:    "dark_green",
            Suit.GRASS:     "light_green",
            Suit.MINE:      "grey_0",
            Suit.SWAMP:     "light_slate_grey",
            Suit.WATER:     "blue",
            Suit.WHEAT:     "yellow",
            Suit.CASTLE:    "white",
            Suit.NONE:      "default",
        }[self]


class Direction(enum.Enum):
    EAST    = Point( 1, 0)
    SOUTH   = Point( 0, 1)
    WEST    = Point(-1, 0)
    NORTH   = Point( 0,-1)

    @classmethod
    def from_string(cls, string: str):
        return {
            "east":     cls.EAST,
            "south":    cls.SOUTH,
            "west":     cls.WEST,
            "north":    cls.NORTH,
        }[string]


@dataclasses.dataclass(frozen=True)
class Player:
    name: str
    color: Color


@dataclasses.dataclass(frozen=True)
class Tile:
    suit: Suit
    crowns: int = 0

    def __str__(self):
        if self.suit == Suit.CASTLE:
            char = "C"
        elif self.crowns == 0:
            char = " "
        else:
            char = self.crowns

        return colored.stylize(
            char,
            colored.fg("white") + colored.bg(self.suit.to_color())
        )


@dataclasses.dataclass(order=True)
class Domino:
    number: int
    left: Tile
    right: Tile
    direction: Direction = Direction.EAST
    player: Player = None

    def flip(self):
        self.left, self.right = self.right, self.left

    def __str__(self):
        return f"{self.left}{self.right}"


@dataclasses.dataclass
class Play:
    domino: Domino
    point: Point
    direction: Direction

    def adjacent_points(self) -> typing.List[Point]:
        return [
            point for point in (
                self.point.adjacent_points()
                + (self.point + self.direction).adjacent_points()
            )
            if point not in (self.point, self.point + self.direction)
        ]

    def adjacent_edges(self) -> typing.List[typing.Tuple[Point, Point]]:
        return [
            edge for edge in (
                self.point.adjacent_edges()
                + (self.point + self.direction).adjacent_edges()
            )
            if edge not in (
                (self.point, self.point + self.direction),
                (self.point + self.direction, self.point),
            )
        ]


@dataclasses.dataclass
class Board:
    rules: Rule
    discards: typing.List[Domino] = dataclasses.field(default_factory=list)
    playable: typing.List[Tile] = dataclasses.field(default_factory=list)
    union: unionfind.UnionFind = dataclasses.field(default_factory=unionfind.UnionFind)

    def __post_init__(self):
        self.size = 12 if Rule.MIGHTY_DUEL in self.rules else 9
        half = self.size // 2
        self.middle = Point(half, half)
        self.grid = self.create_grid()

    def create_grid(self) -> typing.List[typing.List[typing.Optional[Tile]]]:
        grid = [[None] * self.size for _ in range(self.size)]
        grid[self.middle.x][self.middle.y] = Tile(Suit.CASTLE)
        return grid

    # SCORING

    def crowns_and_tiles(self) -> typing.List[typing.Tuple[int, int]]:
        return [
            (
                sum(
                    self.grid[point.x][point.y].crowns
                    for point in points
                ),
                len(points)
            )
            for points in self.union.groups()
        ]

    def points(self):
        return (
            sum(
                crowns * tiles
                for crowns, tiles in self.crowns_and_tiles()
            )
            + self.middle_kingdom_points()
            + self.harmony_points()
        )

    def crowns(self):
        return sum(lambda x: x[1] for x in self.crowns_and_tiles)

    def middle_kingdom_points(self):
        return (
            Points.MIDDLE_KINGDOM
            * int(Rule.MIDDLE_KINGDOM in self.rules)
            * int(self.kingdom_in_middle())
        )

    def kingdom_in_middle(self):
        """Returns False if there are any tiles placed outside the grid."""
        j = 3 if Rule.MIGHTY_DUEL in self.rules else 0

        return not any(
            any(
                (
                    self.grid[1][i],
                    self.grid[7 + j][i],
                    self.grid[i][1],
                    self.grid[i][7 + j],
                )
            )
            for i in range(2, 8 + j)
        )

    def harmony_points(self):
        return (
            Points.HARMONY
            * int(Rule.HARMONY in self.rules)
            * int(not self.discards)
        )

    # PLAY VALIDATION

    def play(self, play: Play):
        if not self.valid_play(play):
            raise InvalidPlay

        self._add_to_grid(play)
        self._unionise(play)

    def valid_play(self, play: Play):
        return all(
            (
                self._play_within_bounds(play),
                self._valid_adjacent(play),
            )
        )

    def _play_within_bounds(self, play: Play) -> bool:
        return (
            self._within_bounds(play.point)
            and self._within_bounds(play.point + play.direction)
        )

    def _within_bounds(self, point: Point) -> bool:
        return 0 <= point.x < self.size and 0 <= point.y < self.size

    def _valid_adjacent(self, play: Play) -> bool:
        print(any(
            self._valid_connection(x, y)
            for x, y in play.adjacent_edges()
        ))
        return any(
            self._valid_connection(x, y)
            for x, y in play.adjacent_edges()
        )

    def _valid_connection(self, a: Point, b: Point) -> bool:
        # TODO wtf?
        if self._tile_at(b) or self._tile_at(b):
            pass#print(self._tile_at(b).suit)
        val = None
        try:
            val = any(
                (
                    self._tile_at(a).suit == Suit.CASTLE,
                    self._tile_at(b).suit == Suit.CASTLE,
                    self._matching_suit(a, b),
                )
            )
            val = self._tile_at(b).suit == Suit.CASTLE
        except:
            val = False
        print(val)
        return val

    def _matching_suit(self, x: Point, y: Point) -> bool:
        return self._tile_at(x).suit == self._tile_at(y).suit

    def _add_to_grid(self, play: Play) -> None:
        x, y = play.point
        dx, dy = play.direction
        self.grid[x][y] = play.domino.left
        self.grid[x + dx][y + dy] = play.domino.right

    def _unionise(self, play: Play) -> None:
        for a, b in play.adjacent_edges():
            if self._tile_at(a) is None or self._tile_at(b) is None:
                continue
            if self._matching_suit(a, b):
                self.union.join(a, b)

    def _tile_at(self, point):
        return self.grid[point.x][point.y]

    # VALIDATION

    def valid_plays(self, play: Play) -> typing.Set[Play]:
        """Returns a list of all valid plays given a Play containing a domino."""
        assert play.domino is not None
        valid = []
        directions = (play.direction,) if play.direction else Direction
        points = (play.point,) if play.point else self._vacant_points()
        for point in points:
            for direction in directions:
                new_play = Play(
                    domino=play.domino,
                    point=point,
                    direction=direction
                )
                if self._valid_play(new_play):
                    valid.append(new_play)

        return valid

    def _vacant_points(self) -> typing.List[Point]:
        vacant_points = []
        seen = set()
        queue = collections.deque(self.middle)
        while queue:

            point = queue.popleft()
            if point in seen:
                continue

            seen.add(point)
            for new_point in point.adjacent_points():
                if not self._within_bounds(new_point):
                    continue
                if self._tile_at(new_point) is None:
                    vacant_points.append(new_point)
                else:
                    queue.append(new_point)

        return vacant_points

    def __str__(self):
        string = " " + "".join(map(str, range(self.size))) + "\n"
        for i, row in enumerate(self.grid):
            string += str(i)
            for tile in row:
                string += str(tile) if tile else " "
            string += "\n"
        return string


class Line:

    def __init__(
        self,
        dominos: typing.List[Domino]
    ):
        self.line = sorted(dominos)

    def pop(self) -> Domino:
        return self.line.pop(0)

    def empty(self) -> bool:
        return not self.line

    def choose(
        self,
        player: Player,
        index: int=None,
        domino: Domino=None,
    ) -> None:
        if domino:
            index = self.line.index(domino)
        self.line[index].player = player

    def __str__(self):
        return "\n".join(
            f"{' ' if domino.player else i}: {domino}"
            for i, domino in enumerate(self.line)
        )


class Dominoes(list):

    @staticmethod
    def to_dict(self) -> typing.List[
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
                    "suit": domino.left.suit.to_string(),
                    "crowns": domino.left.crowns,
                },
                "right": {
                    "suit": domino.right.suit.to_string(),
                    "crowns": domino.right.crowns,
                },
            }
            for domino in self
        ]

    def to_json(self, filename: str) -> None:
        with open(filename, 'w') as f:
            json.dump(
                self.to_dict(),
                f,
                indent=2,
            )

    @classmethod
    def from_json(cls, filename):
        with open(filename) as f:
            dominos = json.load(f)
            return cls(
                Domino(
                    number=int(domino["number"]),
                    left=Tile(
                        suit=Suit.from_string(domino["left"]["suit"]),
                        crowns=int(domino["left"]["crowns"]),
                    ),
                    right=Tile(
                        suit=Suit.from_string(domino["right"]["suit"]),
                        crowns=int(domino["right"]["crowns"]),
                    ),
                )
                for domino in dominos
            )


class Deck:

    def __init__(
        self,
        dominoes: Dominoes,
        deck_size: int,
        draw_num: int,
    ):
        self.deck_size = deck_size
        self.draw_num = draw_num
        self.deck = random.sample(dominoes, self.deck_size)

    def empty(self):
        return not bool(self.deck)

    def draw(self):
        """Returns n dominos from the shuffled deck, sorted by their numbers"""
        return [
            self.deck.pop()
            for _ in range(self.draw_num)
        ]


@dataclasses.dataclass
class Game:
    boards: typing.Dict[Player, Board]
    line: Line
    turn_num: int = 0

    def __init__(
        self,
        dominoes: Dominoes,
        players: typing.List[Player],
        rules: Rule=None,
    ):
        self.players = players
        self.rules = Rule.default(len(self.players))
        self.add_rules(rules)

        self.deck = Deck(
            dominoes=dominoes,
            draw_num=self.num_to_draw(),
            deck_size=self.deck_size(),
        )

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
        elif Rule.MIGHTY_DUEL in self.rules:
            return MaxTurns.MIGHTY_DUEL
        else:
            return MaxTurns.STANDARD

    def deck_size(self):
        return self.max_turns() * len(self.players)

    def num_to_draw(self):
        if Rule.THREE_PLAYERS in self.rules:
            return DrawNum.THREE
        elif self.rules in (
            Rule.MIGHTY_DUEL,
            Rule.FOUR_PLAYERS,
            Rule.TWO_PLAYERS,
        ):
            return DrawNum.FOUR
        else:
            raise ValueError

    def set_initial_order(self):
        self.order = random.sample(self.players, len(self.players))

    def start(self):
        self.turn_num += 1
        while not self.deck.empty():
            self.turn()
        self.final_score()

    def draw(self):
        self.line = Line(self.deck.draw())

    def select(self):
        while self.order:
            print(self.line)
            self.line.choose(
                self.order.pop(0),
                int(input(f"> ")),
            )

    def place(self):
        while not self.line.empty():
            domino = self.line.pop()
            player = domino.player
            board = self.boards[player]

            print(board)
            x, y, direction = input("x y direction: ").split()
            board.play(
                Play(
                    domino=domino,
                    point=Point(int(x), int(y)),
                    direction=Direction.from_string(direction),
                )
            )
            self.order.append(player)

    def turn(self):
        print(f"Turn {self.turn_num}")
        self.draw()
        self.select()
        self.place()
        self.turn_num += 1

    def final_score(self):
        for i, (name, points) in enumerate(
            sorted(
                (
                    (player.name, self.boards[player].points())
                    for player in self.players
                ),
                key=lambda x: x[1],
                reverse=True,
            ),
            start=1
        ):
            print(f"{i}. {name}: {points}")


if __name__ == "__main__":

    filename = "kingdomino.json"

    dominoes = Dominoes.from_json(filename)

    players = [
        Player(
            name=input(f"Player {i+1} name: "),
            color=Color(i),
        )
        for i in range(int(input("How many players? (2/3/4): ")))
    ]

    game = Game(
        dominoes=dominoes,
        players=players,
    )
    game.start()
