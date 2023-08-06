import pickle
import numpy as np
import multiprocessing as mlt
import random
import math
from itertools import product

#使用pickle进行的python文件的读写
def pkl_save(a, path):
    with open(path, "wb") as f:
        pickle.dump(a, f)

def myexp(x):
    if x >= 30:
        return 100000000
    if x <= -30:
        return 0
    return math.exp(x)

def pkl_load(path):
    with open(path, "rb") as f:
        argfile = pickle.load(f)
    return argfile

#判断a, b的类型是否一样
def istype(a, b):
    return type(a) == type(b)

#生成a，b间的一个随机数(不包括上界b，但是无关紧要)
def randNum(a, b=None):
    if b == None:
        b = a
        a = 0
    random.seed()
    k = b - a
    u = random.random()
    v = u * k + a
    return v

def randInt(a, b=None):
    if b == None:
        b = a
        a = 0
    v = math.floor(randNum(a, b))
    return v

def FindListMax(t):
    if not istype(t, []):
        return t, 0
    o = 0
    for i in range(len(t)):
        if t[i] > t[o]:
            o = i
    return o, t[o]

def FindListMin(t):
    if not istype(t, []):
        return t, 0
    o = 0
    for i in range(len(t)):
        if t[i] < t[o]:
            o = i
    return o, t[o]

def range_split(a, b, n):
    k = (b-a)/n
    k = math.floor(k)
    u = []
    t = a
    for i in range(n-1):
        u.append([t, t+k])
        t += k
    u.append([t, b])
    return u


def mySigmoid(x):
    return 1 / (1 + myexp(-x))


def mixed_range2(a, b):
    return product(range(a), range(b))


def mixed_range3(a, b, c):
    return product(range(a), range(b), range(c))


#zip方法   product方法




