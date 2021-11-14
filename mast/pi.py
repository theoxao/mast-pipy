import time

import RPi.GPIO as g
from time import sleep

g.setmode(g.BCM)

g.setup(2, g.OUT, initial= g.LOW)
g.setup(3, g.OUT, initial= g.LOW)
g.setup(4, g.OUT, initial= g.LOW)
g.setup(17,g.OUT, initial = g.LOW)


def move(value):
    g.output(2, value)
    g.output(3, False)
    g.output(3, True)


def commit():
    g.output(4, True)
    g.output(4, False)


def update_state(position, value):
    high = position*2 + int(value)
    print(high)
    g.output(17, True)
    for i in range(high-1):
        move(False)
        commit()
    move(True)
    commit()
    for i in range(32-high):
        move(False)
        commit()
    time.sleep(1)
    g.output(17, False)
    time.sleep(1)
    g.output(17, True)
    for i in range(32):
        move(False)
        commit()
    g.output(17, False)
        
    
