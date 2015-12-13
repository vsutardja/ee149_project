from __future__ import division
import re
import matplotlib.pyplot as plt
import numpy as np
from poly import *
from random import random
import socket
from time import sleep
from math import floor
from select import select
from transformations import euler_from_quaternion
from threading import Lock, Thread
from Queue import Queue
from sys import exit
import argparse

time_interval = 1.5
o_timeout = 0.001
x_scale = 200.0
y_scale = 280.0
direction = False

def update_quadrant(f, s_lock, d_lock):
    global direction
    try:
        while True:
            sleep(0.2)
            s_lock.acquire()
            status = select([s], [], [], o_timeout)[0]
            l = None
            if len(status) > 0:
                print 'reading angle data'
                angle_data = s.recv(1024)
                print 'angle data', angle_data
                angle_data = angle_data[-50:]
                if len(angle_data) > 1:
                    l = int(angle_data.split('\n')[-2])
            s_lock.release()
            if l is None:
                continue
            print 'l:', l
            l = l % 360
            d_lock.acquire()
            print 'netAngle', l
            if l > 90 and l < 270:
                direction = True
            else:
                direction = False
            d_lock.release()
    except Exception as e:
        print 'update_quadrant encountered exception:'
        print e
        print 'update_quadrant exiting'

def drive_kobuki(s, o_sock, rot, s_lock, d_lock):
    f = open('position_data', 'w')
    pattern = re.compile('(f [^g]+g)')
    try:
        for i, (curr_x, curr_y) in enumerate(rot):
            sleep(time_interval)
            status = select([o_sock], [], [], o_timeout)[0]
            if len(status) > 0:
                pos_data = o_sock.recv(4096)
                pos_data = pos_data[-100:]
                curr_data = None
                for curr_data in pattern.finditer(pos_data):
                    pass
                if not curr_data:
                    print 'no data from OptiTrack'
                    continue
                curr_data = curr_data.group()
                print 'curr_data:', curr_data
                vals = curr_data.rstrip('g\n').split(',')
                print 'vals:', vals
                try:
                    x, y = 1000*float(vals[1]), -1000*float(vals[3])
                    print 'actual position:', (x, y)
                    print 'next position:', (curr_x, curr_y)
                    qx, qy, qz, qw = map(float, vals[-4:])
                    d_lock.acquire()
                    local_dir = direction
                    d_lock.release()
                    yaw = get_yaw(qx, qy, qz, qw, local_dir)
                    print 'yaw', yaw*180/np.pi
                    radius, speed = get_roc((x, y), (curr_x, curr_y), yaw, f)
                    s_lock.acquire()
                    print 'sending', radius, speed
                    s.send('%d %d' % (radius, speed))
                    #s.send('1 20')
                    s_lock.release()
                    continue
                except Exception as e:
                    print e
                    s.send('0 0')
    except KeyboardInterrupt:
        print 'closing'
        s.shutdown(2)
        s.close()
        f.close()
        print 'closed'
        return
    print 'closing'
    s.shutdown(2)
    s.close()
    f.close()
    print 'closed'


class DummySocket():
    def __init__(self):
        pass
    def send(self, arg):
        print 'sending', arg
    def shutdown(self):
        pass
    def close(self):
        pass

def get_roc(p1, p2, orientation, f):
    x1, y1 = p1
    x2, y2 = p2
    dy = y2-y1
    dx = x2-x1
    dist = np.sqrt(dx**2 + dy**2)
    reference = (1, 0)
    angle = np.arccos((dx*reference[0] + dy*reference[1]) / dist)
    if dy < 0:
        angle = -angle
    if angle == orientation:
        return 0
    theta = angle - orientation
    theta = theta % (2*np.pi)
    if theta > np.pi:
        theta -= 2*np.pi
    radius = dist /(2*np.sin(theta))
    #internal_angle = np.pi/2 - theta
    center_angle = 2*theta
    #radius = dist*np.sin(internal_angle)/np.sin(center_angle)
    center_angle %= (2*np.pi)
    if center_angle > np.pi:
        center_angle -= 2*np.pi
    speed = int(abs(radius*center_angle) / time_interval)
    print 'get_roc:', 'p1', p1, 'p2', p2, 'orientation', orientation, 'angle', angle, 'theta', theta, 'radius', radius, 'speed', speed
    f.write('; '.join(map(str, [p1, p2, orientation, angle, theta, radius, speed])) + '\n')
    if speed > 300 or abs(theta) > np.pi*3/4:
        print 'setting speed to 0'
        speed = 0
    speed = min(speed / time_interval, 100)
    return radius, speed

def get_yaw(qx, qy, qz, qw, x_neg):
    print map((lambda i: i*180/np.pi), euler_from_quaternion((qw, qx, qy, qz)))
    #psi = np.arctan2(2*(qx*qw+qy*qz), 1-2*(qz**2+qw**2))
    #print 'psi', psi * 180/np.pi
    theta = np.arcsin(-2*(qx*qz-qw*qy))
    if x_neg:
        theta = np.pi - theta
    theta = theta % (2*np.pi)
    return theta

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

# n + K - 2 nonzero functions, from i = 0 to N + K - 3
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='interpolation and control.')
    parser.add_argument('-k', '--kobuki_ip', type=str, default='192.168.2.9')
    parser.add_argument('-o', '--opti_ip', type=str, required=True)
    parser.add_argument('-s', '--scale', type=float, default=5)
    parser.add_argument('-d', '--dummy', dest='dummy', action='store_true')
    args = parser.parse_args()

    s_lock = Lock()
    d_lock = Lock()

    O_HOST = args.opti_ip
    K_HOST = args.kobuki_ip
    scale = args.scale

    K = 4
    def t(i):
        if i < K:
            return 0
        elif i >= n+K-1:
            return n-1
        else:
            return i-K+1

    np.set_printoptions(suppress=True)
    #with open('data_file') as data_file:
        #x = eval(data_file.readline())
        #y = eval(data_file.readline())
    x = []
    y = []
    for i in range(10):
        x.append(np.cos(i*np.pi/4))
        y.append(np.sin(i*np.pi/4))
    #x = [50, 100, 200, 200, 100, 50, 100, 100]
    #y = [100, 100, 100, 200, 200, 200, 250, 300]
    x = map((lambda i: i-x[0]), x)
    y = map((lambda i: i-y[0]), y)
    x_ratio = max(abs(max(x)) / x_scale, abs(min(x)) / x_scale)
    y_ratio = (max(y) - min(y)) / y_scale
    ratio = max(x_ratio, y_ratio)
    x = map((lambda i: i/ratio), x)
    y = map((lambda i: i/ratio), y)
    print 'x:', x
    print 'y:', y
    n = len(x)

    cont = control_points(zip(x, y))
    print 'control_points:', cont
    cont_x = [i for i,j in cont]
    cont_y = [j for i,j in cont]
    plt.hold(True)
    #plt.scatter(x, y)
    #plt.scatter(cont_x, cont_y, color='red')

    px, py = interpolate(cont)
    t = np.linspace(0, n-1, 5*n)
    #flipped because rotated 90 degrees counterclockwise
    #y_vals = [px(i) for i in t]
    #x_vals = [-py(i) for i in t]
    y_vals = [-px(i) for i in t]
    x_vals = [py(i) for i in t]
    #dy = y[1] - y[0]
    #dx = x[1] - x[0]
    #if dx == 0:
        #offset = 0
    #else:
        #offset = np.arctan(float(dy)/dx)
    #print zip(x_vals, y_vals)
    #print 'bad:', x_vals[27], y_vals[27]
    #x_vals, y_vals = y_vals, map((lambda i: -i), x_vals)
    #rot = map((lambda pos: rotate(pos[0], pos[1], offset)), zip(x_vals, y_vals))
    rot = map((lambda p: (p[0] * scale, p[1] * scale)), zip(x_vals, y_vals))
    #print rot
    #print rot
    #print [x for x, y in rot]
    plt.plot([x for x, y in rot], [y for x, y in rot])
    #plt.plot(x_vals, y_vals)
    plt.show()

    r, speeds = roc(x_vals, y_vals)


    for i in range(len(r)):
        r[i] *= 10
        r[i] = int(floor(r[i]))
        if abs(r[i]) > 32000:
            r[i] = 0
        speeds[i] *= 10
        speeds[i] = abs(floor(speeds[i]))
    speeds = map(int, speeds)
    speeds = map((lambda x: x if x < 200 else 200), speeds)
    r = high_pass(r)
    speeds = high_pass(speeds)

    print 'speeds:', speeds
    print 'r:', r

    K_PORT = 1234
    if args.dummy:
        s = DummySocket()
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print 'connecting to Kobuki'
        s.connect((K_HOST, K_PORT))
        print 'connected to Kobuki'
        s.send('0 0')
    #s = DummySocket()

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
    t1 = Thread(target=update_quadrant, args=(s.makefile(), s_lock, d_lock))
    t1.start()
    drive_kobuki(s, o_sock, rot, s_lock, d_lock)
    t1.join()
