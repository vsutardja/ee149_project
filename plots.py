import matplotlib.pyplot as plt

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
        print p1, p2, vals[2:]
    plt.plot(x_vals, y_vals)
    plt.plot(x_vals2, y_vals2, color='red')
    plt.show()

