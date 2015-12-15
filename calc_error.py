import numpy as np

def dist(x1, y1, x2, y2):
    return np.sqrt((x2-x1)**2 + (y2-y1)**2)

def point_line_dist(x1, y1, x2, y2, x0, y0):
    return np.abs((y2-y1)*x0 - (x2-x1)*y0 + x2*y1 - y2*x1)/dist(x1, y1, x2, y2)

with open('position_data') as pos_file:
    lines = pos_file.readlines()
    x_vals = []
    y_vals = []
    x_vals2 = []
    y_vals2 = []
    for i, line in enumerate(lines[:]):
        vals = line.split(';')
        p1 = eval(vals[0])
        p2 = eval(vals[1])
        x_vals.append(p1[0])
        y_vals.append(p1[1])
        x_vals2.append(p2[0])
        y_vals2.append(p2[1])
        #print p1, p2, vals[2:]
    #print 'last point:', x_vals[-1], y_vals[-1]
    #print 'third to last actual', x_vals2[-3], y_vals2[-3]
    #print x_vals[:5]
    #print x_vals2[:5]
    #print y_vals[:5]
    #print y_vals2[:5]

errors = []
n = len(x_vals2)
for i, (x,y) in enumerate(zip(x_vals, y_vals)):
    start = max(0, i-10)
    distances = map((lambda (x2,y2): dist(x, y, x2, y2)), zip(x_vals2, y_vals2)[start:i+1])
    dist_closest = np.argmin(distances)
    closest = start + dist_closest
    print i, closest, (x, y), (x_vals2[closest], y_vals2[closest]), distances[dist_closest]
    error = distances[dist_closest]
    left_error, right_error = None, None
    best_error = error
    if closest > 0:
        left_error = point_line_dist(x_vals2[closest], y_vals2[closest], x_vals2[closest-1], y_vals2[closest-1], x, y)
        if left_error < best_error:
            best_error = left_error
    if closest < n-1:
        right_error = point_line_dist(x_vals2[closest], y_vals2[closest], x_vals2[closest+1], y_vals2[closest+1], x, y)
        if right_error < best_error:
            best_error = right_error
    #print 'errors', error, left_error, right_error
    print 'error', best_error
    #print 'points', (x_vals2[closest-1], y_vals2[closest-1]) if left_error else None, (x_vals2[closest], y_vals2[closest]), (x_vals2[closest+1], y_vals2[closest+1]) if right_error else None
    errors.append(best_error)
errors = np.array(errors[4:])
errors_sq = np.power(errors, 2)
print 'RMS error:', np.sqrt(np.sum(errors_sq)/len(errors_sq))
