import random
import csv

class Game:
    players: List[Player]
    turn: int
    line: Line
    deck: Deck

    def setup(self):



    def num_to_draw(self):
        num_players = len(self.players)
        if num_players == 2:
            return 4
        else:
            return num_players

    def determine_player_order(self):
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


DIRS = [
    (1, 0),
    (0, 1),
    (0, -1),
    (-1, 0),
]

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

class Tile:
    suit: Suit
    crowns: int = 0

@dataclasses.dataclass(order=True)
class Domino:
    number: int
    left: Tile
    right: Tile
    orientation: Orientation = Orientation.EAST


class Line:
    line: List[tuple(Domino, Player)]

    def dominos(self):
       return [domino for domino, player in line]

    def selected(self):
        return all(player for domino, player in line)

    def choose(self, player, position):
        if line[position][1] is None:
            line[position][1] = player
        else
            raise ValueError


class Deck:
    deck = List[Domino]

    def draw(self, num=4):
        """Returns n dominos from the shuffled deck, sorted by their numbers"""
        return sorted(
            self.deck.pop()
            for _ in range(num)
        )

    @classmethod
    def from_csv(filename):
        with open(filename, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                deck.append(
                    Domino(
                        row["Tile Number"],
                        Tile(
                            row[],
                            row["#Crowns on First Suit"]),
                        Tile(
                            row[],
                            row["#Crowns on Second"])
                        ),
                    )
                )

    @classmethod
    def from_json(filename):
        with open (filename) as f:
            dominos = json.load(f)
            for domino in dominos:
                self.deck.append(
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
                )

    def shuffle(self):
        random.shuffle(self.deck)


class Grid:
    grid: List[Tile] #= field(default_factory=list)
    playable: List[Tile]
    union: UnionFind

    def score(self):
        return sum(
            crowns * tiles
            for crowns, tiles in union
        )

    def _find_matching
        ...

    def playable_tiles(self, domino, orientation):
        ...

    def _add_to_grid(self, domino, orientation, x, y):
        # check if valid

        grid[x][y] = domino.left
        dx, dy = orientation
        grid[x + dx][y + dy] = domino.right

        self._unionise(domino, orientation, position)

    def play(self, domino, orientation, position):



    def _all_tile_edges(self, domino, orientation, x, y):
        dx, dy = orientation
        return (
            _tile_edges(domino.left, x, y)
            + _tile_edges(domino.right, x + dx, y + dy)
        )


    def _tile_edges(self, tile, x, y):
        return [
            ((x, y), (x + i, y + j))
            for i, j in DIRS
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


class Player:
    name: str
    board: Grid
    ...

if __name__ == "__main__":
    g = Game()
