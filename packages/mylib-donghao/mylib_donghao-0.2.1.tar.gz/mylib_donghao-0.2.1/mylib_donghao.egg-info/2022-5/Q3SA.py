#需要安装openpyxl库，安装方法为   pip install openpyxl
import pandas as pd
import random
from SAmodel import SAmodel
import numpy as np
import time
random.seed()
import openpyxl
import csv
import matplotlib.pyplot as plt
import math


#生成全0列表
def all(a, n):
    return [a for i in range(n)]


#将列表中a，b索引之间的所有元素倒序
def reverselist(l, a, b):
    if a > b:
        tmp = a
        a = b
        b = tmp
    u = l[a:b+1:1]
    for i in range(len(u)):
        l[b - i] = u[i]
    return l


class SA3(SAmodel):
    def __init__(self, data, n=5, T0=2, ap=1000, minT=0.01, alpha=0.995, N=1500, epoch=20, maxtest=1500):
        super(SA3, self).__init__(T0, minT, alpha, N, epoch, maxtest)
        self.row = n - 1 + len(data)
        self.data = data
        self.n = n
        self.xes = self.generate_xes()
        self.ap = ap

    def generate_xes(self, b=100):
        a = [i for i in range(self.row)]
        for i in range(self.row):
            if a[i] >= len(self.data):
                a[i] = -1
        x = [a.copy() for i in range(b * self.epoch)]
        e = []
        for i in range(b * self.epoch):
            random.shuffle(x[i])
            e.append(self.f(x[i]))
        ids = sorted(range(len(e)), key=lambda k: e[k])
        xx = [x[ids[i]] for i in range(self.epoch)]
        return xx

    def f(self, x):
        t, s = all(0, self.n), all(1, self.n)
        k, p= 0, 0
        while True:
            if x[k] == -1:
                p = p + 1
            else:
                maxp = self.data[x[k]][0]
                minp = self.data[x[k]][1]
                s1 = abs(s[p]-maxp)
                s2 = abs(s[p]-minp)
                t[p] += min(s1, s2) + abs(maxp-minp)
                if s1 >= s2:
                    s[p] = maxp
                else:
                    s[p] = minp
            k = k + 1
            if k >= self.row:
                break
        T = max(t)  #工作结束时间
        E = np.var(t) #员工工作时间方差
        return [T, E]

    def bestcondition(self):
        return self.E[0] < self.bestE[0] or \
               (self.E[0] == self.bestE[0] and self.E[1] < self.bestE[1])

    def Select(self):
        a = random.randint(0, self.row - 1)
        while True:
            b = random.randint(0, self.row - 1)
            if not (b == a):
                break
        self.newx = self.x.copy()
        self.newx = reverselist(self.newx, a, b)
        self.newE = self.f(self.newx)

    def ptrans(self, T):
        if self.newE[0] < self.E[1]:
            return 1.0
        elif self.newE[0] == self.E[0]:
            if self.newE[1] < self.E[1]:
                return 1.0
            else:
                return math.exp((self.E[1] - self.newE[1])/(T*self.ap))
        else:
            return math.exp((self.E[0] - self.newE[0])/T)

    # 从初始解集合中按顺序选取下一个初始解
    def init_x(self):
        self.pepoch += 1
        return self.xes[self.pepoch - 1]

    def find(self):
        records = []
        for i in range(self.epoch):
            print("epoch " + str(i+1) + " starts")
            time1 = time.perf_counter()
            records.append(self.single_epoch())
            time2 = time.perf_counter()
            print("epoch " + str(i+1) + " finishes with " + str(time2-time1) + "s")
            print("E is " + str(self.E))
        return self.bestx, self.bestE, records

if __name__ == '__main__':
    NN = 96
    records = []
    f = open("result3.csv", 'w', encoding='utf-8', newline='')
    writer = csv.writer(f)
    writer.writerow(['OrderNo', 'GroupNo', 'WorkerNo', 'TaskNo'])
    for ii in range(NN):
        order_sheet = pd.read_excel('Q2input.xlsx', 'orders'+str(ii+1), header=None).values.tolist()
        ordername_sheet = pd.read_excel('processed_data.xlsx', 'orders', header=None).values.tolist()
        data = pd.read_excel('Q3input.xlsx', str(ii+1), header=None).values.tolist()
        model = SA3(data=data, n=5, T0=800, minT=0.02, epoch=15, N=8000, ap=1000, alpha=0.999)
        x, bestE, record = model.find()
        # 写入数据
        tskn, p = 0, 0
        for k in range(len(x)):
            GroupNo = str(ii+1)
            r = x[k]
            if r == -1:
                p = p + 1
                tskn = 0
            else:
                tskn += 1
                OrderNo = ordername_sheet[order_sheet[0][r]][0]
                WorkerNo = str(p+1)
                TaskNo = str(tskn)
                writer.writerow([OrderNo, GroupNo, WorkerNo, TaskNo])
            rcd = record[model.bestid]
            rcd1, rcd2 = [], []
            for i in range(len(rcd)):
                rcd1.append(rcd[i][0])
                rcd2.append(rcd[i][1])
            records.append([rcd1, rcd2])
        print("end" + str(ii))
    plt.subplot(2, 1, 1)
    plt.title('工作完成时间随迭代次数的变化')
    plt.plot(records[0][0])
    plt.xlabel('轮次')
    plt.ylabel('工作完成时间')
    plt.subplot(2, 1, 2)
    plt.title('员工工作时间方差随迭代次数的变化')
    plt.plot(records[0][1])
    plt.xlabel('轮次')
    plt.ylabel('员工工作时间方差')
    plt.savefig("Q3.jpg")
    plt.show()
    f.close()




