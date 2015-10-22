#!/usr/bin/python

# Polls fifo pipe and prints results
import os

PIPE_NAME = 'pipe'
f = os.open(PIPE_NAME, os.O_NONBLOCK)
while True:
    try:
        s = os.read(f, 100)
    except:
        s = ''
    if len(s) == 1:
        break
    if s:
        print tuple(map(int, s.rstrip('\n').split('\n')[-1].split(' ')))
os.close(f)
