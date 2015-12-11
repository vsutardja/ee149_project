from __future__ import division
import matplotlib.pyplot as plt
import numpy as np
from poly import *
from random import random
import socket
from time import sleep
from math import floor
from select import select

time_interval = 1.5
scale = 8.25
o_timeout = 0.001
x_scale = 200.0
y_scale = 280.0

def high_pass(sig, mult=0.1):
    new_sig = [(1 + mult)*sig[0]]
    for i in range(1, len(sig)):
        new_sig.append(sig[i] + mult*(sig[i] - sig[i-1]))
    assert len(new_sig) == len(sig)
    return new_sig

def to_polar(x, y):
    r = np.sqrt(x**2 + y**2)
    theta = np.arctan(float(y)/x)
    return r, theta

def to_rect(r, theta):
    x = r*np.cos(theta)
    y = r*np.sin(theta)
    return x, y

def rotate(x, y, offset):
    if x == 0 and y == 0:
        return 0, 0
    r, theta = to_polar(x, y)
    theta -= offset
    x, y = to_rect(r, theta)
    return x, y

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
    speeds = []
    # x_diff = np.gradient(x_vals)
    x_diff = np.ediff1d(x_vals)
    # y_diff = np.gradient(y_vals)
    y_diff = np.ediff1d(y_vals)
    dy = y_diff / x_diff
    # dy_diff = np.gradient(dy)
    dy_diff = np.ediff1d(dy, to_begin=dy[1]-dy[0])
    d2y = dy_diff / x_diff
    R = np.power(1 + np.square(dy), 1.5) / d2y
    R[np.abs(R) > 32000] = 0
    print R
    for i in range(1,len(R)):
        if x_vals[i] - x_vals[i-1] < 0:
            if i == 1:
                R[i-1] = -R[i-1]
            R[i] = -R[i]
    for i in range(0, len(R)-1):
        dist = np.sqrt((x_vals[i+1] - x_vals[i])**2 + (y_vals[i+1] - y_vals[i])**2)
        theta = np.arccos(1 - dist**2 / (2*R[i]**2))
        if np.isnan(theta) or theta == 0:
            speeds.append(dist/time_interval)
        else:
            speeds.append(R[i]*theta / time_interval)
    R = R[:-1]
    return R, speeds

def wheel_speed(r, v=1, b=230):
    spd = np.copy(r)
    for i in range(len(spd)):
        if spd[i] > 0:
            spd[i] = v * (spd[i] + b / 2) / spd[i]
        elif spd[i] < 0:
            spd[i] = v * (spd[i] - b / 2) / spd[i]
    return spd

def all_wheel_speeds(r, speeds, b=230):
    new_speeds = []
    for radius, speed in zip(r, speeds):
        if radius > 0:
            new_speeds.append(speed * (radius + b / 2) / radius)
        elif radius < 0:
            new_speeds.append(speed * (radius - b / 2) / radius)
        else:
            new_speeds.append(speed)
    return new_speeds

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
    #data_points = [(50, 100), (100, 100), (200, 100), (200, 200), (100, 200), (50, 200), (100, 250), (100, 300)]
    with open('data_file') as data_file:
        x = eval(data_file.readline())
        y = eval(data_file.readline())
    x = map((lambda i: i-x[0]), x)
    y = map((lambda i: i-y[0]), y)
    x_ratio = max(abs(max(x)) / x_scale, abs(min(x)) / x_scale)
    y_ratio = (max(y) - min(y)) / y_scale
    ratio = max(x_ratio, y_ratio)
    x = map((lambda i: i/ratio), x)
    y = map((lambda i: i/ratio), y)
    print 'x:', x
    print 'y:', y
    #x = map((lambda i: 3*i), x)
    #y = map((lambda i: 3*i), y)
    # data_points = [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (4, 5), (3, 5), (2, 5), (1, 5), (1, 4), (1, 3), (1, 2)]
    # data_points = random_points(7)
    #print 'data points:', data_points
    n = len(x)
    #print x
    #x = [i for i,j in data_points]
    #y = [j for i,j in data_points]
    cont = control_points(zip(x, y))
    print 'control_points:', cont
    cont_x = [i for i,j in cont]
    cont_y = [j for i,j in cont]
    plt.hold(True)
    plt.scatter(x, y)
    plt.scatter(cont_x, cont_y, color='red')
    px, py = interpolate(cont)
    t = np.linspace(0, n-1, 10*n)
    x_vals = [px(i) for i in t]
    y_vals = [py(i) for i in t]
    dy = y[1] - y[0]
    dx = x[1] - x[0]
    if dx == 0:
        offset = 0
    else:
        offset = np.arctan(float(dy)/dx)
    rot = map((lambda pos: rotate(pos[0], pos[1], offset)), zip(x_vals, y_vals))
    #rot = map((lambda p: p[0] * scale, p[1] * scale), rot)
    for i in range(len(rot)):
        rot[i] = (rot[i][0] * scale, rot[i][1]*scale)
    #print rot
    #print [x for x, y in rot]
    #plt.plot([x for x, y in rot], [y for x, y in rot])
    plt.plot(x_vals, y_vals)
    plt.show()

    r, speeds = roc(x_vals, y_vals)
    #v = wheel_speed(r)


    for i in range(len(r)):
        r[i] *= 10
        r[i] = int(floor(r[i]))
        if abs(r[i]) > 32000:
            r[i] = 0
        speeds[i] *= 10
        speeds[i] = abs(floor(speeds[i]))
    #speeds = all_wheel_speeds(r, speeds)
    speeds = map(int, speeds)
    speeds = map((lambda x: x if x < 200 else 200), speeds)
    r = high_pass(r)
    speeds = high_pass(speeds)

    print 'speeds:', speeds
    print 'r:', r

    K_HOST = '192.168.2.9'
    K_PORT = 1234
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print 'connecting to Kobuki'
    s.connect((K_HOST, K_PORT))
    print 'connected to Kobuki'
    s.send('0 0')

    O_HOST = '10.142.33.186'
    O_PORT = 27015
    o_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print 'connecting to OptiTrack'
    o_sock.connect((O_HOST, O_PORT))
    o_sock.setblocking(0)
    print 'connected to OptiTrack'
    #with open('pos_data') as f:
    print 'waiting 7 seconds'
    sleep(7)
    #sleep(1)
    try:
        for i, (radius, speed) in enumerate(zip(r, speeds)):
            sleep(time_interval)
            status = select([o_sock], [], [], o_timeout)[0]
            if len(status) > 0:
                pos_data = o_sock.recv(4096)
                pos_data = pos_data[-100:]
                curr_data = pos_data.split('f ')[-1]
                vals = curr_data.split(',')
                try:
                    x, y = 1000*float(vals[1]), -1000*float(vals[3])
                    print 'vals:', vals
                    print 'perceived position:', rot[i]
                    print 'actual position:', (x, y)
                except Exception as e:
                    print e
            print 'sending', int(radius), int(speed)
            if i % 10 == 0:
                print 'At data point', int(i/10), 'of', n
            s.send('%d %d' % (radius, speed))
    except KeyboardInterrupt:
        print 'closing'
        s.shutdown(2)
        s.close()
        print 'closed'
