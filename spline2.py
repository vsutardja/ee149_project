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

def wheel_speed(r, v=1, b=230):
    spd = np.copy(r)
    for i in range(len(spd)):
        if spd[i] > 0:
            spd[i] = v * (spd[i] + b / 2) / spd[i]
        elif spd[i] < 0:
            spd[i] = v * (spd[i] - b / 2) / spd[i]
    return spd


    #try:
        #for i, (radius, speed) in enumerate(zip(r, speeds)):
            #sleep(time_interval)
            #status = select([o_sock], [], [], o_timeout)[0]
            #if len(status) > 0:
                #pos_data = o_sock.recv(4096)
                #pos_data = pos_data[-100:]
                #curr_data = pos_data.split('f ')[-1]
                #vals = curr_data.split(',')
                #try:
                    #x, y = 1000*float(vals[1]), -1000*float(vals[3])
                    #print 'vals:', vals
                    #print 'perceived position:', rot[i]
                    #print 'actual position:', (x, y)
                    #s.send('%d %d' % (radius, speed))
                #except Exception as e:
                    #print e
            #print 'sending', int(radius), int(speed)
            #if i % 10 == 0:
                #print 'At data point', int(i/10), 'of', n
            #s.send('%d %d' % (radius, speed))
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

def random_points(n, x=8, y=8):
    return [(random()*x, random()*y) for _ in range(n)]

def high_pass(sig, mult=0.1):
    new_sig = [(1 + mult)*sig[0]]
    for i in range(1, len(sig)):
        new_sig.append(sig[i] + mult*(sig[i] - sig[i-1]))
    assert len(new_sig) == len(sig)
    return new_sig

def rotate(x, y, offset):
    if x == 0 and y == 0:
        return 0, 0
    r, theta = to_polar(x, y)
    theta -= offset
    x, y = to_rect(r, theta)
    return x, y

def to_polar(x, y):
    r = np.sqrt(x**2 + y**2)
    theta = np.arctan(float(y)/x)
    return r, theta

def to_rect(r, theta):
    x = r*np.cos(theta)
    y = r*np.sin(theta)
    return x, y

