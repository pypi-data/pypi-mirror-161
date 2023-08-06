import math

from mylib_donghao.myMatrix import myMatrix
import numpy as np


#基于myMatrix
def MDS(Z0, new_d=None):
    m = Z0.y()
    d = Z0.x()
    D = myMatrix(m, m)
    for i in range(m):
        for j in range(m):
            u = 0.0
            for k in range(d):
                r = Z0.read(k, i) - Z0.read(k, j)
                u += r * r
            D.set(i, j, u)
    dist = []
    distdd = 0.0
    for i in range(m):
        u = 0.0
        for j in range(m):
            u += D.read(i, j)
        u /= m
        dist.append(u)
        distdd += u
    distdd /= m
    B = myMatrix(m, m)
    for i in range(m):
        for j in range(m):
            u = -0.5 * (D.read(i, j) - dist[i] - dist[j] + distdd)
            B.set(i, j, u)
    val, vec = B.eig()
    val.mat = np.real(val.mat)
    vec.mat = np.real(vec.mat)
    I = np.argsort(-val.mat)
    cnt = 0
    for i in range(m):
        if val.read(I[i]) > 0:
            cnt += 1
        else:
            break
    if new_d == None:
        new_d = cnt
    new_d = min(new_d, cnt)
    T = myMatrix(m, new_d)
    for jj in range(new_d):
        j = I[jj]
        r1 = math.sqrt(val.read(j))
        for i in range(m):
            T.set(i, j, r1 * vec.read(i, j))
    return T.transpose()

#主成分分析
def PCA(D, dxing):
    m = D.y()
    tr = D.up_single_column(1.0/m)
    X = D.getcolumn(0) - tr
    for j in range(1, m):
        X = X.right_add(D.getcolumn(j) - tr)
    XX = X * X.transpose()
    val, vec = XX.eig()
    val.mat = np.real(val.mat)
    vec.mat = np.real(vec.mat)
    I = np.argsort(-val.mat)
    T = 0
    limda = myMatrix(dxing, 1)
    for jj in range(dxing):
        if jj == 0:
            T = vec.getcolumn(I[jj])
        else:
            T = T.right_up(vec.getcolumn(I[jj]))
        limda.set(jj, 0, val.read(I[jj]))
    return T, X, limda

def PCA_Transform(D, dxing):
    W, X, limda = PCA(D, dxing)
    return W.transpose() * X, limda









