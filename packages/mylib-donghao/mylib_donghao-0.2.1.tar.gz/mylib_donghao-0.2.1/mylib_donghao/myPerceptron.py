from mylib_donghao.myMatrix import *

class myPerceptron:
    def __init__(self, input_size, output_size=1, ifrandom=False):
        self.W = myMatrix(input_size, output_size)
        self.b = myMatrix(output_size, 1)
        self.input_size = input_size
        self.output_size = output_size
        if ifrandom:
            self.W.random(-1.0, 1.0)
            self.b.random(-1.0, 1.0)
        self.cnt = 0

    def random(self, a=-1.0, b=1.0):
        self.W.random(a, b)
        self.b.random(a, b)

    def forward(self, x):
        return self.W.transpose() * x + self.b

    def forward_numpy_or_list(self, x):
        return self.forward(myMatrix(x))

    def forward_by_class(self, x, ifintrain=False):
        Y = self.forward(x)
        for i in range(Y.x()):
            for j in range(Y.y()):
                u = Y.read(i, j)
                if u > 0:
                    Y.set(i, j, 1)
                elif u<0:
                    Y.set(i, j, -1)
                else:
                    if ifintrain:
                        Y.set(i, j, 0)
                    else:
                        Y.set(i, j, 1)
        return Y

    def forward_by_class_numpy_or_list(self, x, ifintrain=False):
        return self.forward_by_class(myMatrix(x), ifintrain)

    def single_batch_train(self, x, y, yita=0.01):
        yp = self.forward_by_class(x, True)
        if yp.equal(y):
            self.cnt += 1
            return 0
        else:
            self.cnt = 0
            '''这里需要优化函数'''
            '''w <- w + yita * y * x'''
            for i in range(self.input_size):
                for j in range(self.output_size):
                    if y.read(j, 0) == yp.read(j, 0):
                        continue
                    xdata = x.read(i, 0)
                    ydata = y.read(j, 0)
                    w0 = self.W.read(i, j)
                    w0 += yita * xdata * ydata
                    self.W.set(i, j, w0)
            '''b <- b + yita * y'''
            for j in range(self.output_size):
                if y.read(j, 0) == yp.read(j, 0):
                    continue
                b0 = self.b.read(j, 0)
                ydata = y.read(j, 0)
                b0 += ydata * yita
                self.b.set(j, 0, b0)
            return 1

    def train(self, loader, yita=0.01, N=-1):
        n = 0
        loader.new_pointer()
        while (N == -1 or n < N) and self.cnt < loader.size:
            '''终止条件：
               数据集已经无法优化
               或者
               达到最大迭代次数（可选）
             '''
            x, y = loader.pop()
            n += self.single_batch_train(x, y, yita)

