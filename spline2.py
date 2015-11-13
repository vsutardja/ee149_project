from __future__ import division
import matplotlib.pyplot as plt
import numpy as np

K = 3
n = 7
def memo(f):
    cache = {}
    cache[(n+1,K,n)] = 1
    def memoized(*args):
        if args not in cache:
            cache[args] = f(*args)
        return cache[args]
    return memoized

def t(i):
    if i < K:
        return 0
    elif i > n+K-2:
        return n-1
    else:
        return i-K+1

@memo
def N(i, k, u):
    if k == 1:
        if u >= t(i) and (u < t(i+1)):
            return 1
        else:
            return 0
    s = 0
    if t(i+k-1) - t(i) > 0:
        s += (u-t(i)) * N(i, k-1, u) / (t(i+k-1) - t(i))
    if t(i+k) - t(i+1) > 0:
        s += (t(i+k) - u) * N(i+1, k-1, u) / (t(i+k) - t(i+1))
    return s

def control_points(data_points):
    x_pts = np.array([x for (x,y) in data_points])
    y_pts = np.array([y for (x,y) in data_points])
    A = np.zeros((n+1, n+1))
    for i in range(n+1):
        for j in range(K-1):
            if i + j < n+1:
                print i, j, N(i+j, K, i)
                A[i,i+j] = N(i+j, K, i)
    print A

def inrange(x, l, h):
    return x >= l and x < h

def f(x):
    if inrange(x, 0, 1):
        return x**2/2
    elif inrange(x, 1, 2):
        return .5*(-2*x**2 + 6*x - 3)
    elif inrange(x, 2, 3):
        return .5*(3-x)**2
    return 0

if __name__ == '__main__':
    #control_points([(1, 2), (2, 3), (3, 4), (2, 5)])
    for i in range(n+K+1):
        print t(i)
    for m in range(n+K-2):
        print m
        Nfunc = lambda u : N(m, K, u)
        x = [i*.1 for i in range(n*10)]
        y = [Nfunc(j) for j in x]
        #y2 = [f(j) for j in x]
        plt.plot(x, y)
        #plt.hold(True)
        #plt.plot(x, y2)
        plt.show()

