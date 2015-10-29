# issue instructions to kobuki

import socket
from time import sleep
from random import randint
 
HOST = '192.168.2.9'
PORT = 1234
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
try:
    while True:
        sleep(4.5)
        x = randint(1, 200)
        y = randint(1, 200)
        print 'sending', x, y
        s.send('%d %d' % (x, y))
except KeyboardInterrupt:
    print 'closing'
    s.shutdown(2)
    s.close()
    print 'closed'

