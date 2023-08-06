import math
import random
import time

def trigger(p):
    a = random.random()
    if a <= p:
        return True
    else:
        return False


class SAmodel:
    def __init__(self, T0=1, minT=0.01, alpha=0.999, N=1000, epoch=1, maxtest=10000):
        self.E = 0.0
        self.newE = 0.0
        self.x = None
        self.newx = None
        self.T0 = T0
        self.minT = minT
        self.N = N
        self.epoch = epoch
        self.bestx = None
        self.bestE = 0.0
        self.alpha = alpha
        self.maxtest = maxtest
        self.pepoch = 0
        self.bestid = 0

    #转移概率
    def ptrans(self, T):
        if self.newE < self.E:
            return 1.0
        else:
            return math.exp((self.E - self.newE)/T)


    #选择新解，需要根据实际问题手动编程
    def Select(self):
        pass

    #计算解的能量函数,需要根据实际问题手动编程
    def f(self, x):
        return 0.0

    #选取初始解的函数，需要根据实际问题手动编程
    def init_x(self):
        return []

    #选取新解
    def new_x(self, T):
        flg = False
        for i in range(self.maxtest):
            self.Select()
            #计算接受准则
            if trigger(self.ptrans(T)):
                flg = True
                break
        '''
        1、如果返回True，说明在有限次数内存在被接受的转移状态，转移
        2、如果返回false，说明在有限次数内不存在被接受的转移状态，属于结束条件之一
        '''
        return flg

    def bestcondition(self):
        return self.E < self.bestE

    def single_epoch(self):
        record = []
        #选取初始解
        self.x = self.init_x()
        self.E = self.f(self.x)
        if self.bestx is None or self.bestcondition:
            self.bestx, self.bestE = self.x.copy(), self.E
            self.bestid = self.pepoch - 1
        T = self.T0
        cnt = 0
        while T >= self.minT and cnt < self.N:
            #选择新解
            flg = self.new_x(T)
            if flg:
                record.append(self.E)
                self.x, self.E = self.newx.copy(), self.newE
                if self.bestcondition():
                    self.bestx = self.x.copy()
                    self.bestE = self.E
                    self.bestid = self.pepoch - 1
            else:
                break
            #降温
            T *= self.alpha
            cnt += 1
            print(self.E, cnt)
        record.append(self.E)
        return record



