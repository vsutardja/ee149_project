from __future__ import division
import matplotlib.pyplot as plt
import numpy as np

K = 3
n = 4
def memo(f):
    cache = {}
    def memoized(*args):
        if args not in cache:
            cache[args] = f(*args)
        return cache[args]
    return memoized

def t(i):
    if i < K:
        return 0
    elif i > n:
        return n-K+2
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
            if i + j <= n+1:
                print i, j, N(i+j, K, i)
                A[i,i+j] = N(i+j, K, i)
    print A

if __name__ == '__main__':
    #control_points([(1, 2), (2, 3), (3, 4), (2, 5)])
    Nfunc = lambda u : N(3, 3, u)
    x = [i*.1 for i in range(40)]
    y = [Nfunc(j) for j in x]
    plt.plot(x, y)
    plt.show()

