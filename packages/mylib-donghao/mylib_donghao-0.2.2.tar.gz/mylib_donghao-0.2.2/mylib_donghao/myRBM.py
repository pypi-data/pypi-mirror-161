from mylib_donghao.myMatrix import myMatrix
import torch
import mylib_donghao.basic_function as bf


class RBM:
    '''受限玻尔兹曼机'''
    def __init__(self, input_size, hidden_size):
        self.a = myMatrix(input_size, 1)
        self.b = myMatrix(hidden_size, 1)
        self.a.random()
        self.b.random()
        self.W = myMatrix(hidden_size, input_size)
        self.W.random()

    def hidden(self, v):
        B = None
        for i in range(v.y()):
            if i == 0:
                B = self.b.copy()
            else:
                B = B.right_add(self.b)
        P = self.W * v + B
        return P.sigmoid()

    def visible(self, h):
        A = None
        for i in range(h.y()):
            if i == 0:
                A = self.a.copy()
            else:
                A = A.right_add(self.a)
        P = self.W.transpose() * h + A
        return P.sigmoid()

    def hiddened(self, v):
        P = self.hidden(v)
        for i in range(P.x()):
            for j in range(P.y()):
                if bf.randNum(0, 1) < P.read(i, 0):
                    P.set(i, 0, 1)
                else:
                    P.set(i, 0, 0)
        return P

    def visibled(self, h):
        P = self.visible(h)
        for i in range(P.x()):
            for j in range(P.y()):
                if bf.randNum(0, 1) < P.read(i, 0):
                    P.set(i, 0, 1)
                else:
                    P.set(i, 0, 0)
        return P

    def update(self, dW, da, db):
        self.W = self.W + dW
        self.a = self.a + da
        self.b = self.b + db

    def train(self, v, alpha):
        v1 = v.copy()
        h1 = self.hiddened(v1)
        v2 = self.visibled(h1)
        Q2 = self.hidden(v2)
        dW = myMatrix(self.W.x(), self.W.y())
        for j in range(v1.y()):
            vv1 = v1.getcolumn(j)
            hh1 = h1.getcolumn(j)
            vv2 = v2.getcolumn(j)
            QQ2 = Q2.getcolumn(j)
            d1 = hh1 * vv1.transpose()
            d2 = QQ2 * vv2.transpose()
            dW = dW + d1 - d2
        v1 = v1.up_single_column()
        h1 = h1.up_single_column()
        v2 = v2.up_single_column()
        Q2 = Q2.up_single_column()
        da = v1 - v2
        db = h1 - Q2
        dW = dW.alpha(alpha)
        da = da.alpha(alpha)
        db = db.alpha(alpha)
        self.update(dW, da, db)







