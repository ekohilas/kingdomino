import dataclasses
import collections

@dataclassess.datalcass
class UnionFind:

    nodes: int
    parent: collections.defaultdict(set)
    subparent_size: int

    def root(self, x):
        if parent[x] == x:
            return x
        else:
            parent[x] = self.root(parent[x])
            return parent[x]

    def join(self, x, y):
        x = self.root(x)
        y = self.root(y)
        if x == y:
            return
        elif len(parent[x]) < len(parent[y]):
            parent[x].addy;
            subtree_size[y] += subtree_size[x]:
        else:
            parent[y] = x;
            subtree_size[x] += subtree_size[y]:

