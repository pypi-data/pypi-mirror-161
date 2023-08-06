from mylib_donghao.myMatrix import myMatrix
import mylib_donghao.basic_function as bf
import math
import numpy as np
import time


def dl2mM(x):
    tr = myMatrix(x)
    if len(x) == 1:
        return tr
    else:
        return tr.transpose()


def sigle_core_mul(x1, x2, core='dot'):
    if core == 'dot':
        return (x1.transpose() * x2).read(0)


def core_mul(x_input, core='dot'):
    if core == 'dot':
        return x_input.ATA().mat


def good_SVM_input(x_input, y_input):
    x, y = None, None
    if bf.istype(x_input, []):
        x = dl2mM(x_input)
    else:
        x = x_input.copy()
    if bf.istype(y_input, myMatrix(1, 1)):
        y = y_input.copy()
    else:
        y = myMatrix(y_input)
    return x, y


def SMO(x_input, y_input, C=None, core='dot', epsl=1E-8, N=10000, out_type='myMatrix'):
    x, y = good_SVM_input(x_input, y_input)
    m = x.y()
    if y.x() == 1:
        y = y.transpose()
    if not (y.x() == m):
        print("Error input y in SMO of mySVD. Expect input y is " + str(m))
        exit(-1)
    A = core_mul(x, core)
    a0 = myMatrix(m, 1)
    cnt = 0
    while cnt < N:
        cnt += 1
        a = a0.copy()
        for i in range(m):
            for j in range(m):
                if i == j:
                    continue
                b = 0.5 * (A[i][i] + A[j][j]) - A[i][j]
                yi, yj = y.read(i), y.read(j)
                c = yi * a.read(i) + yj * a.read(j)
                aa = 1.0 - 1.0 * yi / yj + yi * A[j][j] * c - 1.0 * yi * A[i][j] * c
                for t in range(m):
                    if t in [i, j]:
                        continue
                    aa -= 1.0 * a.read(t) * yi * y.read(t) * A[i][t]
                    aa += 1.0 * a.read(t) * yi * y.read(t) * A[j][t]
                if aa * b <= epsl:
                    ai = 0.0
                elif (not (C is None)) and 1.0 * aa / (2.0 * b) > C:
                    ai = C
                else:
                    ai = 1.0 * aa / (2.0 * b)
                aj = -1.0 * yi * ai / yj + 1.0 * c / yj
                if aj < 0.0:
                    ai = 1.0 * c / yi
                    aj = 0.0
                elif (not (C is None)) and aj > C:
                    aj = C
                    ai = -1.0 * yj * aj / yi + 1.0 * c / yi
                a.set(i, 0, ai)
                a.set(j, 0, aj)
        da = a - a0
        a0 = a.copy()
        u = 0.0
        for i in range(m):
            u += da.read(i) * da.read(i)
        u = math.sqrt(u)
        if u <= epsl:
            break
    if out_type == 'myMatrix':
        return a0
    if out_type == 'numpy2d':
        return a0.mat
    if out_type == 'numpy':
        u = np.zeros(m)
        for i in range(m):
            u[i] = a0.read(i)
        return u
    if out_type == 'list':
        u = []
        for i in range(m):
            u.append(a0.read(i))
        return u

def SVM(x_input, y_input, C=None, epsl=1E-8, N=10000, mat_max=10000):
    x, y = good_SVM_input(x_input, y_input)
    a = SMO(x, y, C, 'dot', epsl, N)
    a = a ^ y
    m = a.x()
    if m < mat_max:  #维数不大，使用矩阵相乘
        w = x * a
    else:           #维数很大，利用稀疏性
        w = myMatrix(x.x(), 1)
        for i in range(m):
            if a.read(i) == 0.0:
                continue
            w = w + x.getcolumn(i).alpha(a.read(i))
    cnt = 0.0
    b = 0.0
    for i in range(x.y()):
        if a.read(i) == 0:
            continue
        cnt += 1.0
        b += y.read(i) - (w.transpose() * x.getcolumn(i)).read(0)
    b = b / cnt
    return w, b


class SVM_machine:
    def __init__(self, aiy=None, x=None, b=None, core='dot'):
        self.aiy = aiy
        self.core = core
        self.xt = x
        self.b = b

    def forword(self, x):
        if self.aiy is None or self.xt is None or self.b is None:
            print("Empty SVM machine!")
        u = self.b
        for i in range(self.aiy.x()):
            u += self.aiy.read(i) * sigle_core_mul(self.xt.getcolumn(i), x, self.core)
        return u

    def classify(self, x):
        u = self.forword(x)
        if u >= 0:
            return 1.0
        else:
            return -1.0



def kernel_SVM(x_input, y_input, C=None, core='dot', epsl=1E-8, N=10000):
    x, y = good_SVM_input(x_input, y_input)
    aiy = SMO(x, y, C, core, epsl, N)
    for i in range(aiy.x()):
        aiy.set(i, 0, aiy.read(i) * y.read(i))
    svm = SVM_machine(aiy, x, 0.0, core)
    cnt = 0.0
    b = 0.0
    for i in range(x.y()):
        if aiy.read(i) == 0:
            continue
        cnt += 1.0
        b += y.read(i) - svm.forword(x.getcolumn(i))
    b = b / cnt
    svm.b = b
    return svm



if __name__ == "__main__":
    x = [[1, 2], [2, 3], [3, 3], [2, 1], [3, 2]]
    y = [1, 1, 1, -1, -1]
    w, b = SVM(x, y, mat_max=0)
    w.print()
    svm = kernel_SVM(x, y)
    for i in range(5):
        print(svm.classify(myMatrix(x).transpose().getcolumn(i)))



