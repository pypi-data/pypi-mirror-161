import mylib_donghao.myMatrix as myMatrix
import scipy
from scipy import optimize
import pulp
import mylib_donghao.basic_function as bf


def myMatrix2numpy4LP(c, A, b, Aeq, beq, lb, ub):
    mm = myMatrix.myMatrix(1, 1)
    if bf.istype(c, mm):
        if c.y() == 1:
            c = c.transpose()
        c = c.mat[0]
        if len(c.shape) == 2:
            c = c[0]
    if bf.istype(A, mm):
        A = A.mat
    if bf.istype(b, mm):
        if b.y() == 1:
            b = b.transpose()
        b = b.mat
        if len(b.shape) == 2:
            b = b[0]
    if bf.istype(Aeq, mm):
        Aeq = Aeq.mat
    if bf.istype(beq, mm):
        if beq.y() == 1:
            beq = beq.transpose()
        beq = beq.mat
        if len(beq.shape) == 2:
            beq = beq[0]
    if bf.istype(lb, mm):
        if lb.y() == 1:
            lb = lb.transpose()
        lb = lb.mat
        if len(lb.shape) == 2:
            lb = lb[0]
    if bf.istype(ub, mm):
        if ub.y() == 1:
            ub = ub.transpose()
        ub = ub.mat
        if len(ub.shape) == 2:
            ub = ub[0]
    return c, A, b, Aeq, beq, lb, ub

def minLinearProgramming_with_scipy(c, A, b=None, Aeq=None, beq=None, lb=None, ub=None, r=1.0):
    c, A, b, Aeq, beq, lb, ub = myMatrix2numpy4LP(c.alpha(r), A, b, Aeq, beq, lb, ub)
    bound = (lb, ub)
    res = optimize.linprog(c, A, b, Aeq, beq, bound)
    x = myMatrix.myMatrix(res.x)
    fun = res.fun
    return fun, x, res







