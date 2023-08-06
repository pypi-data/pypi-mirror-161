import mylib_donghao.mySort as mySort
from mylib_donghao.basic_function import *


class myQueue:
    def __init__(self, l=None):
        self.queue = list()
        if istype(l, []):
            for i in l:
                self.queue.append(i)

    #快速排序
    def sort(self):
        I = list(range(len(self.queue)))
        self.queue, I = mySort.quickSort(self.queue, I)
        return I

    def enqueue(self, a, i=None):
        if not istype(i, 1):
            self.queue.append(a)
        elif i < 0:
            self.queue.insert(0, a)
        elif i >= len(self.queue):
            self.queue.append(a)
        else:
            self.queue.insert(i, a)
        return True

    def dequeue(self, i=None):
        if not istype(i, 1):
            u = self.queue.pop()
            return u
        elif i >= len(self.queue):
            u = self.queue.pop()
            return u
        elif i < 0:
            u = self.queue.pop(0)
            return u
        else:
            u = self.queue.pop(i)
            return u

    def issame(self, a, i):
        if not istype(i, 1):
            print("myQueue issame 错误的索引类型")
            exit(1)
        if i >= len(self.queue) or i < 0:
            print("myQueue issame 索引越界")
            exit(1)
        return a == self.queue[i]




