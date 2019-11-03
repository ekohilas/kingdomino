import random
import typing
import dataclasses
import csv
import enum
import json
import unionfind
import collections


@dataclasses.dataclass
class Point(typing.NamedTuple):
    x: int
    y: int

    def adjacent_points(self) -> typing.List[Point]:
        return [
            self + direction
            for direction in Direction
        ]

    def adjacent_edges(self) -> typing.List[typing.tuple[Point, Point]]:
        return [
            (self, point)
            for point in self.adjacent_points()
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

    def adjacent_points(self) -> typing.List[Point]:
        return [
            point for point in (
                self.point.adjacent_points()
                + (self.point + self.direction).adjacent_points()
            )
            if point not in (self.point, self.point + self.direction)
        ]

    def adjacent_edges(self) -> typing.List[typing.tuple[Point, Point]]:
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
    discards: List[Domino] = field(default_factory=list)
    grid: typing.List[typing.Optional[Tile]] = field(default_factory=self.create_grid)
    playable: typing.List[Tile] = field(default_factory=list)
    rules: enum.Rule
    union: unionfind.UnionFind = field(default_factory=unionfind.UnionFind)
    size: int = 12 if Rule.MIGHTY_DUEL in self.rules else 9
    middle = Point(size // 2, size // 2)

    def create_grid(self):
        grid = [[None] * self.size for _ in range(size)]
        grid[self.middle.x][self.middle.y] = Tile(Suit.CASTLE)
        return grid

    # SCORING

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
                ...
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
        return any(
            _valid_connection(a, b)
            for a, b in play.adjacent_edges()
        )

    def _valid_connection(self, a: Point, b: Point) -> bool:
        try:
            return any(
                (
                    self._tile_at(a).suit == Tile.CASTLE,
                    self._tile_at(b).suit == Tile.CASTLE,
                    self._matching_suit(a, b),
                )
            )
        except:
            return False

    def _matching_suit(self, a: Point, b: Point) -> bool:
        return self._tile_at(a).suit == self._tile_at(b).suit

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
        return self.gird[point.x][point.y]

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

    def _vacant_points(self) -> typing.List(Point):
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
        self,
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
        elif Rule.MIGHTY_DUEL in self.rules:
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
                (
                    (player.name, player.board.score())
                    for player in self.players
                ),
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
        deck=dominos,
        players=players,
    )
    game.start()
