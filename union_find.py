'''
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
'''
'''
from collections import defaultdict

#This class represents a undirected graph using adjacency list representation
class UnionFind:

    def __init__(self, vertices):
        self.V = vertices #No. of vertices
        self.graph = defaultdict(list) # default dictionary to store graph


    # function to add an edge to graph
    def addEdge(self,u,v):
        self.graph[u].append(v)

    # A utility function to find the subset of an element i
    def find_parent(self, parent,i):
        if parent[i] == -1:
            return i
        if parent[i] != -1:
             return self.find_parent(parent, parent[i])

    # A utility function to do union of two subsets
    def union(self,parent,x,y):
        x_set = self.find_parent(parent, x)
        y_set = self.find_parent(parent, y)
        parent[x_set] = y_set
'''
'''
'''
import typing
import dataclasses

@dataclasses.dataclass
class UnionFind:

    '''
    n: int
    parent: typing.List[int] = dataclasses.field(default_factory=list(range(n)))
    subtree_size: typing.List[int] = dataclasses.field(default_factory=list(1 for _ in range(n)))
    '''

    def __init__(self, n):
        self.n = n
        self.parent = list(range(n))
        self.subtree_size = [1] * n

    def root(self, x):

        if self.parent[x] == x:
            return x
        else:
            self.parent[x] = self.root(self.parent[x])
            return self.parent[x]

    def join(self, x, y):

        x = self.root(x)
        y = self.root(y)

        if x == y:
            return
        elif self.subtree_size[x] < self.subtree_size[y]:
            self.parent[x] = y
            self.subtree_size[y] += self.subtree_size[x]
        else:
            self.parent[y] = x
            self.subtree_size[x] += self.subtree_size[y]

    def unions(self):
        d = {}
        for i in range(self.n):
            root = self.root(i)
            if root not in d:
                d[root] = set()
            d[root].add(i)
        return set(d.values())


if __name__ == "__main__":
    u = UnionFind(5)
    u.join(0,1)
    u.join(2,3)
    u.join(3,4)
    for i in range(5):
        print(u.root(i))



