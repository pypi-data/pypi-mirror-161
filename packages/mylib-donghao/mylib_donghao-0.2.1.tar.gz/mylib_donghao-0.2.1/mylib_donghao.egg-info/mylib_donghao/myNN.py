import numpy as np
from mylib_donghao.basic_function import *
import torch
import torch.nn as nn
import os
from torch.autograd import Variable
import torch.utils.data as Data

#规范
#全连接层 Linear：[  "Linear" , [输入数，输出数，是否采用dropout] ]
#激活函数：softmax, sigmoid, relu, tanh, elu, prelu
#nn.BatchNorm2d ------- "batchnorm2d": [  ["batchnorm2d"], [第1维尺寸，分母偏置值，动量，是否需要引入学习参数（使用默认填入None）] ]
#CNN ： [ "CNN" , [输入通道数，输出通道数，核边长，步长，边缘补充长度]]
#CNN的输入：[batch][通道数][尺寸1][尺寸2]


def AddALinearPlease(with_input, and_output, if_dropout=False, nnlist=None):
    newnn = ["Linear", [with_input, and_output, if_dropout]]
    if istype(nnlist, []):
        nnlist.append(newnn)
        return nnlist
    else:
        return newnn


def AddACNNPlease(input_channels, output_channels, kernal_size, stride, padding_size, nnlist=None):
    newnn = [["CNN"], [input_channels, output_channels, kernal_size, stride, padding_size]]
    if istype(nnlist, []):
        nnlist.append(newnn)
        return nnlist
    else:
        return newnn


class myNN(nn.Module):
    def __init__(self, nnlist):
        super(myNN, self).__init__()
        self.layer = list()
        self.network_list = nnlist.copy()
        self.depth = len(nnlist)
        self.forward_type = list()
        for i in range(len(nnlist)):
            n = nnlist[i]
            if n[0] == "Linear":
                p = n[1].copy()
                b = p[2]
                layer = nn.Linear(p[0], p[1], b)
                self.layer.append(layer)
                self.forward_type.append(0)
            if n[0] == "RNN": #10, 11
                p = n[1].copy()
                input_size = p[0]
                hidden_size = p[1]
                num_layers = p[2]
                nonlinearity = p[3]
                if nonlinearity == None:
                    nonlinearity = "tanh"
                bias = p[4]
                if bias == None:
                    bias = True
                batch_first = p[5]
                if batch_first == None:
                    batch_first = False
                dropout = p[6]
                if dropout == None:
                    dropout = 0
                bid = p[7]
                if bid == None:
                    bid = False
                layer = nn.RNN(
                    input_size=input_size,
                    hidden_size=hidden_size,
                    num_layers=num_layers,
                    bias=bias,
                    nonlinearity=nonlinearity,
                    batch_first=batch_first,
                    dropout=dropout,
                    bid=bid
                )
                self.layer.append(layer)
                if batch_first:
                    self.forward_type.append(10)
                else:
                    self.forward_type.append(11)

            if n[0] == "CNN": #2
                #输入：[batch][通道数][尺寸1][尺寸2]
                p = n[1].copy()
                layer = nn.Conv2d(in_channels=p[0],
                                  out_channels=p[1],
                                  kernel_size=p[2],
                                  stride=p[3],
                                  padding=p[4])
                self.layer.append(layer)
                self.forward_type.append(2)
            if n[0] == "batchnorm2d":
                p = n[1].copy()
                num = p[0]
                eps = p[1]
                momentum = p[2]
                affine = p[3]
                if eps == None:
                    eps = 1e-05
                if momentum == None:
                    momentum = 0.1
                if affine == None:
                    affine = True
                layer = nn.BatchNorm2d(num, eps, momentum, affine)
                self.layer.append(layer)
                self.forward_type.append(-1)
            if n[0] == "relu":
                self.layer.append(nn.ReLU())
                self.forward_type.append(-1)
            if n[0] == "sigmoid":
                self.layer.append(nn.Sigmoid())
                self.forward_type.append(-1)
            if n[0] == "softmax":
                if len(n) == 1:
                    d = -1
                else:
                    d = n[1]
                self.layer.append(nn.Softmax(dim=d))
                self.forward_type.append(-1)
            if n[0] == "elu":
                self.layer.append(nn.ELU())
                self.forward_type.append(-1)
            if n[0] == "prelu":
                if len(n) == 1 or n[1][0] == None:
                    nump = 1
                else:
                    nump = n[1][0]
                if len(n) == 1 or n[1][1] == None:
                    initialize = 0.25
                else:
                    initialize = n[1][1]
                self.layer.append(nn.PReLU(num_parameters=nump, init=initialize))
                self.forward_type.append(-1)
            if n[0] == "maxpool2d":
                self.forward_type.append(3)
                self.layer.append(nn.MaxPool2d(kernel_size=n[1]))
        self.layer_module = nn.ModuleList(self.layer)

    def forward(self, x, H=None):
        i = 0
        numh = 0
        for layer in self.layer_module:
            if self.forward_type[i] == 0 \
                or self.forward_type[i] == -1\
                    or self.forward_type[i] == 2\
                        or self.forward_type[i] == 3:
                x = layer(x)
            #RNN有隐层输入，与CNN的输入格式不同
            if self.forward_type[i] == 10 or self.forward_type[i] == 11:
                if self.forward_type[i] == 10:
                    #batch first, [batch][time][dim]
                    if H == None or len(H) <= numh or H[numh] == None:
                        out = layer(x)[0]
                    else:
                        out = layer(x, H[numh])[0]
                    out = out.transpose(0, 1)
                    x = out[-1]  # 只有最后一次输出的才是真正的预测结果所需要的隐藏层数值
                if self.forward_type[i] == 11:
                    #不是batch first, [time][batch][dim]
                    x = x.transpose(0, 1)
                    if H == None or len(H) <= numh or H[numh] == None:
                        out = layer(x)[0]
                    else:
                        out = layer(x, H[numh])[0]
                    x = out[-1]  # 只有最后一次输出的才是真正的预测结果所需要的隐藏层数值
                numh += 1

            i += 1
        return x

#需要自己写的新函数：
#data_loader的生成，以及成员保存
#训练的过程，如何存取数据，如何测试
#对接到具体场景的方法
class myNetwork:
    def __init__(self, nnlist, bs=1, lr=0.01):
        self.model = myNN(nnlist)
        self.criterion = nn.MSELoss(reduction='mean')
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr)
        self.training_loss_list = []
        self.testing_loss_list = []
        self.testing_accuracy_list = []
        self.batch_size = bs

    def set_optimizer(self, t, lr):
        if t == "Adam":
            self.optimizer = torch.optim.Adam(self.model.parameters(), lr)

    def set_model(self, nnlist, lr=0.01):
        self.model = myNN(nnlist)
        self.criterion = nn.MSELoss(reduction='mean')
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr)

    def set_criterion(self, r):
        self.criterion = r

    def forward(self, x):
        return self.model.forward(x)

    def forward_input_list_or_numpy(self, ux, dtype=torch.float32):
        x = self.expected_input(ux, dtype)
        y = self.forward(x)
        return y

    def forward_myMatrix(self, ux, dtype=torch.float32):
        return self.forward_input_list_or_numpy(ux.mat, dtype)

    def loss(self, pred_y, y):
        return self.criterion(pred_y, y)

    def load_data_loader(self, path):
        return pkl_load(path)

    def generate_data_loader(self, X, Y, batch_size=None, flg=True):
        if batch_size is None:
            batch_size = self.batch_size
        if (not istype(batch_size, 0)) or (batch_size <= 0):
            batch_size = 1
        #flg:是否随机打乱
        dataset = Data.TensorDataset(X, Y)
        loader = Data.DataLoader(dataset, batch_size, flg)
        return loader

    def generate_data_loader_list_or_numpy(self, input_x, output_y, batch_size=None, flg=True):
        X = torch.Tensor(input_x)
        Y = torch.Tensor(output_y)
        return self.generate_data_loader(X, Y, batch_size, flg)

    def generate_data_loader_myMatrix(self, X, Y, batch_size=None, flg=True):
        return self.generate_data_loader_list_or_numpy(X.mat, Y.mat, batch_size, flg)

    def expected_input(self, x, dtype=torch.float32):
        if dtype == "Long":
            return torch.LongTensor(x)
        else:
            return Variable(torch.tensor(x, dtype=dtype))

    def training_of_single_batch(self, x, y):
        pred_y = self.forward(x)
        loss = self.loss(pred_y, y)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return loss


def AddASoftmaxPlease(nnlist=None):
    if istype(nnlist, []):
        nnlist.append(["softmax"])
        return nnlist
    else:
        return ["softmax"]


def AddASigmoidPlease(nnlist=None):
    if istype(nnlist, []):
        nnlist.append(["sigmoid"])
        return nnlist
    else:
        return ["sigmoid"]


def AddAReluPlease(nnlist=None):
    if istype(nnlist, []):
        nnlist.append(["relu"])
        return nnlist
    else:
        return ["relu"]


def AddAMaxPoolPlease(kernel_size=2, nnlist=None):
    s = ["maxpool2d", kernel_size]
    if istype(nnlist, []):
        nnlist.append(s)
        return nnlist
    else:
        return s



