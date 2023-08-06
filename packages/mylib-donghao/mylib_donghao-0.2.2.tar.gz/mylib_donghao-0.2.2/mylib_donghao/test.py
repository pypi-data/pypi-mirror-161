import mylib_donghao.myNN as NN
import torch
from torch.autograd import Variable
import numpy as np
import mylib_donghao.myDimReduce
import mylib_donghao.myRBM as myRBM
from mylib_donghao.myMatrix import myMatrix
from mylib_donghao.myMatrix import myMatrixLoader
import basic_function as bf
from myPerceptron import *
from myLinearProgramming import minLinearProgramming_with_scipy

model = NN.myNetwork([ ["Linear", [2, 3, False]] , ["softmax"], ["Linear", [3, 3, False]] , ["softmax"] ])
l = [[2, 3], [3, 2], [2, 1]]
y = [[1, 0, 0], [1, 0, 0], [0, 0, 1]]
for i in range(500):
    model.training_of_single_batch(model.expected_input(l), model.expected_input(y))
print(model.forward_input_list_or_numpy(l))

layer1 = ["CNN", [1, 2, 3, 2, 0]]
layer2 = ["CNN", [2, 4, 5, 3, 2]]
layer3 = ["batchnorm2d", [4, None, None, None]]
layer4 = NN.AddAMaxPoolPlease(2)
model2 = NN.myNetwork([layer1, layer2, layer3, layer4])
r = torch.rand([2, 1, 16, 16])
print(model2.forward(r))

mm = myRBM.RBM(5, 3)
mm.a.print()
mm.b.print()
for i in range(100):
    mm.train(myMatrix([[0, 1, 0, 1, 1]]).transpose(), 0.01)
    mm.train(myMatrix([[0, 1, 1, 1, 1]]).transpose(), 0.01)
#    mm.train(myMatrix([[1, 1, 0, 1, 1]]).transpose(), 0.01)
#    mm.train(myMatrix([[0, 0, 0, 0, 1]]).transpose(), 0.01)
#    mm.train(myMatrix([[1, 1, 1, 1, 1]]).transpose(), 0.01)
mm.a.print()
mm.b.print()
mm.visibled(mm.hiddened(myMatrix([[0], [1], [0], [1], [1]]))).print()

print("-------------------------------")
a = myPerceptron(2, 1)
loader = myMatrixLoader()
loader.append(myMatrix([[2, 3], [-2, 3]]).transpose(), myMatrix([[1, 1]]))
loader.append(myMatrix([[-2, -3], [2, -3]]).transpose(), myMatrix([[-1, -1]]))
a.forward(loader.matlist[0]).print()
a.forward(loader.matlist[1]).print()
a.forward(loader.matlist[2]).print()
a.forward(loader.matlist[3]).print()
a.train(loader, 0.01, 10000)
a.forward(loader.matlist[0]).print()
a.forward(loader.matlist[1]).print()
a.forward(loader.matlist[2]).print()
a.forward(loader.matlist[3]).print()

Aeq = [[2, 3], [4, 5]]
beq = [[2], [3]]
A = [[55, 1], [56, 36]]
b = [[8], [35]]
Aeq = myMatrix(Aeq)
beq = myMatrix(beq)
A = myMatrix(A)
b = myMatrix(b)
c = myMatrix([1, 4])
fun, x, res = minLinearProgramming_with_scipy(c,A,b,Aeq,beq)
print(fun, x, res)
x.print()



A = myMatrix(37,2)
for i in range(37):
    A.set(i, 0, 1985.0 + 1.0 * i)
    A.set(i, 1, 1.0)
x = [508.14600000000, 509.424000000000,518.762000000000,533.865000000000,543.806000000000,546.820000000000,535.830000000000,533.660000000000,522.490000000000,525.210000000000,532.810000000000,550.690000000000,548.010000000000,552.380000000000,552.540000000000,572.300000000000,581.890000000000,581.960000000000,602.540000000000,610.280000000000,613.410000000000,629.810000000000,632.310000000000,633.200000000000,588.940000000000,624.640000000000,605.170000000000,620.390000000000,631.150000000000,619.950000000000,640.570000000000,642.970000000000,646.010000000000,635.150000000000,601.630000000000,572.530000000000,581.400000000000]
x = myMatrix(x)
u = A.ATA().inv() * A.transpose() * x
(A * u).print()







