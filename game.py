import random
import typing
import dataclasses
import csv
import enum
import json
import unionfind
import collections
import colored

# TODO
# check that the input is within the 5x5 grid
# handle discards

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


class Color(enum.Enum):
    BLUE        = "blue"
    GREEN       = "light_green"
    RED         = "red"
    YELLOW      = "yellow"
    DARK_GREEN  = "dark_green"
    GREY        = "light_slate_grey"
    DARK_GREY   = "grey_0"
    WHITE       = "white"
    NONE        = "default"


class MaxTurns(enum.IntEnum):
    STANDARD    = 12
    MIGHTY_DUEL = 24


class DrawNum(enum.IntEnum):
    THREE   = 3
    FOUR    = 4


class GridSize(enum.IntEnum):
    STANDARD    = 5
    MIGHTY_DUEL = 7


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
            Suit.FOREST:    Color.DARK_GREEN,
            Suit.GRASS:     Color.GREEN,
            Suit.MINE:      Color.DARK_GREY,
            Suit.SWAMP:     Color.GREY,
            Suit.WATER:     Color.BLUE,
            Suit.WHEAT:     Color.YELLOW,
            Suit.CASTLE:    Color.WHITE,
            Suit.NONE:      Color.NONE,
        }[self]


class Direction(enum.Enum):
    EAST    = Point( 0, 1)
    SOUTH   = Point( 1, 0)
    WEST    = Point( 0,-1)
    NORTH   = Point(-1, 0)

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
            colored.fg("white") + colored.bg(self.suit.to_color().value)
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

    def left_adjacent_points(self) -> typing.List[Point]:
        return [
            point for point in self.point.adjacent_points()
            if point != self.point + self.direction
        ]

    def right_adjacent_points(self) -> typing.List[Point]:
        return [
            point for point in (self.point + self.direction).adjacent_points()
            if point != self.point
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
class Grid:

    def __init__(self, size):
        self.size = size
        self.max_size = size * 2 - 1
        self.half = size - 1
        self.middle = Point(self.half, self.half)

        self.grid = [[None] * self.max_size for _ in range(self.max_size)]
        self.grid[self.middle.x][self.middle.y] = Tile(Suit.CASTLE)

        self.max_x = self.half
        self.max_y = self.half
        self.min_x = self.half
        self.min_y = self.half

    def __getitem__(self, point: Point) -> typing.Optional[Tile]:
        return self.grid[point.x][point.y]

    def __setitem__(self, point: Point, tile: Tile) -> None:
        self.max_x = max(self.max_x, point.x)
        self.max_y = max(self.max_y, point.y)
        self.min_x = min(self.min_x, point.x)
        self.min_y = min(self.min_y, point.y)
        self.grid[point.x][point.y] = tile

    def within_grid(self, point: Point) -> bool:
        return 0 <= point.x < self.max_size and 0 <= point.y < self.max_size

    def within_bounds(self, point: Point) -> bool:
        max_x = max(self.max_x, point.x)
        max_y = max(self.max_y, point.y)
        min_x = min(self.min_x, point.x)
        min_y = min(self.min_y, point.y)
        return max_x - min_x < self.size and max_y - min_y < self.size

    def within(self, point: Point) -> bool:
        return self.within_grid(point) and self.within_bounds(point)

    # TODO remove to remove dependancy on play
    def _play_to_points(self, play: Play) -> typing.Tuple[Point]:
        return (play.point, play.point + play.direction)

    def add(self, play: Play) -> None:
        left, right = self._play_to_points(play)
        self[left] = play.domino.left
        self[right] = play.domino.right


    def bounded(self) -> bool:
        """Returns False if there are any tiles placed outside the grid."""
        return not any(
            any(
                (
                    self.grid[1][i],
                    self.grid[self.size - 2][i],
                    self.grid[i][1],
                    self.grid[i][self.size - 2],
                )
            )
            for i in range(2,  self.max_size - 1)
        )

    def __str__(self):
        return "".join(
            (
                " ",
                "".join(map(str, range(self.max_size))),
                "\n",
                "\n".join(
                    str(i)
                    + "".join(
                        str(tile) if tile else " "
                        for tile in row
                    )
                    for i, row in enumerate(self.grid)
                ),
            )
        )


@dataclasses.dataclass
class Board:
    rules: Rule
    discards: typing.List[Domino] = dataclasses.field(default_factory=list)
    playable: typing.List[Tile] = dataclasses.field(default_factory=list)
    union: unionfind.UnionFind = dataclasses.field(default_factory=unionfind.UnionFind)

    def __post_init__(self):
        self.grid = Grid(
            GridSize.MIGHTY_DUEL
            if Rule.MIGHTY_DUEL in self.rules
            else GridSize.STANDARD
        )

    # SCORING

    def crowns_and_tiles(self) -> typing.List[typing.Tuple[int, int]]:
        return [
            (
                sum(
                    self.grid[point].crowns
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
        return sum(crowns for crowns, tiles in self.crowns_and_tiles())

    def middle_kingdom_points(self):
        return (
            Points.MIDDLE_KINGDOM
            * int(Rule.MIDDLE_KINGDOM in self.rules)
            * int(self.grid.bounded())
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

        self.grid.add(play)
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
            self.grid.within(play.point)
            and self.grid.within(play.point + play.direction)
        )

    def _valid_adjacent(self, play: Play) -> bool:
        return (
            any(
                self._valid_connection(self.grid[point], play.domino.left)
                for point in play.left_adjacent_points()
                if self.grid.within(point)
            )
            or any(
                self._valid_connection(self.grid[point], play.domino.right)
                for point in play.right_adjacent_points()
                if self.grid.within(point)
            )
        )

    def _valid_connection(self, a: typing.Optional[Tile], b: Tile) -> bool:
        return a is not None and any(
            (
                a.suit == Suit.CASTLE,
                a.suit == b.suit,
            )
        )

    def _unionise(self, play: Play) -> None:
        for a, b in play.adjacent_edges():
            tile_a = self.grid[a]
            tile_b = self.grid[b]
            if tile_a is None or tile_b is None:
                continue
            if tile_a.suit == tile_b.suit:
                self.union.join(a, b)

    # VALIDATION

    def valid_plays(
            self,
            domino: Domino,
            point: typing.Optional[Point]=None,
            direction: typing.Optional[Direction]=None
    ) -> typing.Set[Play]:
        """Returns a list of all valid plays given a Play containing a domino."""
        valid = []
        directions = (direction,) if direction else Direction
        points = (point,) if point else self._vacant_points()
        for point in points:
            for direction in directions:
                new_play = Play(
                    domino=domino,
                    point=point,
                    direction=direction
                )
                if self.valid_play(new_play):
                    valid.append(new_play)

        return valid

    def _vacant_points(self) -> typing.List[Point]:
        vacant_points = []
        seen = set()
        frontier = collections.deque((self.grid.middle, ))
        while frontier:

            point = frontier.popleft()
            if point in seen:
                continue
            else:
                seen.add(point)

            for new_point in point.adjacent_points():
                if not self.grid.within(new_point):
                    continue
                if self.grid[new_point] is None:
                    vacant_points.append(new_point)
                else:
                    frontier.append(new_point)

        return vacant_points

    def __str__(self) -> str:
        return str(self.grid)


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
            (
                colored.stylize(" ", colored.bg(domino.player.color.value))
                if domino.player else str(i)
            )
            + f": {domino}"
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
        if Rule.MIGHTY_DUEL in self.rules:
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
        if Rule.TWO_PLAYERS in self.rules:
            self.order *= 2

    def start(self):
        self.turn_num += 1
        while not self.deck.empty():
            self.turn()
        self.final_score()

    def draw(self):
        self.line = Line(self.deck.draw())

    def select(self):
        while self.order:
            player = self.order.pop(0)
            print(self.line)
            while True:
                try:
                    self.line.choose(
                        player,
                        int(input(f"{player.name}: ")),
                    )
                except (InvalidPlay, ValueError):
                    continue
                else:
                    break

    def place(self):
        while not self.line.empty():
            domino = self.line.pop()
            player = domino.player
            board = self.boards[player]

            print(board)
            print(domino)
            while True:
                try:
                    plays = self.boards[player].valid_plays(domino)
                    if not plays:
                        self.discards.append(domino)
                        break
                    print(plays)
                    x, y, direction = input("x y direction: ").split()
                    board.play(
                        Play(
                            domino=domino,
                            point=Point(int(x), int(y)),
                            direction=Direction.from_string(direction),
                        )
                    )
                except InvalidPlay:
                    continue
                else:
                    break

            self.order.append(player)

    def turn(self):
        print(f"Turn {self.turn_num}/{self.max_turns()}")
        self.draw()
        self.select()
        self.place()
        self.turn_num += 1

    def final_score(self):
        for i, (points, crowns, player) in enumerate(
            sorted(
                (
                    (
                        self.boards[player].points(),
                        self.boards[player].crowns(),
                        player,
                    )
                    for player in self.players
                ),
                reverse=True,
            ),
            start=1
        ):
            print(f"{i}. {player.name}: {points}")
            print(self.boards[player])

def split_stream(func, filename):
    def wrapper(*args, **kwargs):
        with open(filename, "a") as f:
            output = func(*args, **kwargs)
            print(output, file=f)
        return output
    return wrapper

record = False
if record:
    input = split_stream(input, "3.in")

if __name__ == "__main__":

    filename = "kingdomino.json"

    dominoes = Dominoes.from_json(filename)

    random.seed(0)

    players = [
        Player(
            name=input(f"Player {i+1} name: "),
            color=color
        )
        for i, color in zip(
            range(int(input("How many players? (2/3/4): "))),
            Color,
        )
    ]

    game = Game(
        dominoes=dominoes,
        players=players,
    )
    game.start()
