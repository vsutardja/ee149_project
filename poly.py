from __future__ import division
from sys import maxint
import numpy as np
import matplotlib.pyplot as plt

class Polynomial:
    def __init__(self, coeffs):
        self.coeffs = list(coeffs)
        while self.coeffs[-1] == 0 and len(self.coeffs) > 1:
            del self.coeffs[-1]
        self.n = len(self.coeffs) - 1

    def __getitem__(self, i):
        if i < 0:
            raise ValueError('Negative index ' + str(i))
        elif i <= self.n:
            return self.coeffs[i]
        else:
            return 0
        
    def __mul__(self, other):
        if type(other) != type(self):
            return Polynomial(map((lambda c : c*other), self.coeffs))
        new_coeffs = []
        new_degree = self.n + other.n
        for i in range(new_degree+1):
            s = 0
            for j in range(i+1):
                s += self[j] * other[i-j]
            new_coeffs.append(s)
        return Polynomial(new_coeffs)

    def __add__(self, other):
        new_degree = max(self.n, other.n)
        new_coeffs = []
        for i in range(new_degree + 1):
            new_coeffs.append(self[i] + other[i])
        return Polynomial(new_coeffs)

    def __str__(self):
        return ' + '.join('%.2ft^%d' % (c, i) for i,c in enumerate(self.coeffs)).replace('t^0', '').replace('t^1', 't')

    def __repr__(self):
        return 'Polynomial(' + repr(self.coeffs) + ')'

    def __eq__(self, other):
        if len(self.coeffs) != len(other.coeffs):
            return False
        for c1, c2 in zip(self.coeffs, other.coeffs):
            if c1 != c2:
                return False
        return True

    def __call__(self, t):
        return sum(c * t**i for i, c in enumerate(self.coeffs))

    def __truediv__(self, k):
        return Polynomial([c / k for c in self.coeffs])

class PiecewisePolynomial:
    def __init__(self, func=None):
        self.intervals = [-maxint, maxint]
        if func is None:
            self.funcs = [Polynomial([0])]
        else:
            self.funcs = [func]

    def cleanup(self):
        i = 0
        while i < len(self.intervals) - 1:
            if self.intervals[i] == self.intervals[i+1]:
                del self.intervals[i+1]
                del self.funcs[i]
            else:
                i += 1
        i = 0
        while i < len(self.funcs) - 1:
            if self.funcs[i] == self.funcs[i+1]:
                del self.funcs[i]
                del self.intervals[i+1]
            else:
                i += 1

    def setp(self, func, start, end):
        #print 'setp', func, start, end
        if start == None and end == None:
            self.intervals = [-maxint, maxint]
            self.funcs = [func]
            return
        new_intervals = []
        new_funcs = []
        for i, val in enumerate(self.intervals):
            if start > val:
                new_intervals.append(val)
                new_funcs.append(self.funcs[i])
            else:
                new_intervals.append(start)
                new_funcs.append(func)
                new_intervals.append(end)
                for j, nval in enumerate(self.intervals[i:]):
                    if nval == end:
                        new_intervals += self.intervals[i+j+1:]
                        new_funcs += self.funcs[i+j:]
                        self.intervals = new_intervals
                        self.funcs = new_funcs
                        return
                    elif nval > end:
                        new_intervals += self.intervals[i+j:]
                        new_funcs += self.funcs[i+j-1:]
                        self.intervals = new_intervals
                        self.funcs = new_funcs
                        return

    def __add__(self, other):
        if type(other) != PiecewisePolynomial:
            pass
        return self.merge(other, Polynomial.__add__)

    def __mul__(self, other):
        if type(other) != type(self):
            new_funcs = map((lambda func : func * other), self.funcs)
            p = PiecewisePolynomial()
            p.intervals = list(self.intervals)
            p.funcs = new_funcs
            return p
        return self.merge(other, Polynomial.__mul__)

    def merge(self, other, op):
        i = 1
        j = 1
        new_intervals = [-maxint]
        new_funcs = [self.funcs[0] * other.funcs[0]]
        while i < len(self.intervals) - 1 and j < len(other.intervals) - 1:
            if self.intervals[i] < other.intervals[j]:
                new_intervals.append(self.intervals[i])
                new_funcs.append(op(self.funcs[i], other.funcs[j-1]))
                i += 1
            elif self.intervals[i] > other.intervals[j]:
                new_intervals.append(other.intervals[j])
                new_funcs.append(op(self.funcs[i-1], other.funcs[j]))
                j += 1
            else:
                new_intervals.append(self.intervals[i])
                new_funcs.append(op(self.funcs[i], other.funcs[j]))
                i += 1
                j += 1
        while i < len(self.intervals) - 1:
            new_intervals.append(self.intervals[i])
            new_funcs.append(op(self.funcs[i], other.funcs[j-1]))
            i += 1
        while j < len(other.intervals) - 1:
            new_intervals.append(other.intervals[j])
            new_funcs.append(op(self.funcs[i-1], other.funcs[j]))
            j += 1
        new_intervals.append(maxint)
        p = PiecewisePolynomial()
        p.intervals = new_intervals
        p.funcs = new_funcs
        p.cleanup()
        return p

    def __call__(self, t):
        i = 1
        while self.intervals[i] <= t:
            i += 1
        return self.funcs[i-1](t)

    def __str__(self):
        s = ''
        for i, (t, f) in enumerate(zip(self.intervals[:-1], self.funcs)):
            t2 = self.intervals[i+1]
            trep = str(t) if t > -maxint else '-inf'
            t2rep = str(t2) if t2 < maxint else 'inf'
            s += '[%s, %s): %s; ' % (trep, t2rep, str(f))
        return '(' + s[1:-2]

    def plot(self, s, e):
        r = e-s
        t = np.linspace(s, e, 100)
        y = [self(i) for i in t]
        plt.plot(t, y)
        plt.show()

if __name__ == '__main__':
    p = Polynomial([1, 2, 0])
    q = Polynomial([2, 1])
    w = PiecewisePolynomial()
    v = PiecewisePolynomial(q)
    w.setp(p, 1, 2)
    w.setp(q, 2, 3)
    print 'p', p
    print 'q', q
    print 'w', w
    print 'v', v
    print 'w*v', w * v
    print (w*v)(1)
