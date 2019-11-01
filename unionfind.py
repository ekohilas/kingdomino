import typing
import dataclasses

#http://code.activestate.com/recipes/577225-union-find/

T = typing.TypeVar('T')


@dataclasses.dataclass
class Node(typing.Generic[T]):
    item: typing.Generic[T]
    parent: 'Node' = self
    size: int = 1


@dataclasses.dataclass
class UnionFind:

    def find(self, n: Node) -> T:
        if n.parent == x:
            return n.item
        else:
            n.parent = self.root(n.parent)
            return n.parent.item

    def join(self, x: Node, y: Node) -> None:

        root_x = self.find(x)
        root_y = self.find(y)

        if root_x == root_y:
            return

        if root_x.size < root_y.size:
            root_x, root_y = root_y, root_x

        root_y.parent = root_x
        root_x.size += root_y.size

    def unions(self):
        d = {}
        for i in range(self.n):
            root = self.find(i)
            if root not in d:
                d[root] = set()
            d[root].add(i)
        return {x.item for item in d.values()}


if __name__ == "__main__":
    u = UnionFind()
    u.join(Node(0),Node(1))
    u.join(Node(2),Node(3))
    u.join(Node(3),Node(4))
    for i in range(5):
        print(u.root(i))
