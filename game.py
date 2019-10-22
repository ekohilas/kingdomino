class Game:
    players: List[Player]
    ...

class Suit(enum.Enum):
    WHEAT   = enum.auto()
    FOREST  = enum.auto()
    WATER   = enum.auto()
    GRASS   = enum.auto()
    SWAMP   = enum.auto()
    MINE    = enum.auto()
    CASTLE  = enum.auto()

class Tile:
    suit: Suit
    crowns: int = 0

@dataclasses.dataclass(order=True)
class Domino:
    number: int
    left: Tile
    right: Tile

class Line():
    line: List[Domino]

class Deck:
    deck = List[Domino]

    def draw(self, num=4):
        """Returns n dominos from the shuffled deck, sorted by their numbers"""
        return sorted(
            self.deck.pop()
            for _ in range(num)
        )


    def

class Grid:
    grid: List[Tile] #= field(default_factory=list)

    def tally(self):
        ...

class Player:
    board: Grid
    ...


