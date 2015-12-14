from spline import get_roc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib import rc
#rc('text', usetex=True)
rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})


p1 = (50, 100)
p2 = (75, 90)
orientation = np.pi/8

radius, speed = get_roc(p1, p2, orientation)
print radius, speed

orient_vector = np.array((np.cos(orientation), np.sin(orientation)))
print 'orient_vector', orient_vector
radius_vector = np.array([-orient_vector[1], orient_vector[0]])
radius_vector *= radius
p1_vector = np.array(p1)
print 'radius_vector', radius_vector
circle_center = radius_vector + p1_vector
print 'circle_center', circle_center
plt.hold(True)
plt.scatter([p1[0], p2[0]], [p1[1], p2[1]])
plt.scatter(circle_center[0], circle_center[1], color='red')
t2 = (orientation + np.pi/2) * 180/np.pi
t1 = np.arctan((p2[1]-circle_center[1])/(p2[0]-circle_center[0])) * 180/np.pi
arc = matplotlib.patches.Arc(circle_center, 2*abs(radius), 2*abs(radius), theta1=t1, theta2=t2, ls='dashed')
plt.axes().add_patch(arc)
plt.arrow(p1[0], p1[1], speed/2 * orient_vector[0], speed/2 * orient_vector[1], width=0.01, color='red', head_width=0.5, head_length=0.5)
plt.text(50, 103, 'orientation')
plt.text(50, 98, 'current position')
plt.text(73, 89, 'next position')
plt.text(65, 101, 'planned path')
plt.gca().set_aspect('equal', adjustable='box')
#plt.show()
plt.savefig('plots/roc.png', dpi=600)
