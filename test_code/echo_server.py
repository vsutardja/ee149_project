#!/usr/bin/python

# Gets input over IP socket and relays it into a fifo pipe

import socket
import select
from time import sleep
PIPE_NAME = 'pipe'
 
HOST = '127.0.0.1'       # Hostname to bind
PORT = 12345              # Open non-privileged port 8888
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', PORT))
s.listen(1)
conn, addr = s.accept()
print 'Connected by', addr
try:
    while 1:
        data = conn.recv(1024)
        if data:
            f = open(PIPE_NAME, 'w+')
            f.write(data + '\n')
            f.close()
            print 'written', data
        conn.send('ack')
except:
    f = open(PIPE_NAME, 'w+')
    f.write(' ')
    f.close()
conn.close()
