#!/usr/bin/python

# Gets numbers and passes them over socket to server

import socket
from time import sleep
from random import randint
 
HOST = '127.0.0.1'      # Set the remote host, for testing it is localhost
PORT = 12345            # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
try:
    while True:
        sleep(1)
        x = randint(1, 300)
        y = randint(1, 300)
        s.send('%d %d' % (x, y))
        print 'sent', x, y
except KeyboardInterrupt:
    print 'closing'
    s.shutdown(2)
    s.close()
    print 'closed'
