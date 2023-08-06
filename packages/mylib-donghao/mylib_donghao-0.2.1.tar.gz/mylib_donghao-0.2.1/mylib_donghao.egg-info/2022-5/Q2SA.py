import openpyxl
from SAmodel import SAmodel
import random
import time
import pandas as pd
import csv
import matplotlib.pyplot as plt


#生成全0列表
def zeros(n):
    return [0 for i in range(n)]


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


class SA2(SAmodel):
    def __init__(self, data, T0=100, minT=0.5, alpha=0.995, N=1000, epoch=30, maxtest=1500):
        super(SA2, self).__init__(T0, minT, alpha, N, epoch, maxtest)
        self.row = len(data)
        self.col = len(data[0])
        self.data = self.process(data)
        self.xes = self.generate_xes()


    def generate_xes(self, b=500):
        a = [i for i in range(self.col)]
        x = [a.copy() for i in range(b * self.epoch)]
        e = []
        for i in range(b * self.epoch):
            random.shuffle(x[i])
            e.append(self.f(x[i]))
        ids = sorted(range(len(e)), key=lambda k: e[k])
        xx = [x[ids[i]] for i in range(self.epoch)]
        return xx

    def process(self, data):
        u = []
        for i in range(self.row):
            r = []
            for j in range(self.col):
                if data[i][j] == 1:
                    r.append(j)
            u.append(r)
        return u

    #找到订单o对应的最大货架、最小货架（在x排列方式下）
    def find_maxmin(self, o, x):
        maxp, minp = 0, self.col
        for j in o:
            if x[j] > maxp:
                maxp = x[j]
            if x[j] < minp:
                minp = x[j]
        return maxp, minp

    def f(self, x):
        u = 0.0
        for o in self.data:
            maxp, minp = self.find_maxmin(o, x)
            u += maxp - minp
        return u

    def init_x(self):
        self.pepoch += 1
        return self.xes[self.pepoch-1]

    def Select(self):
        a = random.randint(0, self.col - 1)
        while True:
            b = random.randint(0, self.col - 1)
            if not (b == a):
                break
        self.newx = self.x.copy()
        self.newx = reverselist(self.newx, a, b)
        self.newE = self.f(self.newx)

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
    wb = openpyxl.Workbook()
    f = open("result2.csv", 'w', encoding='utf-8', newline='')
    writer = csv.writer(f)
    writer.writerow(['ItemNo', 'GroupNo', 'ShelfNo'])
    for ii in range(NN):
#        order_sheet = pd.read_excel('Q2input.xlsx', 'orders'+str(ii+1), header=None).values.tolist()
        om_sheet = pd.read_excel('Q2input.xlsx', str(ii+1), header=None).values.tolist()
        materialname_sheet = pd.read_excel('processed_data.xlsx', 'materials', header=None).values.tolist()
        ordername_sheet = pd.read_excel('processed_data.xlsx', 'orders', header=None).values.tolist()
        omlist = []
        for j in range(len(om_sheet[0])):
            for i in range(len(om_sheet)):
                if om_sheet[i][j] == 1:
                    omlist.append(j)
                    break
        xl, yl = len(om_sheet), len(omlist)
        data = [zeros(yl) for i in range(xl)]
        for i in range(xl):
            for j in range(yl):
                yid = omlist[j]
                if om_sheet[i][yid] == 1:
                    data[i][j] = 1
        model = SA2(data)
        x, E, record = model.find()
        records.append(record[model.bestid])
        picihao = str(ii+1)
        #写入数据
        for i in range(len(x)):
            yid = omlist[i]
            shelfid = str(x[i] + 1)
            yname = materialname_sheet[yid][0]
            writer.writerow([yname, picihao, shelfid])
        wb.create_sheet(picihao)
        sheet = wb[picihao]
        for i in range(xl):
            maxp, minp = model.find_maxmin(model.data[i], x)
            sheet.append([maxp+1, minp+1])
        print("end" + str(ii))
    wb.save('Q3input.xlsx')
    f.close()
    plt.plot(records[0])
    plt.savefig("Q2.jpg")
    plt.show()










