from mylib_donghao.myMatrix import myMatrix as Matrix
import mylib_donghao.basic_function as bf
import numpy as np

class Graph:
    def __init__(self, nodeType=1):
        self.V = list()
        self.type = nodeType
        if bf.istype(nodeType, 1):
            self.E = list()
        else:
            self.E = dict()

    def copy(self):
        g = Graph(self.type)
        g.V = self.V.copy()
        g.E = self.E.copy()
        return g

    def edge(self, a, b):
        if bf.istype(self.type, 1):
            u = self.E[a][b]
        else:
            u = self.E.get([a, b], default=None)
        return u

    def addNode(self, nod=None):
        if nod is None:
            n = len(self.V)
            self.V.append(n)
        else:
            self.V.append(nod)
        if bf.istype(self.type, 1):
            for i in range(len(self.E)):
                self.E[i].append(None)
            t = [None for i in range(len(self.V))]
            self.E.append(t)

    def addEdge(self, a, b, v, directed = False):
        if bf.istype(self.type, 1):
            self.E.update({[a, b]: v})
        else:
            self.E[a][b] = v
        if ~directed:
            if bf.istype(self.type, 1):
                self.E.update({[b, a]: v})
            else:
                self.E[b][a] = v

    def deleteEdge(self, a, b, directed):
        if bf.istype(self.type, 1):
            self.E.pop([a, b])
        else:
            self.E[a][b] = None
        if ~directed:
            if bf.istype(self.type, 1):
                self.E.pop([b, a])
            else:
                self.E[b][a] = None

    def setEdge(self, a, b, v, directed=False):
        self.addEdge(a, b, v, directed)

    def __add__(self, b):
        if bf.istype(self.type, b.type):
            if bf.istype(self.type, 1):
                l = max(len(self.V), len(b.V))
                g = Graph(1)
                g.V = [i for i in range(l)]
                g.E = [[None for i in range(l)] for j in range(l)]
                for i, j in bf.mixed_range2(l, l):
                    if (i < len(self.V)) and (j < len(self.V)):
                        g.E[i][j] = self.edge(i, j)
                    if (i < len(b.V)) and (j < len(b.V)):
                        g.E[i][j] = b.edge(i, j)
                return g
            else:
                g = Graph('a')
                v = self.V.copy()
                for i in range(len(b.V)):
                    if b.V[i] not in v:
                        v.append(b.V[i])
                g.V = v
                g.E = self.E.copy()
                g.E.update(b.E)
                return g
        else:
            print("Two Graph is not the same type! One is numbered and the other is nodes!")
            return None



g1 = Graph("a")
g2 = Graph("b")
g1.addNode("a")
g1.addNode("b")
g2.addNode("a")
g2.addNode("c")
print((g1+g2).V)
