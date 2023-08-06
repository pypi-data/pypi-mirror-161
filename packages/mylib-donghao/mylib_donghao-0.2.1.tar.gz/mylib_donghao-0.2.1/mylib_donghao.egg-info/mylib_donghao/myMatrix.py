from mylib_donghao.basic_function import *
import numpy as np
import torch
from torch.autograd import Variable
from itertools import product

class myMatrix:
    def __init__(self, l, k=None):
        self.default = 0.0
        if k == None:
            self.mat = np.array(l)
            if len(self.mat.shape) == 1:
                nmat = np.zeros([self.mat.shape[0], 1])
                for i in range(self.mat.shape[0]):
                    nmat[i][0] = self.mat[i]
                self.mat = nmat
        else:
            self.mat = np.zeros([l, k])

    def x(self):
        return self.mat.shape[0]

    def y(self):
        if len(self.mat.shape) == 1:
            return 1
        else:
            return self.mat.shape[1]

    def read(self, i, j=0):
        if i >= self.x() or i < 0 or j >= self.y() or j < 0:
            return self.default
        if len(self.mat.shape) == 1:
            return self.mat[i]
        return self.mat[i][j]

    def set(self, i, j, k):
        if len(self.mat.shape) == 1:
            self.mat[i] = k
        else:
            self.mat[i][j] = k

    def __add__(self, other):
        return myMatrix(self.mat + other.mat)

    def print(self):
        print(self.mat)

    def __sub__(self, other):
        return myMatrix(self.mat - other.mat)

    def __mul__(self, other):
        return myMatrix(np.matmul(self.mat, other.mat))

    def __xor__(self, other):
        if not (self.x() == other.x() and self.y() == other.y()):
            print("Shape is not the same in ^ of myMatrix")
        else:
            X = self.copy()
            for i, j in product(range(self.x()), range(self.y())):
                X.set(i, j, self.read(i, j) * other.read(i, j))
            return X

    def __eq__(self, other):
        self.mat = other.copy().mat
        return self


    def transpose(self):
        return myMatrix(self.mat.transpose())

    def ATA(self):
        return myMatrix(np.matmul(self.mat.transpose(), self.mat))

    def rank(self):
        return np.linalg.matrix_rank(self.mat)

    def inv(self, flg=True):
        x = self.x()
        y = self.y()
        if flg and x == y and self.rank() == x:
            return myMatrix(np.linalg.inv(self.mat))
        else:
            return myMatrix(np.linalg.pinv(self.mat))

    def copy(self):
        return myMatrix(self.mat)

    def trace(self):
        mm = min(self.x(), self.y())
        u = 0
        for i in range(mm):
            u += self.read(i, i)
        return u

    def eig(self):
        e_val, e_vec = np.linalg.eig(self.mat)
        return myMatrix(e_val), myMatrix(e_vec)

    def getline(self, i=0):
        if len(self.mat.shape) == 1:
            return self.copy()
        else:
            m = np.zeros([1, self.y()])
            for j in range(self.y()):
                m[0][j] = self.mat[i][j]
            return myMatrix(m)

    def getcolumn(self, j=0):
        if len(self.mat.shape) == 1:
            return self.copy()
        else:
            return self.transpose().getline(j).transpose()

    def value_up(self):
        u = 0.0
        for i in range(self.x()):
            for j in range(self.y()):
                u += self.read(i, j)
        return u

    def up_single_column(self, m=1.0):
        u = np.zeros([self.x(), 1])
        for i in range(self.x()):
            u[i][0] = self.getline(i).value_up() * m
        return myMatrix(u)

    def up_single_line(self, m=1.0):
        return self.transpose().up_single_column(m).transpose()

    def right_add(self, b):
        return myMatrix(np.append(self.mat, b.mat, axis=1))

    def down_add(self, b):
        return myMatrix(np.append(self.mat, b.mat, axis=0))

    def as_pytorch(self, dtype=torch.float32):
        return Variable(torch.tensor(self.mat, dtype=dtype))

    def random(self, a=-1.0, b=1.0):
        for i in range(self.x()):
            for j in range(self.y()):
                self.set(i, j, randNum(a, b))

    def sigmoid(self, flg=False):
        P = self.copy()
        for i in range(self.x()):
            for j in range(self.y()):
                u = self.read(i, j)
                P.set(i, j, mySigmoid(u))
        if flg:
            self.mat = P.mat
        return P

    def alpha(self, alpha):
        P = self.copy()
        for i in range(self.x()):
            for j in range(self.y()):
                u = self.read(i, j)
                P.set(i, j, u * alpha)
        return P

    def equal(self, y):
        if not (self.x() == y.x() and self.y == y.y()):
            return False
        for i in range(self.x()):
            for j in range(self.y()):
                if not (self.read(i, j) == y.read(i, j)):
                    return False
        return True

    def same(self):
        return myMatrix(self.x(), self.y())



class myMatrixLoader:
#myMatrixLoader是一个向量数据存储器，或者矩阵数据存储器
    def __init__(self):
        self.ptr = 0
        self.matlist = list()
        self.size = 0
        self.flglist = list()

    def append_withMat(self, x, y=None, dim=0):
        if dim == -1:
            self.matlist.append(x)
            self.flglist.append(y)
            self.size += 1
        if dim == 0:
            for j in range(x.y()):
                self.matlist.append(x.getcolumn(j))
                if y is None:
                    self.flglist.append(None)
                else:
                    self.flglist.append(y.getcolumn(j))
                self.size += 1
        if dim == 1:
            x = x.transpose()
            if not y == None:
                y = y.transpose()
            for j in range(x.y()):
                self.matlist.append(x.getcolumn(j))
                if y == None:
                    self.flglist.append(None)
                else:
                    self.flglist.append(y.getcolumn(j))
                self.size += 1

    def append(self, x, y=None, dim=0):
        if istype(x, []):
            for u in x:
                if istype(u, myMatrix(2, 3)):
                    self.append_withMat(u, dim)
        elif istype(x, myMatrix(2, 3)):
            self.append_withMat(x, y, dim)
        else:
            print("Error input in myMatrixLoader's append! Nothing happens.")



    def pointer(self):
        return self.ptr

    def new_pointer(self):
        self.ptr = 0

    def set_pointer(self, x):
        if x >= self.size:
            print("Too large pointer!")
            self.ptr = 0
        else:
            self.ptr = x

    def pop(self):
        if self.size == 0:
            print("Error! Nothing in myMatrixLoader!")
            return None, None
        i = self.ptr
        self.ptr += 1
        if self.ptr == self.size:
            self.ptr = 0
        return self.matlist[i], self.flglist[i]

