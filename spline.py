from __future__ import division
import matplotlib.pyplot as plt
import numpy as np
from poly import *


def memo(f):
    cache = {}
    def memoized(*args):
        if args not in cache:
            cache[args] = f(*args)
        return cache[args]
    return memoized

@memo
def N(i, k):
    if k == 1:
        p = PiecewisePolynomial()
        p.setp(Polynomial([1]), t(i), t(i+1))
        return p
    if t(i+k-1) - t(i) > 0:
        p1 = PiecewisePolynomial(Polynomial([-t(i), 1]) / (t(i+k-1)-t(i))) * N(i, k-1)
        #print i, k, 'setting p1', p1
    else:
        p1 = PiecewisePolynomial()
        #print i, k, 'p1 is 0'
    if t(i+k) - t(i+1) > 0:
        p2 = PiecewisePolynomial(Polynomial([t(i+k), -1]) / (t(i+k)-t(i+1))) * N(i+1, k-1)
        #print i, k, 'setting p2', p2
    else:
        #print i, k, 'p2 is 0'
        p2 = PiecewisePolynomial()
    return p1 + p2

def control_points(data_points):
    n = len(data_points)
    x = [i for i,j in data_points]
    y = [j for i,j in data_points]
    control_points = []
    control_points.append(data_points[0])
    A = np.zeros((n, n))
    A[0,0] = 1.5
    A[0,1] = -0.5
    A[1,0] = 1/4
    A[1,1] = 7/12
    A[1,2] = 1/6
    A[n-2,n-1] = 1/4
    A[n-2,n-2] = 7/12
    A[n-2,n-3] = 1/6
    A[n-1,n-2] = -0.5
    A[n-1,n-1] = 1.5
    for i in range(2, n-2):
        A[i, i-1] = 1/6
        A[i, i] = 2/3
        A[i, i+1] = 1/6
    #print A
    cont_x = np.linalg.solve(A, x)
    cont_y = np.linalg.solve(A, y)
    control_points += zip(cont_x, cont_y)
    control_points.append(data_points[-1])
    return control_points

def interpolate(cont):
    px = PiecewisePolynomial()
    py = PiecewisePolynomial()
    n = len(cont)
    x = [i for i,j in cont]
    y = [j for i,j in cont]
    for i in range(n):
        px += N(i,K) * x[i]
        py += N(i,K) * y[i]
    #print px
    px.setp(Polynomial([x[-1]]), n-3, n-2)
    #print
    #print px
    py.setp(Polynomial([y[-1]]), n-3, n-2)
    return px, py

# n + K - 2 nonzero functions, from i = 0 to N + K - 3
if __name__ == '__main__':
    K = 4
    def t(i):
        if i < K:
            return 0
        elif i >= n+K-1:
            return n-1
        else:
            return i-K+1

    data_points = [(1, 2), (2, 2), (4, 2), (4, 4), (2, 4), (1, 4), (2, 5), (2, 6)]
    print 'data points:', data_points
    n = len(data_points)
    x = [i for i,j in data_points]
    y = [j for i,j in data_points]
    cont = control_points(data_points)
    print 'control_points:', cont
    cont_x = [i for i,j in cont]
    cont_y = [j for i,j in cont]
    plt.scatter(x, y)
    plt.hold(True)
    plt.scatter(cont_x, cont_y, color='red')
    px, py = interpolate(cont)
    t = np.linspace(0, len(data_points)-1, 100)
    x_vals = [px(i) for i in t]
    y_vals = [py(i) for i in t]
    plt.plot(x_vals, y_vals)
    plt.show()
    #print [t(i) for i in range(n+2*K-2)]
    #p2 = N(2, K)
    #print p2(2)
    #print N(3, K)(2)
    #print N(4, K)(2)
    #p.plot(0, 6)
    #t0 = [0.01*i for i in range(100)]
    #t1 = [1+0.01*i for i in range(100)]
    #x0 = [2*b1(i) + 4*b21(i) + 4*b31(i) for i in t0]
    #y0 = [0*b1(i) + 3*b21(i) + 1*b31(i) for i in t0]
    #plt.plot(x0,y0)
    #plt.hold(True)
    #x1 = [4*b22(i) + 4*b32(i) + 8*b41(i) for i in t1]
    #y1 = [3*b22(i) + 1*b32(i) - 1*b41(i) for i in t1]
    #plt.plot(x1,y1)
    #plt.show()
