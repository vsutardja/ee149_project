from __future__ import division
import matplotlib.pyplot as plt
import numpy as np
from poly import *
from random import random


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
    else:
        p1 = PiecewisePolynomial()
    if t(i+k) - t(i+1) > 0:
        p2 = PiecewisePolynomial(Polynomial([t(i+k), -1]) / (t(i+k)-t(i+1))) * N(i+1, k-1)
    else:
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
    px.setp(Polynomial([x[-1]]), n-3, n-2)
    py.setp(Polynomial([y[-1]]), n-3, n-2)
    return px, py

def random_points(n, x=8, y=8):
    return [(random()*x, random()*y) for _ in range(n)]

def roc(x_vals, y_vals):
    # x_diff = np.gradient(x_vals)
    x_diff = np.ediff1d(x_vals)
    # y_diff = np.gradient(y_vals)
    y_diff = np.ediff1d(y_vals)
    dy = y_diff / x_diff
    # dy_diff = np.gradient(dy)
    dy_diff = np.ediff1d(dy, to_begin=dy[1]-dy[0])
    d2y = dy_diff / x_diff
    R = np.power(1 + np.square(dy), 1.5) / d2y
    for i in range(1,len(R)):
        if x_vals[i] - x_vals[i-1] < 0:
            if i == 1:
                R[i-1] = -R[i-1]
            R[i] = -R[i]
    return R

def wheel_speed(r, v=1, b=230):
    spd = np.copy(r)
    for i in range(len(spd)):
        if spd[i] > 0:
            spd[i] = v * (spd[i] + b / 2) / spd[i]
        elif spd[i] < 0:
            spd[i] = v * (spd[i] - b / 2) / spd[i]
    return spd

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

    np.set_printoptions(suppress=True)
    data_points = [(1, 2), (2, 2), (4, 2), (4, 4), (2, 4), (1, 4), (2, 5), (2, 6)]
    # data_points = random_points(7)
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
    t = np.linspace(0, len(data_points)-1, 10*n)
    x_vals = [px(i) for i in t]
    y_vals = [py(i) for i in t]
    plt.plot(x_vals, y_vals)
    #plt.savefig('img/spline%d.png' % n)

    r = roc(x_vals, y_vals)
    v = wheel_speed(r)

    pts = []
    pts2 = []

    for i in range(len(r)):
        if abs(r[i]) > 5:
            pts.append([x_vals[i], y_vals[i]])
            r[i] = 0
            v[i] = 100
        if abs(r[i]) < 0.1:
            pts2.append([x_vals[i], y_vals[i]])
    print r
    print v

    plt.plot(*zip(*pts2), marker='o', color='g', ls='')
    plt.plot(*zip(*pts), marker='o', color='y', ls='')

    plt.show()
